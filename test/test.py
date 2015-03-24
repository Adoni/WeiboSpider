import requests
import urllib
url='http://stu.baidu.com/i'
objurl='http://img1.imgtn.bdimg.com/it/u=3505033395,3076547582&fm=11&gp=0.jpg'
objurl=urllib.quote_plus(objurl)
print objurl
data={
    'objurl':objurl,
    'filename':'',
    'rt':0,
    'rn':10,
    'ftn':'searchstu',
    'ct':1,
    'stt':1,
    'tn':'faceresult'
}
r=requests.get(url=url,params=data)
