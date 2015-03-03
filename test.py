#coding:utf8
import multiprocessing
import time
 
def func(msg):
    for i in xrange(3):
        print msg+str(i)
        time.sleep(2)
 
if __name__ == "__main__":
    p = multiprocessing.Process(target=func, args=("hello", ))
    p.start()
    #p.join()#阻塞当前进程
    print "Sub-process done."
    time.sleep(3)
    #p.terminate()