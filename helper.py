#coding:utf8
import re
import random
import time
import cPickle
import lxml.html
from lxml import etree
import json
import urllib
import urllib2
from pyltp import Segmentor
from pyltp import Postagger
import requests
import urllib
import json
import os

global segmentor
MODELDIR='./ltp_model/'
segmentor = Segmentor()
segmentor.load("./ltp_model/cws.model")
postagger = Postagger()
postagger.load(os.path.join(MODELDIR, "pos.model"))

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
        if len(echo)<3:
            return None,None,None,None
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

    def get_emoticons(status):
        emoticons_list=status.xpath('./div[1]/div[2]/div[1]//img')
        emoticons=[]
        for emoticon in emoticons_list:
            emoticon=emoticon.get('src')
            emoticons.append(emoticon)
        return emoticons

    try:
        doc = lxml.html.fromstring(html)
    except:
        return []
    statuses_list = doc.xpath('//div[@class="WB_cardwrap WB_feed_type S_bg2 "]')
    statuses=[]
    for status in statuses_list:
        s=dict()
        mid=status.get('mid')
        text=get_text(status)
        if text=='':
            continue
        emoticons=get_emoticons(status)
        time=get_time(status)
        source=get_source(status)
        collect,repost,response,like=get_echo(status)
        if collect==None:
            continue
        s['mid']=mid
        s['text']=text
        s['emoticons']=emoticons
        s['time']=time
        s['source']=source
        s['collect']=collect
        s['repost']=repost
        s['response']=response
        s['like']=like
        statuses.append(s)
    return statuses

def parse_text(text):
    try:
        text=text.encode('utf8')
        words = segmentor.segment(text)
    except Exception as e:
        print [text]
        print e
        return None
    return [word for word in words]
def postagger_text(text):
    try:
        text=text.encode('utf8')
        words= segmentor.segment(text)
        print words
        words = postagger.postag(words)
        print words
    except Exception as e:
        print [text]
        print e
        return None
    return [word for word in words]

def get_href_from_text(text, html):
    pat='<a[^<,>]*>'+text+'<'
    with_hrefs=re.findall(pat,html)
    ans=[]
    for with_href in with_hrefs:
        with_href=with_href.replace('\\','')
        pat='href="[^"]*"'
        href=re.search(pat,with_href)
        if(href==None):
            return None
        else:
            ans.append(href.group()[6:-1])
    if(ans==[]):
        return None
    return ans

def is_not_name(name):
    bad_words=[word.replace('\n','').decode('utf8') for word in open('./bad_word.bin')]
    for w in bad_words:
        if w in name :
            return True
    return False

def clean_users():
    from pymongo import Connection
    user_image=Connection().user_image
    users=user_image.users
    corpse_users=user_image.corpse_users
    print corpse_users.count()
    for user in users.find():
        if is_not_name(user['information']['screen_name']):
            print user['information']['screen_name']
            corpse_users.insert(user)
            users.remove({'_id':user['_id']})

def sleep(sleep_time):
    sleep_time=sleep_time+random.randint(-2,2)
    print sleep_time
    if sleep_time<=0:
        sleep_time=0
    print('Sleeping for '+str(sleep_time)+' seconds')
    time.sleep(sleep_time)
    print('Wake up')

def get_target(html):
    if(not 'location.replace' in html):
        print('No location.replace in html')
        return None
    pat="location.replace\('[^']*'\)"
    a=re.findall(pat,html)
    pat='location.replace\("[^"]*"\)'
    b=re.findall(pat,html)
    ans=[]
    for url in a:
        ans.append(url[18:-2])
    for url in b:
        ans.append(url[18:-2])
    if(ans==[]):
        return None
    else:
        return ans

def get_average_statuses_count():
    from pymongo import Connection
    from progressbar import ProgressBar
    from progressive.bar import Bar
    con = Connection()
    db = con.user_image
    users=db.users
    l=0.0
    total_count=users.count()
    finish_count=0
    bar = Bar(max_value=total_count, fallback=True)
    bar.cursor.clear_lines(2)
    bar.cursor.save()
    for user in users.find():
        if len(user['statuses'])<100:
            continue
        l+=len(user['statuses'])
        finish_count+=1
        bar.cursor.restore()
        bar.draw(value=finish_count)
    l/=finish_count
    return l

def clean_database():
    from pymongo import Connection
    con = Connection()
    db = con.user_image
    users=db.users
    users.remove({'type':None})

def check():
    from pymongo import Connection
    con=Connection()
    db=con.user_image
    users=db.users
    number=dict()
    number['None']=0
    index=0
    count=0
    for user in users.find():
        try:
            if len(user['statuses'])>300:
                count+=1
        except:
            print user
            exit(0)
    print count
    exit(0)
    for user in users.find():
        index+=1
        if index%1000==0:
            print index
        name=user['information']['screen_name']
        sources=set()
        for status in user['statuses']:
            source=status['source']
            try:
                source=source[source.index('>')+1:source.index('</')]
            except:
                continue
            sources.add(source)
        if sources==[]:
            print name
        for s in sources:
            if s in number:
                number[s]+=1
            else:
                number[s]=1
    number=sorted(number.items(), key=lambda d:d[1], reverse=True)
    f=open('source.txt','w')
    for s in number:
        if s[1]>1:
            f.write(s[0].encode('utf8')+' '+str(s[1])+'\n')

