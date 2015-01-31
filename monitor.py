import web
import subprocess
urls=(
    '/','index',
    '/add', 'add',
    '/restart', 'restart',
    '/stop', 'stop',
    '/restart_all', 'restart_all',
    '/stop_all', 'stop_all',
    )
app = web.application(urls, globals())
render = web.template.render('templates/')

crawlers=[]
class index:
    def GET(self):
        return render.index(crawlers=crawlers)
class add:
    def POST(self):
        crawlers.append(subprocess.Popen("python crawler.py "+str(len(crawlers)+1),shell=True,stdout=subprocess.PIPE,stderr=subprocess.PIPE))
        raise web.seeother('/')

class stop:
    def POST(self):
        i=web.input(name=None)
        try:
            crawlers[int(i.crawler_id)].terminate()
        except:
            pass
        raise web.seeother('/')

class restart:
    def POST(self):
        i=web.input(name=None)
        try:
            crawlers[int(i.crawler_id)].terminate()
        except:
            pass
        crawlers[int(i.crawler_id)]=subprocess.Popen("python crawler.py "+str(int(i.crawler_id)+1),shell=True,stdout=subprocess.PIPE,stderr=subprocess.PIPE)
        raise web.seeother('/')

class restart_all():
    def POST(self):
        for i in range(0,len(crawlers)):
            try:
                crawlers[i].terminate()
            except:
                pass
            crawlers[i]=subprocess.Popen("python crawler.py "+str(i+1),shell=True,stdout=subprocess.PIPE,stderr=subprocess.PIPE)
        raise web.seeother('/')
class stop_all():
    def POST(self):
        for i in range(0,len(crawlers)):
            try:
                crawlers[i].terminate()
            except:
                pass
        raise web.seeother('/')

web.webapi.internalerror = web.debugerror
if __name__ == "__main__":
    app.run()
