# -*- coding: utf-8 -*-
#!/usr/bin/env python
import urllib, urllib2
import re
from lxml import etree
from pymongo import Connection
import time

def parse_text(text):
    uri_base = "http://127.0.0.1:12345/ltp"
    data = {
            's': text,
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
        open('data.txt','a').write(text+'\n')
        return None

def get_emoji(text):
    text=text
    # UCS-2
    pat_ucs_2 = u'[\uD800-\uDBFF][\uDC00-\uDFFF]'
    return re.findall(pat_ucs_2,text)

if __name__=='__main__':
    con=Connection()
    db=con.user_image
    users_collection=db.users
    for user in users_collection.find({'parsed':False}):
        new_statuses=[]
        for status in user['statuses']:
            text=status['text']
            if text=='':
                continue
            new_status=status
            try:
                emoji=get_emoji(text)
            except:
                print text
                continue
            new_status['emoticons']=new_status['emoticons'].split(' ')
            if u'' in new_status['emoticons']:
                new_status['emoticons'].remove(u'')
            for e in emoji:
                new_status['emoticons'].append(e)
                text=text.replace(e,' ')
            text=parse_text(text.encode('utf8'))
            if(text==None):
                continue
            new_status['text']=text
            new_statuses.append(new_status)
        user['statuses']=new_statuses
        user['parsed']=True
        users_collection.update({"_id":user["_id"]},user)
