#coding=utf-8
import json
import time
import urllib
class tester:
    access_token='2.00Ji6SNDlxpd6Ce469dd9f28qaqaTC'
    sleeptime=5
    all_users=set()
    user_to_parse=[]
    TOTAL=0
    FRIEND_PER_USER=0
    #fout=open('./all.data','a')
    def __init__(self):
        print('start')
        for l in open('./all.data').readlines()[-1000:-1]:
            l=l[0:-1]
            self.all_users.add(l)
        for uid in self.all_users:
            self.user_to_parse.append(uid)
        self.TOTAL=int(raw_input('请输入需要爬取的总量：'))
        self.FRIEND_PER_USER=int(raw_input('请输入每个用户需要爬取的朋友数：'))

    #This function is used to get the user text
    def get_friends(self, uid):
        base_url='https://api.weibo.com/2/friendships/friends.json'
        complete_url = base_url + '?' + 'uid=' + uid + '&access_token=' + self.access_token + '&count=' + str(self.FRIEND_PER_USER)
        try:
            raw_json = urllib.urlopen(complete_url).read().decode('utf8')
        except Exception as e:
            print('Error:')
            print(e)
            print ('exception!\n' + complete_url)
            time.sleep(self.sleeptime)
            try:
                raw_json = urllib.urlopen(complete_url).read().decode('utf8')
            except:
                print ('shit!!!!')
                return
        try:
            json_data = json.loads(raw_json)
        except:
            print(complete_url)
            return
        try:
            for user in json_data["users"]:
                fid=user['id']
                if(not fid in self.all_users):
                    self.fout.write(str(fid)+'\n')
                    #self.fout.close()
                    #self.fout=open('total.txt','a')
                    self.user_to_parse.append(fid)
                self.all_users.add(fid)
        except Exception as e:
            print(complete_url)
            print(e)
            return

    def get_all(self):
        while(len(self.all_users)<self.TOTAL and len(self.user_to_parse)>0):
            self.get_friends(self.user_to_parse[0])
            self.user_to_parse=self.user_to_parse[1:]
            print(str(len(self.all_users))+'/'+str(self.TOTAL))

        print('Total count: '+str(len(self.all_users)))

a=tester()
a.get_all()