def output_all_uids():
    from pymongo import Connection
    con = Connection()
    db = con.user_image
    users=db.users
    uids=[]
    index=0
    total_count=users.count()
    for user in users.find():
        if index%1000==0:
            print index,total_count
        uids.append(user['information']['uid'])
        index+=1
    cPickle.dump(uids,open('uids.bin','wb'))

def get_htmls_by_domid(html, domid):
    pat=ur'{.*"domid":"%s.*}'%domid
    try:
        results=re.findall(pat, html.decode('utf8'))
    except:
        results=re.findall(pat, html)
    if(results==[]):
        return None
    try:
        htmls=[]
        for result in results:
            if 'html' in result:
                html=normal(result[result.index('html')+7:-2])
                #htmls.append(normal(result['html']).decode('utf8'))#[22:-1].replace('\\','')
                htmls.append(html)
        return htmls
    except Exception as e:
        print e
        print 'No dict'
        return None

def get_school(html):
    if(not '&school' in html):
        return None
    pat='<a[^<>]*&school[^<>]*>[^<>]*<'
    a=re.findall(pat,html)
    ans=[]
    for school in a:
        pat='>.*<'
        school=re.findall(pat,school)
        if(school==[]):
            continue
        else:
            ans.append(school[0][1:-1])
    if(ans==[]):
        return None
    else:
        return ans

def get_target(html):
    if(not 'location.replace' in html):
        print('No location.replace in html')
        return None
    pat="location.replace\('[^']*'\)"
    a=re.findall(pat,html)
    pat='location.replace\("[^"]*"\)'
    b=re.findall(pat,html)
    ans=[]
    for url in a:
        ans.append(url[18:-2])
    for url in b:
        ans.append(url[18:-2])
    if(ans==[]):
        return None
    else:
        return ans

def remove_trn(s):
    strings=['\t','\r','\n']
    for ss in strings:
        s=s.replace(ss,'')
    return s

def normal(html):
    to_replace=dict()
    to_replace['\\t']='\t'
    to_replace['\\n']='\n'
    to_replace['\\r']='\r'
    to_replace['\\"']='"'
    to_replace['\\/']='/'
    for key in to_replace.keys():
        html=html.replace(key, to_replace[key])
    return html

def load_headers():
    f=open('./headers.bin')
    headers_list={}
    header_name=''
    headers={}
    for l in f:
        l=l.replace('\n','')
        if l.startswith('BEGIN'):
            header_name=l.split(' ')[1]
            continue
        if l.startswith('END'):
            headers_list[header_name]=headers
            headers={}
            continue
        l=l.split(':')
        headers[l[0]]=l[1]
    return headers_list

def get_htmls_by_domid(html, domid):
    pat=ur'{.*"domid":"%s.*}'%domid
    try:
        results=re.findall(pat, html.decode('utf8'))
    except:
        results=re.findall(pat, html)
    if(results==[]):
        return None
    try:
        htmls=[]
        for result in results:
            if 'html' in result:
                html=normal(result[result.index('html')+7:-2])
                #htmls.append(normal(result['html']).decode('utf8'))#[22:-1].replace('\\','')
                htmls.append(html)
        return htmls
    except Exception as e:
        print e
        print 'No dict'
        return None

def get_image_description(image_url):
    url='http://stu.baidu.com/n/searchpc'
    objurl=urllib.quote_plus(image_url)
    objurl=image_url
    data={
        'queryImageUrl':objurl,
    }
    try:
        r=requests.get(url=url,params=data,timeout=20)
    except:
        return None
    #r=requests.get('http://stu.baidu.com/n/searchpc?queryImageUrl=http%3A%2F%2Ftp4.sinaimg.cn%2F5103578591%2F180%2F22871946288%2F1')
    pattern = re.compile(r'keywords:\'.*\'')
    d=pattern.findall(r.text.encode('utf8'))
    if len(d)<1:
        return []
    descriptions=d[0][12:-3].split('},{')
    keys=[]
    for d in descriptions:
        if u'keyword' not in d:
            continue
        pattern=re.compile(r'keyword\\x22:\\x22[^,]*')
        c=compile('key=u"'+pattern.findall(d)[0][16:-4].replace('\\\\','\\')+'"','','exec')
        exec c
        keys.append(key)
    return keys

