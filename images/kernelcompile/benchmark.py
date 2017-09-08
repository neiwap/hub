import docker
import threading
import optparse
import sys
import influxdb
import os
import time
import subprocess
import json

def prepare(callback=lambda x : x, tags={}):
    form = '{ "real" : %e, "user" : %U, "sys" : %S }'
    call = ['/usr/bin/time', '--format', form, 'bash', '-c', 'make -C linux allmodconfig > /dev/null 2>&1']
    start = time.time()
    output = subprocess.check_output(call, stderr=subprocess.STDOUT)
    fields = json.loads(output)
    points = [{
        'measurement' : 'prepare',
        'tags' : tags,
        'time' : int(start),
        'fields' : fields,
    }]
    callback(points)

def run(jobs, callback=lambda x : x, tags={}):
    form = '{ "real" : %e, "user" : %U, "sys" : %S }'
    call = ['/usr/bin/time', '--format', form, 'bash', '-c',
            'make -C linux -j {} > /dev/null 2>&1'.format(jobs)]
    start = time.time()
    output = subprocess.check_output(call, stderr=subprocess.STDOUT)
    fields = json.loads(output)
    points = [{
        'measurement' : 'run',
        'tags' : tags,
        'time' : int(start),
        'fields' : fields,
    }]
    callback(points)

def clean(callback=lambda x : x, tags={}):
    form = '{ "real" : %e, "user" : %U, "sys" : %S }'
    call = ['/usr/bin/time', '--format', form, 'bash', '-c',
            'make -C linux clean > /dev/null 2>&1']
    start = time.time()
    output = subprocess.check_output(call, stderr=subprocess.STDOUT)
    fields = json.loads(output)
    points = [{
        'measurement' : 'clean',
        'tags' : tags,
        'time' : int(start),
        'fields' : fields,
    }]
    callback(points)

def main():
    parser = optparse.OptionParser()
    parser.add_option("--stdout", dest="stdout", default=False, action="store_true")
    parser.add_option("--influx", dest="influx", default=False, action="store_true")
    parser.add_option("--influxdbname", dest="influxdbname", type=str, nargs=1, default='kernelcompile')
    parser.add_option("--influxdbhost", dest="influxdbhost", type=str, nargs=1, default='localhost')
    parser.add_option("--influxdbport", dest="influxdbport", type=str, nargs=1, default='8086')
    (options, args) = parser.parse_args()
    clt = docker.APIClient()
    HOSTNAME = os.environ['HOSTNAME']
    info = clt.inspect_container(HOSTNAME)
    tags = info["Config"]["Labels"]
    tags['name'] = info["Name"]
    tags['id'] = info['Id']
    
    callbacks = []

    if options.stdout:
        def stdout(x):
            print(x)
        callbacks.append(stdout)

    if options.influx:
        client = influxdb.InfluxDBClient(host=options.influxdbhost,
                                port=int(options.influxdbport),
                                database=options.influxdbname)
        client.create_database(options.influxdbname)
        def influx(points):
            print(points)
            client.write_points(points)
        callbacks.append(influx)
    
    def callback(x):
        for call in callbacks:
            try:
                call(x)
            except Exception as e:
                print(e)
    
    i = 0
    while i < len(args):
        if args[i] == 'prepare':
            tags['stage'] = 'prepare'
            prepare(callback, tags)
        elif args[i] == 'run':
            tags['stage'] = 'run'
            i += 1
            jobs = args[i]
            run(jobs, callback, tags)
        elif args[i] == 'clean':
            tags['stage'] = 'clean'
            clean(callback, tags)
        elif args[i] == 'sleep':
            i += 1
            sleep = args[i]
            time.sleep(int(sleep))
        i+=1

if __name__ == "__main__":
    main()
