import subprocess
import time
import psutil


def kill(popen):
    popen.terminate()
    pid=popen.pid
    try:
        process = psutil.Process(pid)
    except:
        print "error"
        return
    for proc in process.get_children(recursive=True):
        proc.kill()
    process.kill()

command="python ./runner.py"
proc = subprocess.Popen(command, shell=True, stderr=subprocess.PIPE)

print proc.poll()
time.sleep(5)
print proc.poll()
process = psutil.Process(proc.pid)
print process.status()
kill(proc)
print proc.poll()
try:
    process = psutil.Process(proc.pid)
    process.status()
except:
    print 'stop'
    pass