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
import requests
import cPickle
import StringIO

global cookieJar
global sleep_time
global headers
global session

global debug
debug=False

def myprint(information):
    if debug:
        print information

def install_cookie(cookie_file_name):
    global cookieJar
    global session
    cookies=requests.utils.cookiejar_from_dict(cPickle.load(open(cookie_file_name,'rb')))
    session=requests.Session()
    session.cookies=cookies

def update_time(body):
    if 'timestamp' in body['params']:
        body['params']['timestamp']=str(int(time.time()*1000))
    return body

def get_html(body):
    global sleep_time
    global session
    try:
        body=update_time(body)
        myprint(body['headers'])
        html=session.get(url=body['url'], headers=body['headers'],
                params=body['params'],timeout=20,allow_redirects=True)
    except requests.exceptions.ConnectionError:
        raise Exception('ConnectionError')
    except requests.exceptions.Timeout:
        try:
            body=update_time(body)
            html=session.get(url=body['url'], headers=body['headers'], params=body['params'], timeout=20)
        except Exception as e:
            myprint(e)
            return ''
    except Exception as e:
        raise

    myprint(html.text)
    if 'location.replace' in html.text:
        target=get_target(html.text)
        if(target==None):
            raise Exception('Cannot find redirect target')
        else:
            body['url']=target[0]
            myprint(target[0])
            try:
                body=update_time(body)
                html=session.get(url=body['url'], headers=body['headers'], params=body['params'], timeout=20)
                myprint(html.text)
                myprint(html.url)
                cookies=requests.utils.dict_from_cookiejar(session.cookies)
                cPickle.dump(cookies,open('./cookies/cookie_'+str(sys.argv[1]),'wb'))
            except:
                sleep(sleep_time)
                try:
                    body=update_time(body)
                    html=session.get(url=body['url'], headers=body['headers'],params=body['params'], timeout=20)
                    myprint(html.url)
                    cookies=requests.utils.dict_from_cookiejar(session.cookies)
                    cPickle.dump(cookies,open('./cookies/cookie_'+str(sys.argv[1]),'wb'))
                except Exception as e:
                    print '============'
                    myprint(e)
                    print '============'
                    raise Exception('Cannot find redirect target')
    if '<title>Sina Visitor System</title>' in html.text:
        raise(Exception('Cookie is past due'))
    if '<title>502' in html.text:
        raise(Exception('502 error'))
    return html

#定义接收到消息的处理方法
def on_request(ch, method, props, body):
    #将string类型的body转化为字典
    body=eval(body)
    #获取返回
    html=get_html(body)
    output_file=StringIO.StringIO()
    cPickle.dump(html, output_file)
    output_file.flush()
    #将计算结果发送回控制中心
    ch.basic_publish(exchange='',
                     routing_key=props.reply_to,
                     properties=pika.BasicProperties(correlation_id = props.correlation_id),
                     body=output_file.getvalue())
    #检查是否需要休眠
    if body['need_sleep']:
        sleep(sleep_time)
    ch.basic_ack(delivery_tag = method.delivery_tag)
    myprint('=========Complete Crawl=========')


def main():
    global sleep_time
    #载入cookie
    cookie_file_name='./cookies/cookie_'+str(sys.argv[1])
    install_cookie(cookie_file_name)
    #连接rabbitmq服务器
    connection = pika.BlockingConnection(pika.ConnectionParameters(
            host='localhost'))
    channel = connection.channel()
    sleep_time=5
    #定义队列
    channel.queue_declare(queue=settings.QUEUE_NAME)
    channel.basic_qos(prefetch_count=1)
    channel.basic_consume(on_request, queue=settings.QUEUE_NAME)

    channel.start_consuming()

if __name__ == '__main__':
    main()
