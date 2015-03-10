#!/usr/bin/env python
#coding=utf8
import pika
import requests
from helper import sleep
import cookielib
from helper import get_target
import sys
import random
import time
import copy
import settings

global cookieJar
global sleep_time
global headers

global session

def install_cookie(cookie_file_name):
    global cookieJar
    global session
    cookie_str='''SINAGLOBAL=968399799894.5415.1424607979995;myuid=3623327573;un=adoni_spider1@163.com;wvr=6;YF-Page-G0=416186e6974c7d5349e42861f3303251;SUS=SID-5518729600-1425888094-GZ-fd4sx-843e1f91c2da74de87b0be35afdadc63;SUE=es%3Dfbe36fab51c05947e411390deaf0050b%26ev%3Dv1%26es2%3D4dd928e364ed1e5801ce7c70223979f6%26rs0%3Dic4cz8Z4txOpUn2VPOxGpG7RDy8Tyi3e%252Bwww9f63IFiAdZYIPxqcw2ZGYEkD6Av3NaY9v3tqn5rl72vvOBiPAfkHkj5mGml2C25h%252Be%252BS2cIpjKpAZU0JXok3lFWMRlNVTWtWP3aA8g0bqJYhKkn0%252BMyVwkopv6DvW2z4oF%252FD7AM%253D%26rv%3D0;SUP=cv%3D1%26bt%3D1425888094%26et%3D1425974494%26d%3Dc909%26i%3Ddc63%26us%3D1%26vf%3D0%26vt%3D0%26ac%3D0%26st%3D0%26uid%3D5518729600%26name%3Dadoni_spider1%2540163.com%26nick%3Dadoni_spider_1%26fmp%3D%26lcp%3D;SUB=_2A255-SMODeTxGeNL6loW8ifKyzyIHXVajxPGrDV8PUNbvtBuLVjtkW9SKMD9o05JSjscLslAxcssYBXzow..;SUBP=0033WrSXqPxfM725Ws9jqgMF55529P9D9WhWDXeNEehUidkXekqaL9uc5JpX5KMt; SUHB=0y0JhecEc3ZAlu; ALF=1457424093;SSOLoginState=1425888094; YF-V5-G0=bc033c7c7d5164aa92fea9d75cc6f127; _s_tentry=login.sina.com.cn;Apache=6462309621274.472.1425888101165; ULV=1425888101174:3:2:1:6462309621274.472.1425888101165:1425703260785;UOR=developer.51cto.com,widget.weibo.com,login.sina.com.cn'''
    cookie_str=cookie_str.replace(' ','')
    cookie_dict=dict()
    for c in cookie_str.split(';'):
        cookie_dict[c.split('=')[0]]=c.split('=')[1]
    cookieJar=requests.utils.cookiejar_from_dict(cookie_dict)
    #cookieJar = cookielib.LWPCookieJar(cookie_file_name)
    #cookieJar.load( ignore_discard=True, ignore_expires=True)
    session=requests.Session()
    session.cookies = cookieJar
    print('Install Cookie Done')

def get_html(url):
    global sleep_time
    global session
    html=session.get(url)
    #print html
    if('location.replace' in html.text):
        print('Redirect..')
        print('Try to get target')
        target=get_target(html.text)
        if(target==None):
            print 'get target error'
            return ''
        else:
            print('Got target')
            print('Retry to get html')
            url=target[0]
            try:
                html=session.get(url)
                print('Got html')
                print('Saveing cookie')
                cookieJar.save(ignore_discard=True)
                print('Save cookie')
            except:
                print('Error!!!!!')
                print 'refresh cookie error'
                return ''
    return html

if __name__ == '__main__':
    cookie_file_name='./cookies/cookie_'+'12'#str(sys.argv[1])
    install_cookie(cookie_file_name)
    url='http://weibo.com/p/1006051235576307/info?mod=pedit_more'
    url='http://weibo.com/hangeng'
    print get_html(url).text
