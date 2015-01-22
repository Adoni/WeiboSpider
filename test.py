#coding:utf8
import urllib, urllib2
from helper import load_headers
from crawler import install_cookie
from helper import get_target
from helper import normal
from helper import get_htmls_by_domid
import json
import lxml.html

def get_statuses(html):

    def get_time(status):
        time=status.xpath('./div[1]/div[2]//div[@class="WB_from S_txt2"]/a[1]/text()')
        try:
            time=time[0]
        except:
            return None
        while time[0]==' ':
            time=time[1:]
        return time

    def get_source(status):
        source=status.xpath('./div[1]/div[2]//div[@class="WB_from S_txt2"]/a[2]/text()')
        try:
            source=source[0]
        except:
            return None
        while source[0]==' ':
            source=source[1:]
        return source

    def get_echo(status):
        echo=status.xpath('./div[2]/div[1]/ul[1]//li/a[1]/span[1]/span[1]/text()')
        collect=echo[0]
        repost=echo[1]
        response=echo[2]
        like=status.xpath('./div[2]/div[1]/ul[1]//li/a[1]/span[1]/span[1]/span[1]/em[1]/text()')
        if like==[]:
            like=u'赞 0'
        else:
            like=u'赞 '+like[0]
        return collect,repost,response,like

    def get_text(status):
        text=status.xpath('./div[1]/div[2]/div[1]')
        try:
            text=text[0].text_content()
        except:
            return None
        text=text.replace('\\','').replace('/','').replace(' ','').replace('\n','')
        return text

    doc = lxml.html.fromstring(html)
    statuses_list = doc.xpath('//div[@class="WB_cardwrap WB_feed_type S_bg2 "]')
    statuses=[]
    for status in statuses_list:
        print '+++++++++'
        s=dict()
        text=get_text(status)
        if text=='':
            continue
        time=get_time(status)
        source=get_source(status)
        collect,repost,response,like=get_echo(status)
        s['text']=text
        s['time']=time
        s['source']=source
        s['collect']=source
        s['repost']=repost
        s['response']=response
        s['like']=like
        statuses.append(s)
    return statuses

if __name__=='__main__':
    install_cookie('./cookies/cookie_25')
    headers=load_headers()['UserStatus']
    url='http://www.weibo.com/p/aj/v6/mblog/mbloglist?ajwvr=6&domain=100505&profile_ftype=1&is_ori=1&pre_page=1&page=1&pagebar=0&id=1005051831202675'
    url='http://www.weibo.com/1831202675?is_search=0&visible=0&is_ori=1&is_tag=0&profile_ftype=1&page=2#feedtop'
    request=urllib2.Request(
            url=url,
            headers=headers
            )
    try:
        html=urllib2.urlopen(request).read()
        if 'location.replace' in html:
            url=get_target(html)[0]
            request=urllib2.Request(
                url=url,
            )
            html=urllib2.urlopen(request).read()
        open('hehe.html','w').write(html)
        html=get_htmls_by_domid(html,'Pl_Official_MyProfileFeed__')
        html=normal(html[0])
        #html=normal(json.loads(html)['data'])
        for status in get_statuses(html):
            print '+++++++++'
            print status['text']
            print status['time']
            print status['source']
    except Exception as e:
        print e
