import subprocess
import time

user = 'root'
host = 'mysql'
dbname = 'dbname'
dbsize = 1000

sysbench_bin_path = './sysbench/sysbench'
sysbench_lua_path = './sysbench/tests/db/oltp.lua'

mysql_call = ['mysql',
              '--host', host,
              '-u', user]

sysbench_call = [sysbench_bin_path,
                 '--test=%s' % sysbench_lua_path,
                 '--oltp-table-size=%d' % dbsize,
                 '--mysql-db=%s' % dbname,
                 '--mysql-host=%s' % host,
                 '--mysql-user=root',
                 '--mysql-password=']

def wait_for_server_to_start():
    while True:
        try:
            subprocess.check_call(mysql_call + ['-e', 'show status'])
            break
        except Exception as e:
            print(e)
        print('Waiting for %s to start' % (host))
        time.sleep(10)
        
def prepare():
    subprocess.check_call(mysql_call + ['-e', 'CREATE DATABASE %s' % dbname])
    subprocess.check_call(sysbench_call + ['prepare'])

wait_for_server_to_start()
prepare()
