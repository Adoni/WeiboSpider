#coding:utf8
import re
import random
import time
import cPickle

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
    bad_words=[
            u'团委',
            u'党委',
            u'公安',
            u'交警',
            u'消防',
            u'官网',
            u'外卖',
            u'官方',
            u'订餐',
            u'基金',
            u'团购',
            u'大学',
            u'资讯',
            u'新闻',
            u'後援會',
            u'海洋馆',
            u'报',
            u'礼服',
            u'平台',
            u'咨询',
            u'杂志',
            u'粉丝',
            u'论坛',
            u'联盟',
            u'公司',
            u'讲坛',
            u'旅行社',
            u'出版社',
            u'电视台',
            u'公共',
            u'微博',
            u'24小时服务',
            u'馆',
            u'同城会',
            u'老乡会',
            u'校友会',
            u'网',
            u'店']
    for w in bad_words:
        if(w in name):
            return True
    return False

def sleep(sleep_time):
    sleep_time=sleep_time+random.randint(-2,2)
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
    con = Connection()
    db = con.user_image
    users=db.user_age
    l=0.0
    for user in users.find():
        l+=len(user['statuses'])
    l/=users.find().count()
    return l

def check():
    from pymongo import Connection
    con=Connection()
    db=con.user_image
    users=db.users
    number=dict()
    number['None']=0
    index=0
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
    cPickle.dump(uids,open('uids.data','wb'))

def get_htmls_by_domid(html, domid):
    pat=ur'{.*"domid":"%s.*}'%domid
    try:
        results=re.findall(pat, html.decode('utf8'))
    except:
        results=re.findall(pat, html)
    if(results==[]):
        print 'No html'
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

def sleep(sleep_time):
    sleep_time=sleep_time+random.randint(-5,5)
    print('Sleeping for '+str(sleep_time)+' seconds')
    time.sleep(sleep_time)
    print('Wake up')


if __name__=='__main__':
    #print get_average_statuses_count()
    #check()
    output_all_uids()
