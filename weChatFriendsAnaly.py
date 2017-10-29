# -*- coding: utf-8 -*-
"""
Created on 2017/03/08

@author: Ricardolcf
"""
'''
模拟登录微信，并爬取一些数据；对数据进行分析和可视化
'''
import os
import requests
import re
import time
import xml.dom.minidom
import json
import sys
import ssl
import threading
import urllib

DEBUG = False

MAX_GROUP_NUM = 2  # 每组人数
INTERFACE_CALLING_INTERVAL = 5  # 接口调用时间间隔, 间隔太短容易出现"操作太频繁", 会被限制操作半小时左右
MAX_PROGRESS_LEN = 50

QRImagePath = os.path.join(os.getcwd(), 'qrcode.jpg')

tip = 0
uuid = ''

base_uri = ''
redirect_uri = ''
push_uri = ''

skey = ''
wxsid = ''
wxuin = ''
pass_ticket = ''
deviceId = 'e000000000000000'

BaseRequest = {}

ContactList = []
My = []
SyncKey = []

try: #通配py2
    xrange
    range = xrange
except:
    # python 3
    pass

#登录获取数据的主函数
def mainWeChat():
    global myRequests
    
    if hasattr(ssl, '_create_unverified_context'):
        ssl._create_default_https_context = ssl._create_unverified_context

    headers = {'User-agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_2) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/44.0.2403.125 Safari/537.36'}
    myRequests = requests.Session()
    myRequests.headers.update(headers)

    if not getUUID():
        print('获取uuid失败')
        return

    print('正在获取二维码图片...')
    showQRImage()#也可以用pygame库打开图片


    while waitForLogin() != '200':
        pass

    os.remove(QRImagePath)

    if not login():
        print('登录失败')
        return

    if not webwxinit():
        print('初始化失败')
        return

    MemberList,NumM,pubNum,speUsers,groupChat= webwxgetcontact()
    #爬下来的数据
    threading.Thread(target=heartBeatLoop)#这里用到多线程

    MemberCount = len(MemberList)
    print('通讯录共%s位好友' % MemberCount)
    print('总共：',NumM)
    print('公众号：',pubNum)
    print('特殊账号数：',speUsers)
    print('群聊数：',groupChat)
    #print(type(MemberList)) #list
   
    try:
        with open('D:/python_works/GeoData/myWeChatJson2017391836.txt','a+',encoding='utf-8') as f:
            f.write(str(MemberList))
        
    except:
        print('not save MemberList')
    countMemberData(MemberList) #分类保存数据
    print('end main code')

def countMemberData(memberList):
    d = {}
    li=[]
    cityList=[]
    #mindex=0
    for Member in memberList:
        #li.append([])
        d[Member['UserName']] = (Member['NickName'], Member['RemarkName'])
        city = Member['City']
        city = 'noCity' if city == '' else  city
        province = Member['Province']
        province = 'noProvince' if province == '' else  province
        name = Member['NickName']#名称，也是昵称
        name = 'notName' if name == '' else  name
        sign = Member['Signature']#签名
        sign = 'notSign' if sign == '' else  sign
        remark = Member['RemarkName']#备注
        remark = 'notRemark' if remark == '' else remark
        alias = Member['Alias']#星标好友
        alias = 'notAlias' if alias == '' else alias
        #nick = Member['NickName']#昵称
        #nick = 'nonickname' if nick == '' else nick
        wriStr=name+','+remark+','+province+','+city+','+judgeSex(Member['Sex'])+','+str(Member['StarFriend'])+','+sign+','+alias+','+'\n'
        clst=[city,province]
        cityList.append(clst)
        #li[mindex].append(wriStr)
        li.append(wriStr)
        #mindex+=1
        
    #写入csv文件
    savePath='D:/python_works/GeoData/myWeChat2017391836.csv'
    with open(savePath,'a+') as fw:
        #fw.write()
        for i in li:
            fw.write(i)
            #fw.write(i.encode('utf-8'))
    
    saveCityData(cityList)
    print("数据保存结束！")

