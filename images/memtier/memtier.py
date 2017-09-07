import sys, os
import subprocess
import itertools
import threading

def gen_calls(call):
    for id in itertools.count(0):
        yield call + ["--client-stats", str(id)]

def work(call):
    id = call[-1] + "-"
    n = len(id)
    for root, dirs, files in os.walk('.'):
        for name in files:
            if name[:n] == id:
                path = os.path.join(root, name)
                # TODO: parse content of path and push to influxdb
                print(path)
                os.remove(path)

spawn_worker = work # debug

def main():
    bin = "memtier_benchmark"
    cmd = []
    if len(sys.argv) > 1:
        cmd = sys.argv[1:]
    if "--client-stats" in cmd:
        print('Do not use --client-stats!')
        return

    for call in gen_calls([bin]+cmd):
        subprocess.check_call(call)
        spawn_worker(call)

if __name__ == "__main__":
    main()
