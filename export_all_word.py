#coding:utf8
from pymongo import Connection

db=Connection()
user_image=db.user_image
users=user_image.users

fout=open('./all_text.data','w')
i=0
for user in users.find():
    print i
    i+=1
    for status in user['statuses']:
        if user['information']['gender']=='m':
            status=u'男'+' '+' '.join(status['text'])+'\n'
        else:
            status=u'女'+' '+' '.join(status['text'])+'\n'
        fout.write(status.encode('utf8'))