def saveCityData(cityList):
    sPath='D:/python_works/GeoData/myWeChatCity20171029.csv'
    with open(sPath,'a+') as fcity:
        for c in cityList:
            fcity.write(c[0]+','+c[1]+'\n')
    
    
    
def saveAllJson(mList):
    sPath=""
    
    
    

def downloadImg(mList,name=""):#输入MemberList和保存图片目录
    imageIndex = 0
    for Member in mList:
        imageIndex +=1
        if name=="":
            name = os.getcwd() + '/friendImage/Image2/' + str(imageIndex) + '.jpg'
        
        #下载头像部分 找不到问题出在哪里
        imageUrl = 'https://wx.qq.com'+Member['HeadImgUrl']
        r = myRequests.get(url=imageUrl,headers=headers)
        imageContent = (r.content)
        fileImage = open(name,'wb+')
        fileImage.write(imageContent)
        fileImage.close()#写入图片--头像
        with open(name,'wb+') as fim:
            fim.write(imageContent)
        #print('正在下载第'+str(imageIndex)+'位好友的头像\t')
        
    print("头像下载完毕")

def responseState(func, BaseResponse):
    ErrMsg = BaseResponse['ErrMsg']
    Ret = BaseResponse['Ret']
    if DEBUG or Ret != 0:
        print('func: %s, Ret: %d, ErrMsg: %s' % (func, Ret, ErrMsg))

    if Ret != 0:
        return False

    return True

def getUUID():
    global uuid

    url = 'https://login.weixin.qq.com/jslogin'
    params = {
        'appid': 'wx782c26e4c19acffb',
        'fun': 'new',
        'lang': 'zh_CN',
        '_': int(time.time()),
    }

    r= myRequests.get(url=url, params=params)
    r.encoding = 'utf-8'
    data = r.text

    # print(data)

    # window.QRLogin.code = 200; window.QRLogin.uuid = "oZwt_bFfRg==";
    regx = r'window.QRLogin.code = (\d+); window.QRLogin.uuid = "(\S+?)"'
    pm = re.search(regx, data)

    code = pm.group(1)
    uuid = pm.group(2)

    if code == '200':
        return True

    return False

def saveQRImage():
    global tip

    url = 'https://login.weixin.qq.com/qrcode/' + uuid
    params = {
        't': 'webwx',
        '_': int(time.time()),
    }

    r = myRequests.get(url=url, params=params)

    tip = 1

    f = open(QRImagePath, 'wb')
    f.write(r.content)
    f.close()
    print('扫码登录\n请手动扫码')
    time.sleep(5)

def showQRImage():
    global tip

    url = 'https://login.weixin.qq.com/qrcode/' + uuid
    params = {
        't': 'webwx',
        '_': int(time.time()),
    }

    r = myRequests.get(url=url, params=params)

    tip = 1
    f = open(QRImagePath, 'wb')
    f.write(r.content)
    f.close()

    from PIL import Image
    img = Image.open(QRImagePath, 'r')
    img.show()
    print('请使用微信扫描二维码以登录')


