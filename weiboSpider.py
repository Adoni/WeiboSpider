#coding:utf8
import json
import time
import codecs
import urllib
import urllib2
import re
from lxml import etree
import cPickle

from deliver import Deliver
from helper import is_not_name
from helper import get_statuses
from helper import load_headers
from helper import normal
from helper import get_htmls_by_domid
from pymongo import Connection


class WeiboSpider():
    name='Weibo'
    allowed_domains=['weibo.com',]
    access_token = '2.00_BHNxDlxpd6C2fab6e6e09i5M5DE'
    ltp_token='j323H4kIWzQkRwGxiGNUtGhO7f6tGBQNvqWqSW3K'
    #sleep time before try again
    sleep_time=50

    #The headers to imitate the brower
    all_headers=load_headers()

    def __init__(self):
        print('========This is Weibo Spider========')
        #Define the deliver
        self.deliver=Deliver()
        #Connect with mongodb
        self.con=Connection()
        self.db = self.con.user_image
        #self.users_collection=self.db.user_age
        self.users_collection=self.db.users
        self.corpse_users=self.db.corpse_users

    def get_html(self, url):
        body={'url':url, 'headers':self.all_headers['UserStatus'],'need_sleep':True}
        return self.deliver.request(body)

    def parse_text(self, text):
        uri_base = "http://127.0.0.1:12345/ltp"
        data = {
                's': text.encode('utf8'),
                'x': 'n',
                'c': 'utf-8',
                't': 'ws'}

        request = urllib2.Request(uri_base)
        params = urllib.urlencode(data)
        try:
            result=[]
            response = urllib2.urlopen(request, params)
            content = response.read().strip()
            tree=etree.XML(content)
            nodes=tree.xpath('//word')
            for node in nodes:
                result.append(node.get('cont'))
            return result
        except Exception as e:
            print '========Error when parse text========'
            print '========Error:========'
            print e
            print '========End========'
            return None

    #Use this function to take emotions from user posts
    def get_emoticons(self, text):
        pattern_normal='\[[^\]]*\]'
        pattern_ucs_2 = u'[\uD800-\uDBFF][\uDC00-\uDFFF]'
        emoticons=re.findall(pattern_normal, text)+re.findall(pattern_ucs_2, text)
        for emoticon in emoticons:
            text=text.replace(emoticon,' ')
        return text, emoticons

    def get_user_statuses(self, uid):
        base_url='https://api.weibo.com/2/statuses/timeline_batch.json?'
        #statuses是要返回的数据
        statuses=[]
        page=1
        while 1:
            if len(statuses)>1000:
                break
            print 'Try to get %d pages, and now we got %d statuses'%(page,len(statuses))
            #获取基础的网页
            url='http://www.weibo.com/%s?is_search=0&visible=0&is_ori=1&is_tag=0&profile_ftype=1&page=%d#feedtop'%(uid,page)
            html=self.get_html(url)
            html=get_htmls_by_domid(html,'Pl_Official_MyProfileFeed__')
            if not html:
                break
            html=normal(html[0])
            tmp_statuses=get_statuses(html)
            if tmp_statuses==[]:
                break
            statuses+=tmp_statuses
            for pagebar in range(0,2):
                url='http://www.weibo.com/p/aj/v6/mblog/mbloglist?ajwvr=6&domain=100505&profile_ftype=1&is_ori=1&pre_page=%d&page=%d&pagebar=%d&id=100505%s'%(page, page, pagebar, uid)
                html=self.get_html(url)
                try:
                    json_data=json.loads(html)
                except Exception as e:
                    print '========Error when try to load as json========='
                    print '========Error:========'
                    print e
                    open(str(uid)+'.loadjson','w').write(html)
                    print '========End========'
                    continue
                try:
                    html=normal(json_data['data'])
                except Exception as e:
                    print '========Error when try to get html from json data========='
                    print '========Error:========'
                    print e
                    open(str(uid)+'.gethtmlfromjsondata','w').write(str(json_data))
                    print '========End========'
                    continue
                tmp_statuses=get_statuses(html)
                if tmp_statuses==[]:
                    continue
                statuses+=tmp_statuses
            page+=1
        return statuses

    def get_uids(self, count=-1):
        all_uids=cPickle.load(open('./uids.bin','rb'))
        all_existed_users=self.users_collection.find({},{'information':1})
        for existed_user in all_existed_users:
            if existed_user['information']['uid'] in all_uids:
                all_uids.remove(existed_user['information']['uid'])
        all_existed_corpse_users=self.corpse_users.find({},{'information':1})
        for existed_user in all_existed_corpse_users:
            if existed_user['information']['uid'] in all_uids:
                all_uids.remove(existed_user['information']['uid'])
        print '========There are %d users and %d corpse_users users========'%(all_existed_users.count(),all_existed_corpse_users.count())
        if(count==-1):
            return all_uids
        else:
            return all_uids[0:count]

    def get_user_information(self, uid):
        base_url='https://api.weibo.com/2/users/show.json?'
        complete_url=base_url+'access_token='+self.access_token+'&uid='+str(uid)
        html=self.get_html(complete_url)
        if(html=='' or 'error' in html):
            print('========Html is empty or error in html========')
            print '=======End========'
            print '=======Complete url========'
            print(complete_url)
            print '=======End========'
            return None
        html=html
        try:
            json_data=json.loads(html)
        except:
            print '=======Error when load json========'
            print '=======End========'
            return None
        try:
            information=dict()
            information['uid']=str(json_data['id'])
            information['screen_name']=json_data['screen_name']
            information['province']=str(json_data['province'])
            information['city']=str(json_data['city'])
            information['location']=json_data['location']
            information['gender']=str(json_data['gender'])
            information['followers_count']=str(json_data['followers_count'])
            information['friends_count']=str(json_data['friends_count'])
            information['bi_followers_count']=str(json_data['bi_followers_count'])
            information['verified']=str(json_data['verified'])
        except Exception as e:
            print '========Error when constructing the dict information========'
            print '========Error:========'
            print e
            print json_data.keys()
            open(str(uid)+'.construct','w').write(str(json_data))
            print '========End========'
            return None
        return information

    def get_user_data(self, uid):
        information=self.get_user_information(uid)
        if information==None:
            return None
        statuses=self.get_user_statuses(uid)
        if statuses==[] or statuses==None:
            return None
        user_data=dict()
        user_data['information']=information
        user_data['statuses']=statuses
        user_data['parsed']=False
        return user_data

    def start_requests(self):
        uids=self.get_uids()
        print '========The count of uids to crawl:========'
        print len(uids)
        print '========End========'
        for uid in uids:
            print '========Index:========'
            print uids.index(uid)
            print '========End========'
            user_data=self.get_user_data(uid)
            if user_data==None:
                print '========User data is None========'
                continue
            if is_not_name(user_data['information']['screen_name']):
                print '========The name is illgal========'
                self.corpse_users.insert(user_data)
                print '========End========'
            else:
                print '========The name is leagal========'
                print 'leagal'
                print '========End========'
                self.users_collection.insert(user_data)

if __name__=='__main__':
    spider=WeiboSpider()
    spider.start_requests()
    #uid='2412928981'
    #spider.get_user_information(uid)
