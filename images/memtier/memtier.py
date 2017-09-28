import sys, os
import subprocess
import itertools
import threading

def gen_calls(call):
    for id in itertools.count(0):
        yield call + ["--client-stats", str(id)]

def work(call):
    loop_id = call[-1] + "-"
    len_loop_id = len(loop_id)
    for root, dirs, files in os.walk('.'):
        for name in files:
            if name[:len_loop_id] == loop_id:
                path = os.path.join(root, name)
                loop_id, run_id, cg_id, prefix, client_id = os.path.splitext(name)[0].split('-')
                # TODO: parse content of path and push to influxdb
                print(loop_id, run_id, cg_id, prefix, client_id)
                with open(path) as f:
                    contents = f.read()
                    for content in contents.split('\n\n'):
                        lines = content.split('\n')
                        title = lines[0]
                        header = [e for e in lines[1].split(',')]
                        n = len(header)
                        for line in lines[2:]:
                            line = [e for e in line.split(',')]
                            if len(line) != n: continue
                            fields = {
                                header[i] : line[i]
                                for i in range(n)
                            }
                            print(fields)
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