def waitForLogin():
    global tip, base_uri, redirect_uri, push_uri

    url = 'https://login.weixin.qq.com/cgi-bin/mmwebwx-bin/login?tip=%s&uuid=%s&_=%s' % (
        tip, uuid, int(time.time()))

    r = myRequests.get(url=url)
    r.encoding = 'utf-8'
    data = r.text

    # print(data)

    # window.code=500;
    regx = r'window.code=(\d+);'
    pm = re.search(regx, data)

    code = pm.group(1)

    if code == '201':  # 已扫描
        print('成功扫描,请在手机上点击确认以登录')
        tip = 0
    elif code == '200':  # 已登录
        print('正在登录...')
        regx = r'window.redirect_uri="(\S+?)";'
        pm = re.search(regx, data)
        redirect_uri = pm.group(1) + '&fun=new'
        base_uri = redirect_uri[:redirect_uri.rfind('/')]

        # push_uri与base_uri对应关系(排名分先后)(就是这么奇葩..)
        services = [
            ('wx2.qq.com', 'webpush2.weixin.qq.com'),
            ('qq.com', 'webpush.weixin.qq.com'),
            ('web1.wechat.com', 'webpush1.wechat.com'),
            ('web2.wechat.com', 'webpush2.wechat.com'),
            ('wechat.com', 'webpush.wechat.com'),
            ('web1.wechatapp.com', 'webpush1.wechatapp.com'),
        ]
        push_uri = base_uri
        for (searchUrl, pushUrl) in services:
            if base_uri.find(searchUrl) >= 0:
                push_uri = 'https://%s/cgi-bin/mmwebwx-bin' % pushUrl
                break

        # closeQRImage
        if sys.platform.find('darwin') >= 0:  # for OSX with Preview
            os.system("osascript -e 'quit app \"Preview\"'")
    elif code == '408':  # 超时
        pass
    # elif code == '400' or code == '500':

    return code

def login():
    global skey, wxsid, wxuin, pass_ticket, BaseRequest

    r = myRequests.get(url=redirect_uri)
    r.encoding = 'utf-8'
    data = r.text
    # print(data)

    doc = xml.dom.minidom.parseString(data)
    root = doc.documentElement

    for node in root.childNodes:
        if node.nodeName == 'skey':
            skey = node.childNodes[0].data
        elif node.nodeName == 'wxsid':
            wxsid = node.childNodes[0].data
        elif node.nodeName == 'wxuin':
            wxuin = node.childNodes[0].data
        elif node.nodeName == 'pass_ticket':
            pass_ticket = node.childNodes[0].data

    # print('skey: %s, wxsid: %s, wxuin: %s, pass_ticket: %s' % (skey, wxsid,
    # wxuin, pass_ticket))

    if not all((skey, wxsid, wxuin, pass_ticket)):
        return False

    BaseRequest = {
        'Uin': int(wxuin),
        'Sid': wxsid,
        'Skey': skey,
        'DeviceID': deviceId,
    }

    return True


    

#初始化部分
def webwxinit():

    url = (base_uri + 
        '/webwxinit?pass_ticket=%s&skey=%s&r=%s' % (
            pass_ticket, skey, int(time.time())) )
    params  = {'BaseRequest': BaseRequest }
    headers = {'content-type': 'application/json; charset=UTF-8'}

    r = myRequests.post(url=url, data=json.dumps(params),headers=headers)
    r.encoding = 'utf-8'
    data = r.json()

    if DEBUG:
        f = open(os.path.join(os.getcwd(), 'webwxinit.json'), 'wb')
        f.write(r.content)
        f.close()


    # print(data)

    global ContactList, My, SyncKey
    dic = data
    ContactList = dic['ContactList']
    My = dic['User']
    SyncKey = dic['SyncKey']

    state = responseState('webwxinit', dic['BaseResponse'])
    return state

