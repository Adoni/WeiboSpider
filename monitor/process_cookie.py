import cPickle
import cookielib
import requests

def str2dict(cookie_str):
    cookie_str=cookie_str.replace(' ','')
    cookie_dict=dict()
    for c in cookie_str.split(';'):
        cookie_dict[c.split('=')[0]]=c.split('=')[1]
    return cookie_dict

def dump_cookieJar(file_name):
    cookies=cookielib.LWPCookieJar(file_name)
    cookies.load(ignore_discard=True, ignore_expires=True)
    cookie_dict=requests.utils.dict_from_cookiejar(cookies)
    cPickle.dump(cookie_dict,open(file_name,'wb'))

def dump_string_cookie(file_name):
    cookie_str=open(file_name).readlines()[0]
    cookie_str=cookie_str[7:]
    cookie_dict=str2dict(cookie_str)
    cPickle.dump(cookie_dict,open(file_name,'wb'))

def dump_batch_string_cookie(start,end):
    for i in range(start,end+1):
        file_name='./cookies/cookie_'+str(i)
        dump_string_cookie(file_name)

def dump_batch_cookieJar(start, end):
    for i in range(start, end+1):
        file_name='./cookies/cookie_'+str(i)
        dump_cookieJar(file_name)

def main():
    dump_batch_cookieJar(1,18)
if __name__=='__main__':
    main()
