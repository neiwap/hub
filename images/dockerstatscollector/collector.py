import docker
import threading
import optparse
import pymongo
import sys
import influxdb
import datetime
import time

def fields(myk, myv):
    if type(myv) == dict:
        for k in myv:
            for k, v in fields(myk+[k], myv[k]):
                yield k, v
    elif type(myv) == list:
        for i in range(len(myv)):
            for k, v in fields(myk+[i], myv[i]):
                yield k, v
    else:
        yield (myk, myv)

def influx_format(stat, tags={}):
    # TODO: cpu usage %, pg{in,out}/s, blkio byte/s
    time = stat['read']
    tags['name'] = stat['name']
    tags['id'] = stat['id']
    for measurement in ['memory_stats', 'blkio_stats', 'networks', 'cpu_stats']:
        if measurement not in stat: continue
        point = {
            "measurement": measurement,
            "tags": tags,
            "time": time,
            "fields": {
                '.'.join([str(e) for e in k]) : v
                for k,v in fields([], stat[measurement])
            },
        }
        yield point

class CPU_PERCENT_USAGE:
    def __init__(self):
        self.system_cpu_usage_old = None
        self.total_usage_old = None
    def update(self, stat):
        if 'cpu_stats' not in stat:
            return stat
        try:
            system_cpu_usage_new = stat['cpu_stats']['system_cpu_usage']
            total_usage_new = stat['cpu_stats']['cpu_usage']['total_usage']
            if (self.system_cpu_usage_old != None and
                self.total_usage_old != None):
                dx = system_cpu_usage_new - self.system_cpu_usage_old
                dy = total_usage_new - self.total_usage_old
                if dy >= 0 and dx >0:
                    ncpu = len(stat['cpu_stats']['cpu_usage']['percpu_usage'])
                    stat['cpu_stats']['percent_usage'] = 100 * ncpu * dy / dx
            self.system_cpu_usage_old = system_cpu_usage_new
            self.total_usage_old = total_usage_new
        except Exception as e:
            print(e)
        return stat

class IO_USAGE:
    def __init__(self):
        self.bytes_r_old = None
        self.bytes_w_old = None
        self.time_old = None
    def update(self, stat):
        if 'blkio_stats' not in stat:
            return stat
        try:
            time_new = stat['read']
            time_new = datetime.datetime.strptime(time_new[:-4], "%Y-%m-%dT%H:%M:%S.%f")
            time_new = float(time.mktime(time_new.timetuple()))
            bytes_r_new = 0.0
            bytes_w_new = 0.0
            for data in stat['blkio_stats']['io_service_bytes_recursive']:
                if data['op'] == 'Write':
                    bytes_w_new += data['value']
                if data['op'] == 'Read':
                    bytes_r_new += data['value']
            if (self.bytes_r_old != None and
                self.bytes_w_old != None and
                self.time_old != None):
                dr = bytes_r_new - self.bytes_r_old
                dw = bytes_w_new - self.bytes_w_old
                dt = time_new - self.time_old
                if dt > 0 and dr >=0 and dw >= 0:
                    stat['blkio_stats']['Rbps'] = dr/dt
                    stat['blkio_stats']['Wbps'] = dw/dt
            self.bytes_r_old = bytes_r_new
            self.bytes_w_old = bytes_w_new
            self.time_old = time_new
        except Exception as e:
            print(e)
        return stat

def statsonthefly(stats):
    cpu = CPU_PERCENT_USAGE()
    io = IO_USAGE()
    for stat in stats:
        stat = cpu.update(stat)
        stat = io.update(stat)
        yield stat

def loop(clt, callbacks, Id, buffering):
    stats = []
    if not clt.inspect_container(Id)['State']['Running']: return
    for stat in statsonthefly(clt.stats(Id, decode=True)):
        stats.append(stat)
        if len(stats) < buffering: continue
        info = clt.inspect_container(Id)
        if not info['State']['Running']: return
        for call in callbacks:
            try:
                call(stats, info)
            except Exception as e:
                print(e)
        stats = []

def main():
    parser = optparse.OptionParser()
    parser.add_option('--buffering', dest="buffering", type=int, nargs=1, default=10)
    parser.add_option("--print", dest="print", default=False, action="store_true")
    parser.add_option("--mongo", dest="mongo", default=False, action="store_true")
    parser.add_option('--mongodbname', dest="mongodbname", type=str, nargs=1, default='prod')
    parser.add_option('--mongocollection', dest="mongocollection", type=str, nargs=1, default='dockerstats')
    parser.add_option("--influx", dest="influx", default=False, action="store_true")
    parser.add_option("--influxdbname", dest="influxdbname", type=str, nargs=1, default='dockerstats')
    parser.add_option("--influxdbhost", dest="influxdbhost", type=str, nargs=1, default='localhost')
    parser.add_option("--influxdbport", dest="influxdbport", type=str, nargs=1, default='8086')
    (options, args) = parser.parse_args()
    filterout = lambda clt, Id : False # TODO
    clt = docker.APIClient()
    callbacks = []
    if options.print:
        # TODO: lock
        # TODO: pretty print
        callbacks.append(lambda stats, info : print(stats,info))

    if options.mongo:
        def mongo(stats, info):
            with pymongo.MongoClient() as client:
                client[options.mongodbname][options.mongocollection].insert_many(stats)
        callbacks.append(mongo)

    if options.influx:
        client = influxdb.InfluxDBClient(host=options.influxdbhost,
                                port=int(options.influxdbport),
                                database=options.influxdbname)
        client.create_database(options.influxdbname)
        def influx(stats, info):
            points = [point for stat in stats for point in influx_format(stat,info["Config"]["Labels"])]
            client.write_points(points)
        callbacks.append(influx)

    def spawn_worker(Id):
        t = threading.Thread(target=loop, args=(clt, callbacks, Id, options.buffering))
        t.daemon = True
        t.start()

    for container in clt.containers():
        Id = container['Id']
        if filterout(clt, Id): continue
        # loop(clt, callbacks, Id, options.buffering) #debug
        spawn_worker(Id)

    for event in clt.events(decode=True):
        print(event)
        if 'status' not in event: continue
        status = event['status']
        if status == 'start':
            Id = event['id']
            if filterout(clt, Id): continue
            spawn_worker(Id)

if __name__ == "__main__":
    main()
