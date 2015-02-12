#coding:utf8
import re
import random
import time
import lxml.html
import json

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

if __name__=='__main__':
    print 'Helper'
    #print get_average_statuses_count()
    #check()
    #output_all_uids()
