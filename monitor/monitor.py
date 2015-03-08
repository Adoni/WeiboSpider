import web
import subprocess
import multiprocessing
import time
import psutil

urls=(
    '/','index',
    '/add', 'add',
    '/add_a_batch', 'add_a_batch',
    '/restart', 'restart',
    '/stop', 'stop',
    '/restart_all', 'restart_all',
    '/stop_all', 'stop_all',
    '/set_restart_auto','set_restart_auto',
    '/stop_restart_auto','stop_restart_auto',
    )
app = web.application(urls, globals())
render = web.template.render('templates/')
crawlers=[]

def kill(popen):
    popen.terminate()
    pid=popen.pid
    try:
        process = psutil.Process(pid)
    except Exception as e:
        print e
        print "error"
        return
    for proc in process.get_children(recursive=True):
        proc.kill()
    process.kill()

def restart_all_crawlers():
    for i in range(0,len(crawlers)):
        try:
            kill(crawlers[i])
        except:
            pass
        order='python crawler.py '+str(i+1)
        print order
        crawlers[i]=subprocess.Popen(order,shell=True,stdout=subprocess.PIPE,stderr=None)

def clock_restart(period):
    while 1:
        print 'Restart automatically'
        restart_all_crawlers()
        time.sleep(period)

clock=multiprocessing.Process(target=clock_restart, args=(10, ))

class index:
    def GET(self):
        print '================'
        print len(crawlers)
        print '================'
        return render.index(crawlers=crawlers)

class add:
    def POST(self):
        order='python ./crawler.py '+str(len(crawlers)+1)
        print order
        crawlers.append(subprocess.Popen(order,shell=True,stdout=subprocess.PIPE,stderr=None))
        raise web.seeother('/')

class add_a_batch:
    def POST(self):
        try:
            count=int(web.input(name=None).count)
        except:
            raise web.seeother('/')
        for i in range(0,count):
            order='python ./crawler.py '+str(len(crawlers)+1)
            print order
            crawlers.append(subprocess.Popen(order,shell=True,stdout=subprocess.PIPE,stderr=None))
        raise web.seeother('/')

class stop:
    def POST(self):
        i=web.input(name=None)
        try:
            kill(crawlers[int(i.crawler_id)])
        except:
            pass
        raise web.seeother('/')

class restart:
    def POST(self):
        i=web.input(name=None)
        try:
            kill(crawlers[int(i.crawler_id)])
        except:
            pass
        order='python crawler.py '+str(int(i.crawler_id)+1)
        print order
        crawlers[int(i.crawler_id)]=subprocess.Popen(order,shell=True,stdout=subprocess.PIPE,stderr=None)
        raise web.seeother('/')

class restart_all():
    def POST(self):
        restart_all_crawlers()
        raise web.seeother('/')


class stop_all():
    def POST(self):
        for i in range(0,len(crawlers)):
            try:
                kill(crawlers[i])
            except:
                pass
        raise web.seeother('/')

class set_restart_auto:
    def POST(self):
        #try:
        #    period=int(web.input(name=None).period)
        #except:
        #    raise web.seeother('/')
        clock.start()
        raise web.seeother('/')
class stop_restart_auto:
    def POST(self):
        clock.terminate()
        raise web.seeother('/')




web.webapi.internalerror = web.debugerror
if __name__ == "__main__":
    app.run()
