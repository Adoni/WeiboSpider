#!/usr/bin/env python
#coding=utf8
import pika
import urllib2
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

def install_cookie(cookie_file_name):
    global cookieJar
    cookieJar = cookielib.LWPCookieJar(cookie_file_name)
    cookieJar.load( ignore_discard=True, ignore_expires=True)
    opener = urllib2.build_opener(urllib2.HTTPCookieProcessor(cookieJar));
    urllib2.install_opener(opener);
    print('Install Cookie Done')

def get_request(body):
    if('timestamp' in body['url']):
        url=body['url'].replace('timestamp', str(int(time.time()*1000)))
    else:
        url=body['url']
    headers=body['headers']
    request=urllib2.Request(
            url=url,
            headers=headers)
    return request

def get_html(body):
    global sleep_time
    request=get_request(body)
    try:
        request=get_request(body)
        html=urllib2.urlopen(request, timeout=10).read()
    except:
        print('Sleeping...')
        print(body)
        #sleep(sleep_time)
        try:
            html=urllib2.urlopen(request, timeout=10).read()
        except:
            print 'get url error'
            return ''

    if('location.replace' in html):
        print('Redirect..')
        print('Try to get target')
        target=get_target(html)
        if(target==None):
            print 'get target error'
            return ''
        else:
            print('Got target')
            print('Retry to get html')
            body['url']=target[0]
            request=self.get_request(body)
            try:
                html=urllib2.urlopen(request).read()
                print('Got html')
                print('Saveing cookie')
                cookieJar.save()
                print('Save cookie')
            except:
                sleep(sleep_time)
                try:
                    request=self.get_request(body)
                    html=urllib2.urlopen(request).read()
                    print('Got html')
                    print('Saveing cookie')
                    cookieJar.save()
                    print('Save cookie')
                except:
                    print('Error!!!!!')
                    print 'refresh cookie error'
                    print(url)
                    return ''
    return html

#定义接收到消息的处理方法
def request(ch, method, properties, body):
    #将string类型的body转化为字典
    body=eval(body)
    #获取返回
    response = get_html(body)
    #将计算结果发送回控制中心
    ch.basic_publish(exchange='',
                     routing_key=properties.reply_to,
                     body=response)
    #检查是否需要休眠
    if body['need_sleep']:
        sleep(sleep_time)
    ch.basic_ack(delivery_tag = method.delivery_tag)
    print '=========Complete Crawl========='


if __name__ == '__main__':
    #载入cookie
    #cookie_file_name='./cookies/cookie_'+str(sys.argv[1])
    #install_cookie(cookie_file_name)
    #连接rabbitmq服务器
    connection = pika.BlockingConnection(pika.ConnectionParameters(
            host='localhost'))
    channel = connection.channel()
    sleep_time=2
    #定义队列
    channel.queue_declare(queue=settings.QUEUE_NAME)
    channel.basic_qos(prefetch_count=1)
    channel.basic_consume(request, queue=settings.QUEUE_NAME)

    channel.start_consuming()
