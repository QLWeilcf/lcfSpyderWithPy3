#coding=UTF-8

import requests
import json
import re

def getOneUrl(url):
	try:
		r = requests.get(url, timeout=30)
		r.raise_for_status()
		r.encoding = r.apparent_encoding
		return r.text
	except:
		return -1  # 页面没正常下下来

def getOverViewComment():#评论概览
	oc_url1="https://rate.tmall.com/listTagClouds.htm?" \
	       "itemId=565264660443&isAll=true&isInner=true&" \
	       "t=1525589708011&_ksTS=1525589708015_920&callback=jsonp921"
	oc_url = "https://rate.tmall.com/listTagClouds.htm?" \
	         "itemId=565264660443&isAll=true&isInner=true" #这也是可以的
	ovtxt=getOneUrl(oc_url)
	print(ovtxt)
	#jsonp921({"tags":{"dimenSum":8,…… loudList":""}})
	if ovtxt==-1:
		return
	#ov2=re.compile('\{.+\}').search(ovtxt) #json的部分

	ovc = json.loads('{'+ovtxt+'}')
	print(ovc["tags"]["rateSum"])
	for tc in ovc['tags']['tagClouds']:
		print(tc['tag'],tc)


def parseCommentJson(url, savep):  # 解析每个页面的json数据
	text = getOneUrl(url)
	if text == -1:
		print('页面没正常获取', url)
		return -1
	hc = json.loads(text.strip().strip('()'))  # 除掉空格和首尾括号
	if (hc['total'] == 0 or hc['comments'] == None):
		return 0

	print(hc['total'])

	with open(savep, 'a+', encoding='utf-8') as wf:
		for each_c in hc['comments']:
			wstr = '{name},{date},{ct},{sku}'.format(name=each_c['user']['nick'],
			                                         date=each_c['date'], ct=each_c['content'],
			                                         sku=each_c['auction']['sku'])

			aplst = each_c['appendList']
			addstr = ''
			if aplst != []:  # 有追评
				for adict in aplst:
					astr = ',{dac},{act}'.format(dac=str(adict['dayAfterConfirm']), act=adict['content'])
					addstr = addstr+astr

			wf.write(wstr+addstr+'\n')



def honorComment():
	for i in range(1,101):#结束页面可以自由改，如果要全量爬就设大一些,每个页面大概有20条 30115/20
		url='https://rate.taobao.com/feedRateList.htm?auctionNumId={cid}&' \
		    'currentPageNum={page}'.format(cid='565264660443',page=str(i))
		savep='D:/FFOutput/honor7cComment_{page}.csv'.format(page=str(i)) #直接page=i 也是可以的
		#page不迭代时，是写到同一个文件里，省得去合并了
		if (parseCommentJson(url,savep)==0):
			break

getOverViewComment()
#honorComment()


