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

    #The headers to imitate the brower
    all_headers=load_headers()
    print all_headers

    def __init__(self):
        print('========This is Weibo Spider========')
        #Define the deliver
        self.deliver=Deliver()
        #Connect with mongodb
        self.con=Connection()
        #self.db = self.con.user_image
        self.db = self.con.users_for_liyang
        self.users_collection=self.db.users
        self.corpse_users=self.db.corpse_users

    def construct_url(self,url,params):
        complete_url=url
        p=[]
        for key in params:
            p.append(str(key)+'='+str(params[key]))
        if p is not []:
            complete_url+='?'+'&'.join(p)
        return complete_url

    def get_html(self, url, headers=None, need_sleep=True, params={}):
        body={'url':url, 'headers':headers, 'need_sleep':True, 'params':params}
        #url=self.construct_url(url,params)
        #body={'url':url, 'headers':headers, 'need_sleep':True, 'params':None}
        return self.deliver.request(body)

    #Use this function to take emotions from user posts
    def get_emoticons(self, text):
        pattern_normal='\[[^\]]*\]'
        pattern_ucs_2 = u'[\uD800-\uDBFF][\uDC00-\uDFFF]'
        emoticons=re.findall(pattern_normal, text)+re.findall(pattern_ucs_2, text)
        for emoticon in emoticons:
            text=text.replace(emoticon,' ')
        return text, emoticons

    def get_user_statuses(self, uid, user_name=None):
        statuses=[]
        page=1
        while 1:
            if len(statuses)>1000:
                break
            print 'Try to get %d pages, and now we got %d statuses'%(page,len(statuses))
            url='http://www.weibo.com/u/%s'%uid
            params={
                'is_search':0,
                'visible':0,
                'is_ori':1,
                'is_tag':0,
                'profile_ftype':1,
                'page':page
            }
            html=self.get_html(url=url, headers=self.all_headers['UserStatus'], params=params)
            if html=='':
                print 'Html is empty'
                print url
                break
            open('./hehe.html','w').write(html.text.encode('utf8'))
            print html.url
            print html.headers
            html=get_htmls_by_domid(html.text,'Pl_Official_MyProfileFeed__')
            if not html:
                print 'Html is None'
                print url
                break
            html=normal(html[0])
            tmp_statuses=get_statuses(html)
            if tmp_statuses==[]:
                print html
                break
            statuses+=tmp_statuses
            for pagebar in range(0,2):
                url='http://www.weibo.com/p/aj/v6/mblog/mbloglist'
                params={
                    'ajwvr':6,
                    'domain':100505,
                    'profile_ftype':1,
                    'is_ori':1,
                    'pre_page':page,
                    'page':page,
                    'pagebar':pagebar,
                    'id':'100505'+uid
                }
                html=self.get_html(url=url, headers=self.all_headers['UserStatus'], params=params)
                try:
                    json_data=html.json()
                except Exception as e:
                    print '========Error when try to load as json========='
                    print '========Error:========'
                    print e
                    print '========End========'
                    continue
                try:
                    html=normal(json_data['data'])
                except Exception as e:
                    print '========Error when try to get html from json data========='
                    print '========Error:========'
                    print e
                    print '========End========'
                    continue
                tmp_statuses=get_statuses(html)
                if tmp_statuses==[]:
                    continue
                statuses+=tmp_statuses
            page+=1
            break
        return statuses

    def get_uids(self, count=-1, uid_file='./uids.bin'):
        all_uids=cPickle.load(open(uid_file,'rb'))
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

    def get_user_birthday(self,uid):
        complete_url='http://weibo.com/u/'+str(uid)
        html=self.get_html(complete_url, self.all_headers['Homepage'])
        if not html:
            print 'get html error'
            return None
        html=get_htmls_by_domid(html.text,'Pl_Core_UserInfo__')
        if not html:
            print complete_url
            print 'get div error'
            return None
        html=normal(html[0])
        pattern=re.compile(u'\d{4}年\d{1,2}月\d{1,2}日')
        result=pattern.findall(html)
        if len(result)==1:
            birthday=result[0].replace(u'年','-').replace(u'月','-').replace(u'日','')
            return birthday
        else:
            print 'no birthday'
            return None

    def get_user_information(self, uid):
        url='https://api.weibo.com/2/users/show.json'
        params={
            'access_token':self.access_token,
            'uid':str(uid)
        }
        html=self.get_html(url=url, headers=self.all_headers['Simple'], params=params, need_sleep=False)
        if(html=='' or 'error' in html):
            print('========Html is empty or error in html========')
            print '=======End========'
            #print html
            print '=======Complete url========'
            print(url)
            print '=======End========'
            return None
        html=html
        try:
            json_data=html.json()
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
            information['avatar_large']=str(json_data['avatar_large'])
            information['verified']=str(json_data['verified'])
        except Exception as e:
            print '========Error when constructing the dict information========'
            print '========Error:========'
            print e
            print json_data.keys()
            #open(str(uid)+'.construct','w').write(str(json_data))
            print '========End========'
            return None
        return information

    def get_user_data(self, uid):
        #information=self.get_user_information(uid)
        #if information==None:
        #    return None
        statuses=self.get_user_statuses(uid)
        if statuses==[] or statuses==None:
            return None
        user_data=dict()
        #user_data['information']=information
        user_data['statuses']=statuses
        user_data['parsed']=False
        user_data['type']='new'
        if 'avatar_large' in information:
            user_data['got_avatar_large']=True
        else:
            user_data['got_avatar_large']=False
        return user_data

    def start_requests(self):
        uid_file='/Users/sunxiaofei/workspace/ir_project/for_liyang/uids_for_liyang.bin'
        uids=self.get_uids(uid_file=uid_file)
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
            #if is_not_name(user_data['information']['screen_name']):
            #   print '========The name is illgal========'
            #    self.corpse_users.insert(user_data)
            #    print '========End========'
            #else:
            #    print '========The name is leagal========'
            #    print 'leagal'
            #    print '========End========'
            #    self.users_collection.insert(user_data)
            self.users_collection.insert(user_data)

    def insert_birthday(self):
        from progressive.bar import Bar
        total_count=self.users_collection.find({'have_birthday':None}).count()
        finish_count=0
        bar = Bar(max_value=total_count, fallback=True)
        bar.cursor.clear_lines(2)
        bar.cursor.save()
        for user in self.users_collection.find({'have_birthday':None}):
            birthday=self.get_user_birthday(user['information']['uid'])
            continue
            if birthday is None:
                self.users_collection.update({'_id':user['_id']}, {'$set':{'have_birthday':False}})
            else:
                user['information']['birthday']=birthday
                self.users_collection.update({'_id':user['_id']}, {'$set':{'information':user['information'],'have_birthday':True}})
            finish_count+=1
            #bar.cursor.restore()
            #bar.draw(value=finish_count)

if __name__=='__main__':
    spider=WeiboSpider()
    print spider.get_user_statuses('1831202675')
    #spider.start_requests()
    #print spider.get_user_birthday('1448482450')
    #h=spider.get_html('http://weibo.com/u/1883388073',headers=spider.all_headers['UserStatus'])
    #open('./hehe.html','w').write(h.text.encode('utf8'))
    #print(h.url)
    #print h.headers
    # print('======')
    # for i in h.history:
    #     print i.url
    #     print i.status_code
    #     print i.headers
    #     print i.text
    # spider.insert_birthday()
