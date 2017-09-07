import docker
import threading
import optparse
import pymongo
import sys
import influxdb

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

def loop(clt, callbacks, Id, buffering):
    stats = []
    if not clt.inspect_container(Id)['State']['Running']: return
    for stat in clt.stats(Id, decode=True):
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