def webwxgetcontact():

    url = (base_uri + 
        '/webwxgetcontact?pass_ticket=%s&skey=%s&r=%s' % (
            pass_ticket, skey, int(time.time())) )
    headers = {'content-type': 'application/json; charset=UTF-8'}

    r = myRequests.post(url=url,headers=headers)
    r.encoding = 'utf-8'
    data = r.json()

    if DEBUG:
        f = open(os.path.join(os.getcwd(), 'webwxgetcontact.json'), 'wb')
        f.write(r.content)
        f.close()


    dic = data
    MemberList = dic['MemberList']#记录通讯录好友数

    # 倒序遍历,不然删除的时候出问题..
    SpecialUsers = ["newsapp", "fmessage", "filehelper", "weibo", "qqmail", "tmessage", "qmessage", "qqsync", "floatbottle", "lbsapp", "shakeapp", "medianote", "qqfriend", "readerapp", "blogapp", "facebookapp", "masssendapp",
                    "meishiapp", "feedsapp", "voip", "blogappweixin", "weixin", "brandsessionholder", "weixinreminder", "wxid_novlwrv3lqwv11", "gh_22b87fa7cb3c", "officialaccounts", "notification_messages", "wxitil", "userexperience_alarm"]
    NumM=len(MemberList)#总共数目
    pubNum=0 #公众号/服务号
    speUsers=0 #特殊账号
    groupChat=0 #群聊,它只会记录你保存的群聊数
    for i in range(NumM- 1, -1, -1):
        Member = MemberList[i]
        if Member['VerifyFlag'] & 8 != 0:  # 公众号/服务号
            MemberList.remove(Member)
            pubNum+=1
        elif Member['UserName'] in SpecialUsers:  # 特殊账号
            MemberList.remove(Member)
            speUsers+=1
        elif Member['UserName'].find('@@') != -1:  # 群聊
            MemberList.remove(Member)
            groupChat+=1
        elif Member['UserName'] == My['UserName']:  # 自己
            MemberList.remove(Member)

    return MemberList,NumM,pubNum,speUsers,groupChat

def syncKey():
    SyncKeyItems = ['%s_%s' % (item['Key'], item['Val'])
                    for item in SyncKey['List']]
    SyncKeyStr = '|'.join(SyncKeyItems)
    return SyncKeyStr

def syncCheck():
    url = push_uri + '/synccheck?'
    params = {
        'skey': BaseRequest['Skey'],
        'sid': BaseRequest['Sid'],
        'uin': BaseRequest['Uin'],
        'deviceId': BaseRequest['DeviceID'],
        'synckey': syncKey(),
        'r': int(time.time()),
    }

    r = myRequests.get(url=url,params=params)
    r.encoding = 'utf-8'
    data = r.text

    # print(data)

    # window.synccheck={retcode:"0",selector:"2"}
    regx = r'window.synccheck={retcode:"(\d+)",selector:"(\d+)"}'
    pm = re.search(regx, data)

    retcode = pm.group(1)
    selector = pm.group(2)

    return selector

def webwxsync():
    global SyncKey

    url = base_uri + '/webwxsync?lang=zh_CN&skey=%s&sid=%s&pass_ticket=%s' % (
        BaseRequest['Skey'], BaseRequest['Sid'], urllib.quote_plus(pass_ticket))
    params = {
        'BaseRequest': BaseRequest,
        'SyncKey': SyncKey,
        'rr': ~int(time.time()),
    }
    headers = {'content-type': 'application/json; charset=UTF-8'}

    r = myRequests.post(url=url, data=json.dumps(params))
    r.encoding = 'utf-8'
    data = r.json()

    # print(data)

    dic = data
    SyncKey = dic['SyncKey']

    state = responseState('webwxsync', dic['BaseResponse'])
    return state

def heartBeatLoop():
    while True:
        selector = syncCheck()
        if selector != '0':
            webwxsync()
        time.sleep(1)

def judgeSex(a):#格式化性别，输入为0、1、2
    if a==1:
        return '男'
    elif a==2:
        return '女'
    else:
        return 'unclear'



def analCity():#分析城市-省份
    import csv
    from collections import OrderedDict
    ds=OrderedDict()
    filename='D:\python_works\别人优秀的项目\\friendImage\微信数据20173800251.csv'
    reader = csv.reader(open(filename))
    for liu in reader:
        la=liu[2]
        ds[la]=(ds[la]+1) if (la in ds) else (1)
    for a,b in ds.items():
        print(a,',',b)

    #return ds

if __name__ == '__main__':

    mainWeChat()
    #analCity()
    


'''
参考：
'''