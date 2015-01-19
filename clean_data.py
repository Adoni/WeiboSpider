#coding=utf8
import MySQLdb
import random
import sys

def isNotName(name):
    bad_words=['团委',
            '党委',
            '公安',
            '交警',
            '消防',
            '官网',
            '外卖',
            '官方',
            '订餐',
            '基金',
            '团购',
            '大学',
            '资讯',
            '新闻',
            '後援會',
            '海洋馆',
            '报',
            '礼服',
            '平台',
            '咨询',
            '粉丝',
            '论坛',
            '联盟',
            '公司',
            '讲坛',
            '旅行社',
            '公共',
            '微博',
            '24小时服务',
            '网',
            '店']
    for w in bad_words:
        if(w in name):
            return True
    return False

def clean(fname,foutname):
    total=0.0
    count=0
    fin=open(fname,'r').readlines()
    fout=open(foutname,'w')
    for line in fin:
        userinfo=line[0:-1].split('\t')
        if(isNotName(userinfo[1]) or len(userinfo[1])>15):
            print(userinfo[1])
            total+=len(userinfo[1])
            count+=1
            continue
        fout.write(line)
    fout.close()
    if(count>0):
        print('平均值：'+str(total/count))
    else:
        print('No machine use')

if(__name__=='__main__'):
    clean("./all_id.data", "./all_id.data")
