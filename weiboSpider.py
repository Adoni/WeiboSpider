#coding:utf8
import json
import time
import codecs
import urllib
import urllib2
import re
from lxml import etree

from deliver import Deliver
from helper import is_not_name
from helper import get_new_line_num
from pymongo import Connection


class WeiboSpider():
    name='Weibo'
    allowed_domains=['weibo.com',]
    access_token = '2.00_BHNxDlxpd6C2fab6e6e09i5M5DE'
    ltp_token='j323H4kIWzQkRwGxiGNUtGhO7f6tGBQNvqWqSW3K'
    #sleep time before try again
    sleep_time=5
    file_in_name='./age_uids.data'


    #The headers to imitate the brower
    all_headers={
            'simple_headers':{
                'Accept':'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
                'Accept-Language':'zh-CN,zh;q=0.8,en;q=0.6',
                'User-Agent':'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_0) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/38.0.2125.111 Safari/537.36'
                }
            }

    def __init__(self):
        print('This is Weibo Spider')
        #Define the deliver
        self.deliver=Deliver()
        #Connect with mongodb
        self.con=Connection()
        self.db = self.con.user_image
        #self.users_collection=self.db.user_age
        self.users_collection=self.db.users
        self.corpse_users=self.db.corpse_users

    def get_html(self, url):
        body={'url':url, 'headers':self.all_headers['simple_headers'],'need_sleep':False}
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
            print e
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
            complete_url = base_url+'uids='+str(uid)+'&access_token='+self.access_token+'&count=100&feature=1&page='+str(page)
            page+=1
            response=self.get_html(complete_url)
            #将网页内容载入为json数据
            try:
                json_data = json.loads(response)
            except:
                return None

            #判断json的有效性
            if(not 'statuses' in json_data):
                return None
            if(not json_data['statuses']):
                return None

            #获取每一条微博的信息
            for status in json_data['statuses']:
                local_status=dict()
                #created_at:微博创建时间
                local_status['created_at']=status['created_at']
                #text:微博信息内容
                text=status['text'].replace('\n',' ')
                #提取表情符提取和分词
                pure_text, emoticons=self.get_emoticons(text)
                if('#' in pure_text):
                    continue
                #分词
                pure_text = self.parse_text(pure_text)
                if(pure_text==None):
                    continue
                local_status['text']=pure_text
                local_status['emoticons']=emoticons
                #source:微博来源
                local_status['source']=status['source']
                #geo:地理信息字段;其中取province_name和city_name
                if(status['geo'] and 'province_name' in status['geo'] and 'city_name' in status['geo']):
                    local_status['province']=status['geo']['province_name']
                    local_status['city']=status['geo']['city_name']
                else:
                    local_status['province']='Null'
                    local_status['city']='Null'
                #reposts_count:转发数
                local_status['response_count']=str(status['reposts_count'])
                #comments_count:评论数
                local_status['comments_count']=str(status['comments_count'])
                statuses.append(local_status)
        return statuses

    def get_uids(self, count=-1):
        all_existed_users=self.users_collection.find({},{'information':1})
        all_uids=[uid.replace('\n','') for uid in open(self.file_in_name).readlines()]
        print all_existed_users.count()
        for existed_user in all_existed_users:
            if existed_user['information']['uid'] in all_uids:
                all_uids.remove(existed_user['information']['uid'])
                #print existed_user['information']['uid']
        print all_existed_users.count()
        if(count==-1):
            return all_uids
        else:
            return all_uids[0:count]

    def get_user_information(self, uid):
        base_url='https://api.weibo.com/2/users/show.json?'
        complete_url=base_url+'access_token='+self.access_token+'&uid='+str(uid)
        html=self.get_html(complete_url)
        if(html=='' or 'error' in html):
            print('error')
            print(complete_url)
            return None
        html=html
        try:
            json_data=json.loads(html)
        except:
            print html
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
        return information

    def get_user_data(self, uid):
        information=self.get_user_information(uid)
        statuses=self.get_user_statuses(uid)
        if information==None or statuses==None:
            return None
        if statuses==[] or information=={}:
            return None
        user_data=dict()
        user_data['information']=information
        user_data['statuses']=statuses
        user_data['parsed']=True
        return user_data

    def start_requests(self):
        uids=self.get_uids()
        for uid in uids:
            print uids.index(uid)
            user_data=self.get_user_data(uid)
            if user_data==None:
                continue
            if is_not_name(user_data['user_information']):
                print 'illgal'
                print user_data
                #self.corpse_users.insert(user_data)
            else:
                print 'leagal'
                print user_data
                #self.users_collection.insert(user_data)
            print 'Done'


if __name__=='__main__':
    spider=WeiboSpider()
    spider.start_requests()
