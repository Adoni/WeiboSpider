#coding:utf8
import urllib, urllib2
from helper import load_headers
from crawler import install_cookie
from helper import get_target
from helper import normal
from helper import get_htmls_by_domid
from helper import get_statuses
import json
import lxml.html

if __name__=='__main__':
    install_cookie('./cookies/cookie_1')
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
            print status['emoticons']
    except Exception as e:
        print e
