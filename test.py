from helper import load_headers
import urllib2
h=load_headers()
url='http://weibo.com/u/1883388073'
request = urllib2.Request(url=url, headers=h['UserStatus'])
response = urllib2.urlopen(request)
the_page = response.read()
print the_page
