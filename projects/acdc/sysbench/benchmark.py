import subprocess
import time
import argparse
import parse
import influxdb
import datetime

main_parser = argparse.ArgumentParser()
# TODO
user = 'root'
host = 'mysql'
dbname = 'dbname'
#duration = 5*60
main_subparsers = main_parser.add_subparsers()

sysbench_bin_path = './sysbench/sysbench'
sysbench_lua_path = './sysbench/tests/db/oltp.lua'

mysql_call = ['mysql',
              '--host', host,
              '-u', user]

def sysbench_call(dbsize):
    return [sysbench_bin_path,
            '--test=%s' % sysbench_lua_path,
            '--oltp-table-size=%d' % dbsize,
            '--mysql-db=%s' % dbname,
            '--mysql-host=%s' % host,
            '--mysql-user=root',
            '--mysql-password=']

sysbench_expected_v05_intermediate_output = """[{}] timestamp: {timestamp}, threads: {threads}, tps: {trps}, reads: {rdps}, writes: {wrps}, response time: {rtps}ms ({}%), errors: {errps}, reconnects:  {recops}"""
sysbenchoutput_parser = parse.compile(sysbench_expected_v05_intermediate_output)

def wait_for_server_to_start():
    while True:
        try:
            subprocess.check_call(mysql_call + ['-e', 'show status'])
            break
        except Exception as e:
            print(e)
        print('Waiting for %s to start' % (host))
        time.sleep(10)
        
def prepare(args):
    try:
        subprocess.check_call(mysql_call + ['-e', 'CREATE DATABASE %s' % dbname])
        subprocess.check_call(sysbench_call(args.dbsize) + ['prepare'])
    except Exception as e:
        print(e)
    finally:
        out = subprocess.check_output(mysql_call + ['-D', dbname, '-e', 'select count(*) from sbtest1'])
        count = int(out.split('\n')[1])
        if count != args.dbsize:
            raise Exception('count != dbsize')
        subprocess.check_call(mysql_call + ['-e', 'shutdown'])

def run(args):
    def foo(x): print(x)
    args.callback = influx

    client = influxdb.InfluxDBClient(host='influxdb',
                                     database='perf')
    client.create_database('perf')
    def callback(res):
        client.write_points([p for p in influx(res)])
    args.callback = callback

    call = sysbench_call(args.dbsize) + ['--report-interval=1',
                            '--tx-rate=%d' % 0,
                            '--max-requests=0',
                            '--max-time=%d' % args.duration,
                            '--num-threads=%d' % 8,
                            '--oltp-read-only=on',
                            'run']
    p = subprocess.Popen(call, stdout=subprocess.PIPE)
    for line in p.stdout:
        res = sysbenchoutput_parser.search(line)
        if res == None:
            print(line)
        else:
            args.callback(dict(res.named))

def dummy(*args,**kwargs):
    pass

def influx(fields, tags={}):
    t = datetime.datetime.utcfromtimestamp(int(fields['timestamp']))
    del fields['timestamp']
    point = {
        "measurement": "sysbench",
        "tags": tags,
        "time": t,
        "fields": fields,
    }
    yield point

def main():
    prepare_parser = main_subparsers.add_parser('prepare')
    prepare_parser.add_argument('--dbsize',   dest="dbsize", type=int, nargs='?', default=10000)
    prepare_parser.set_defaults(func=prepare)
    run_parser = main_subparsers.add_parser('run')
    run_parser.add_argument('--dbsize',   dest="dbsize", type=int, nargs='?', default=10000)
    run_parser.add_argument('--duration', dest="duration", type=int, nargs='?', default=60)
    run_parser.set_defaults(func=run)
    run_parser.set_defaults(callback=dummy)

    args = main_parser.parse_args()
    
    wait_for_server_to_start()
    args.func(args)

main()
