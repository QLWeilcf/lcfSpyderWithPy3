#coding=UTF-8

import requests
from bs4 import BeautifulSoup
from lxml import etree

#获取单个页面
def getOneUrl(url):
    try:
        r=requests.get(url,timeout=30)
        r.raise_for_status()
        r.encoding=r.apparent_encoding
        return r.text
    except:
        return -1  #页面没正常下下来

def parseUkUrl(url): #uoko的爬虫
    text=getOneUrl(url)
    if text!=-1:
	    con=etree.HTML(text)
	    rel_comment=con.xpath('//*[@id="J_Reviews"]/div/div[6]/table/tbody/tr/td[1]/div[1]/div[1]')
	    for cn in rel_comment:
		    print(cn.text)

def honorComment():
	curl='https://rate.tmall.com/list_detail_rate.htm?itemId=565264660443&spuId=937776110&sellerId=1114511827&order=3&currentPage=2&append=0&content=1&tagId=&posi=&picture=&ua=098%23E1hv1pvWvRhvUvCkvvvvvjiPPFMw1jtPRLzWljljPmPptj3nn2shtjDWPszy0jrUiQhvChCvCCptvpvhphvvvvGCvvpvvPMMvphvCyCCvvvvvbyCvm3vpvvvvvCvphCv2v9vvhUuphvZ7pvvp6nvpCBXvvC2p6CvHHyvvhn2kphvCyEmmvo4euyCvv3vpvoEOyCxu9yCvh1m9WGvItttp7QEfwAK5FXX8Z0vQC4AVAIaUExrV4t%2BmB%2BiaNpXVcEJEcqvaXTrjLhDNr1l5dUf836AAnpfHkx%2FaoF6AEu4X9Wfbj7Q3QhvChCCvvmrvpvEphUz7vZvpmqA9phv2Hiw5gCTzHi47%2BKZzsyCvvBvpvvv&isg=BMDAu6VfjlH6RHG2aXAzbq1ZkU6YS7QZpGrr6DpRiFtqtWDf4ll0o5anyR11BVzr&needFold=0&_ksTS=1523715183450_710&callback=jsonp711'
	#c2='https://detail.tmall.com/item.htm?spm=a1z10.3-b-s.w4011-15291748836.63.418a6af4CjJ9NQ&id=565264660443&rn=09cbfdd9acb638b9e6aa4e9d568b2abe&abbucket=14&sku_properties=10004:653780895;5919063:6536025'
	print(getOneUrl(curl)) #异步加载js，json的处理之后再补上。
	parseUkUrl(curl)


honorComment()
