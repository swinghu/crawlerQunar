#! /usr/bin/env python
# -*- coding=utf-8 -*-

from sys import argv

import urllib2
import json
import time
import requests
import pymongo

#connect mydb in MongoDB  
from pymongo import MongoClient
client = MongoClient()
db = client['mydb']
tourcoll = db.tour


#get the start city number in st_c list
s = int(argv[1]) 
#get the end city number in ec_c list
e = int(argv[2]) 

#all main cities on qunar.com
st_c = [u'北京',u'上海',u'广州',u'深圳',u'香港',u'长沙',u'宁波',u'沈阳',u'重庆',u'乌鲁木齐',u'石家庄',u'郑州',u'天津',u'昆明',u'厦门',u'太原',u'无锡',u'兰州',u'苏州',u'常州',u'武汉',u'青岛',u'大连',u'南京',u'张家界',u'贵阳',u'杭州',u'桂林',u'温州',u'南宁',u'三亚',u'南昌',u'成都',u'福州',u'哈尔滨',u'西安',u'济南',u'合肥']

ed_c = [u'三亚',u'海口',u'蜈支洲岛',u'阳朔',u'漓江',u'桂林',u'北海',u'涠洲岛',u'广州',u'深圳',u'上海',u'杭州',u'苏州',u'厦门',u'鼓浪屿',u'青岛',u'武夷山',u'张家界',u'凤凰',u'乌镇',u'绍兴',u'黄山',u'普陀山',u'三清山',u'婺源',u'山东',u'泰山',u'安徽',u'江苏',u'浙江',u'江西',u'九寨沟',u'峨眉山',u'成都',u'重庆',u'昆明',u'丽江',u'西双版纳',u'迪庆',u'大理',u'束河古镇',u'林芝',u'拉萨',u'四川',u'云南',u'西藏',u'西安',u'华山',u'延安',u'敦煌莫高窟',u'青海湖',u'喀纳斯',u'乌鲁木齐',u'银川',u'陕西',u'甘肃',u'宁夏',u'新疆',u'青海',u'北京',u'天津',u'呼伦贝尔',u'五台山',u'平遥',u'太原',u'壶口瀑布',u'大同',u'山西',u'云台山',u'洛阳',u'开封',u'张家界',u'衡山',u'凤凰',u'河南',u'武当山',u'三峡大坝旅游区',u'宜昌',u'重庆',u'湖北',u'黑龙江',u'吉林',u'辽宁',u'哈尔滨',u'亚布力',u'太阳岛',u'镜泊湖',u'沈阳',u'大连',u'长白山']

#encode city name in st_c/ed_c into url code
sc = urllib2.quote(st_c[s].encode("utf8"))
ec = urllib2.quote(ed_c[e].encode("utf8"))

#construct http header
http_refer = 'http://dujia.qunar.com/pdq/list_' + sc + '_' + ec + '?tm=gn02'
req_header = {'User-Agent':'Mozilla/5.0 (X11; Linux i686) AppleWebKit/537.22 (KHTML, like Gecko) Chrome/25.0.1364.172 Safari/537.22',
              'Accept':'application/json, text/javascript, */*',
              'Accept-Charset':'ISO-8859-1,utf-8;q=0.7,*;q=0.3',
              'Accept-Encoding':'gzip,deflate,sdch',
              'Host':'dujia.qunar.com',
              'Connection':'close',
              'Referer':http_refer,
              'X-Requested-With':'XMLHttpRequest'
              }
req_timeout = 5


#get total page number, give up the last page which doesn't have 20 records
#construct url for first page of two cities
sp_a = 'http://dujia.qunar.com/p/listapi?action=filter&obpop=desc&tm=gn02&dep='
sp_b = '&query='
sp = sp_a + sc + sp_b + ec
#fetch the data of the first page of two cities
req_p = urllib2.Request(sp,None,req_header)
sp_json = urllib2.urlopen(req_p,None,req_timeout)
sp_json_c = sp_json.read()
#load the data into json format
sp_json_j = json.loads(sp_json_c)
#get total page number from object 'all' in the json file(20 records in every page)
total_page = sp_json_j['data']['types']['all']/20
print "There are totally %d pages\n " % total_page

#get all records of two cities according to page number
for page_num in range(total_page):
    #construct url for data file of everypage of two cities
    se_a = 'http://dujia.qunar.com/p/listapi?action=routeResult&tm=gn02&obpop=desc&toprecommend=0&dep='
    se_b = '&query='
    se_c = '&pageNo='
    page_num_s = str(page_num + 1)
    se = se_a + sc +se_b + ec + se_c + page_num_s

    #fetch the data stream according to the url above
    r = requests.post(se, stream=True)
    r_get = ''
    for line in r.iter_lines():
        if line:
            r_get = r_get + line

    #load the data into json format
    r_get_dic = json.loads(r_get)

    #store the data into MogoDb
    r_get_dic['startcity'] = st_c[s]
    r_get_dic['endcity'] = ed_c[e]
    tourlistId = tourcoll.insert(r_get_dic)

    #print out the number of the fetched page 
    print "Page %d successfully stroed at mydb-tour-id = %s\n" % (page_num, tourlistId)

    #sleep 2 second after fetch one page
    time.sleep(2)
