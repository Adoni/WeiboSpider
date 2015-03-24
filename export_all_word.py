#coding:utf8
from pymongo import Connection
from progressive.bar import Bar

db=Connection()
user_image=db.user_image
users=user_image.users

total_count=users.count()
finish_count=0
bar=Bar(max_value=total_count, fallback=True)
bar.cursor.clear_lines(2)
bar.cursor.save()
fout=open('./all_text.data','w')
for user in users.find():
    if len(user['statuses'])<100:
        continue
    for status in user['statuses']:
        status=' '.join(status['text'])+'\n'
        fout.write(status.encode('utf8'))
    finish_count+=1
    bar.cursor.restore()
    bar.draw(value=finish_count)