def insert_avatar_url():
    import requests
    from pymongo import Connection
    from progressbar import ProgressBar
    from progressive.bar import Bar
    pbar = ProgressBar(maxval=100)
    con = Connection()
    db = con.user_image
    users=db.users
    total_count=users.find({'got_avatar_large':None}).count()
    finish_count=0
    bar = Bar(max_value=total_count, fallback=True)
    bar.cursor.clear_lines(2)
    bar.cursor.save()
    for user in users.find({'got_avatar_large':None}):
        uid=user['information']['uid']
        access_token = '2.00_BHNxDlxpd6C2fab6e6e09i5M5DE'
        url='https://api.weibo.com/2/users/show.json'
        params={
            'access_token':access_token,
            'uid':str(uid)
        }
        try:
            html=requests.get(url=url,params=params,timeout=5)
            information=html.json()
            user['information']['avatar_large']=information['avatar_large']
            users.update({'_id':user['_id']}, {'$set':{'information':user['information'], 'got_avatar_large':True}})
            finish_count+=1
        except:
            continue
        bar.cursor.restore()
        bar.draw(value=finish_count)

def insert_image_descriptions():
    import requests
    from pymongo import Connection
    from progressbar import ProgressBar
    from progressive.bar import Bar
    pbar = ProgressBar(maxval=100)
    con = Connection()
    db = con.user_image
    users=db.users
    total_count=users.find({'got_avatar_large':True, 'got_image_descriptions':None}).count()
    finish_count=0
    bar = Bar(max_value=total_count, fallback=True)
    bar.cursor.clear_lines(2)
    bar.cursor.save()
    for user in users.find({'got_avatar_large':True, 'got_image_descriptions':None}):
        image_url=user['information']['avatar_large']
        try:
            descriptions=get_image_description(image_url)
            if descriptions==None:
                continue
            if descriptions==[]:
                users.update({'_id':user['_id']}, {'$set':{'information':user['information'],'got_image_descriptions':False}})
            print user['information']['gender']+' '+'|'.join(descriptions)
            user['information']['descriptions']=[]
            for d in descriptions:
                dd=parse_text(d)
                if dd==None:
                    dd=[d]
                user['information']['descriptions'].append(dd)
            users.update({'_id':user['_id']}, {'$set':{'information':user['information'], 'got_image_descriptions':True}})
            finish_count+=1
        except Exception as e:
            raise
            print e
            continue
        #bar.cursor.restore()
        #bar.draw(value=finish_count)

def parse_all():
    from pymongo import Connection
    from progressbar import ProgressBar
    from progressive.bar import Bar
    con = Connection()
    db = con.user_image
    users=db.users
    try:
        # UCS-4
        highpoints = re.compile(u'([\U00002600-\U000027BF])|([\U0001f300-\U0001f64F])|([\U0001f680-\U0001f6FF])')
        highpoints = re.compile(u'[\U00010000-\U0010ffff]')
    except re.error:
        # UCS-2
        highpoints = re.compile(u'([\u2600-\u27BF])|([\uD83C][\uDF00-\uDFFF])|([\uD83D][\uDC00-\uDE4F])|([\uD83D][\uDE80-\uDEFF])')
    total_count=users.find({'parsed':False}).count()
    finish_count=0
    bar = Bar(max_value=total_count, fallback=True)
    bar.cursor.clear_lines(2)
    bar.cursor.save()
    for user in users.find({'parsed':False}):#.limit(10):
        statuses=user['statuses']
        success=True
        for i in xrange(len(statuses)):
            emojs=highpoints.findall(statuses[i]['text'])
            puretext=highpoints.sub('',statuses[i]['text'])
            parsed_text=parse_text(puretext)
            if parsed_text is None:
                success=False
                print emojs
                print [statuses[i]['text']]
                break
            statuses[i]['text']=parsed_text
            statuses[i]['emoticons']+=emojs
        if success:
            finish_count+=1
            users.update({'_id':user['_id']}, {'$set':{'statuses':statuses, 'parsed':True}})
            bar.cursor.restore()
            bar.draw(value=finish_count)

def parse_image_descriptions():
    from pymongo import Connection
    from progressive.bar import Bar
    con = Connection()
    db = con.user_image
    users=db.users
    total_count=users.find({'got_image_descriptions':True}).count()
    finish_count=0
    bar = Bar(max_value=total_count, fallback=True)
    bar.cursor.clear_lines(2)
    bar.cursor.save()
    for user in users.find({'got_image_descriptions':True}):
        finish_count+=1
        bar.cursor.restore()
        bar.draw(value=finish_count)
        try:
            descriptions=[]
            if type(user['information']['descriptions']) is list:
                continue
            for d in user['information']['descriptions']:
                dd=parse_text(d)
                if dd==None:
                    dd=[d]
                descriptions.append(dd)
            user['information']['descriptions']=descriptions
            users.update({'_id':user['_id']}, {'$set':{'information':user['information'], 'got_image_descriptions':True}})
        except Exception as e:
            continue

if __name__=='__main__':
    print '========Helper========'
    #clean_users()
    #parse_image_descriptions()
    #parse_all()
    #insert_avatar_url()
    #insert_image_descriptions()
    #print get_average_statuses_count()
    #print parse_text(u'呼伦贝尔大草原')
    print postagger_text(u'呼伦贝尔大草原')
