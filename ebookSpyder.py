# -*- coding: utf-8 -*-
"""
Created on Wed Oct  4 12:11:22 2017
小说爬虫
@author: Ricardolcf
小说类爬虫的集合，这类网页的特征是需要提取的文本特别多，
特别是中文，解析却相对简单，涉及的js较少
**思路**：爬目录页，解析各章节链接，爬各章节，解析，保存到txt里
一个一个页面的爬虫有些慢呀
大部分的小说当然不是自己看啦，主要拿来练习爬虫和做文本分析用
"""
import requests
from bs4 import BeautifulSoup

def get_one_page(url):
    try:
        r=requests.get(url,timeout=30)
        r.raise_for_status()
        r.encoding=r.apparent_encoding
        return r.text
    except:
        print('get_one_page error')
        return None

def parse_ebook_page(response,fname):#解析单个章节页面
    #import re
    soup = BeautifulSoup(response, 'lxml')  
    s_c_text=soup.find_all('p')
    
    for sc in s_c_text:#
        fname.write(sc.string)
    
    #return wants 

def parse_dzz(resp):
    html=BeautifulSoup(resp, 'lxml')
    s_c_div=html.find('div',id="chaptercontent")
    print(s_c_div)
    #for s_br in s_c_div:##chaptercontent
        #print(s_br.string)


def parse_con(resp):
    #import re
    html=BeautifulSoup(resp, 'lxml')
    s_ol_text=html.find_all('ol',"clearfix")
    
    #print(type(s_ol_text))#<class 'bs4.element.ResultSet'>
    s_a_href=s_ol_text[1].find_all('a')
    fn=open('第十一根手指11.txt','a+',encoding="utf-8")
    for h in s_a_href:
        #可以选择装入列表，这里直接做解析了。
        #print(h.attrs['href'])
        print("爬取："+h.string)
        each_resp=get_one_page(h.attrs['href'])
        fn.write("\n\n========"+h.string+"=====\n")
        parse_ebook_page(each_resp,fn)
        
    fn.close()
    print("==end")


def save_one_url():
    url="http://www.136book.com/fayiqinmingdishiyigenshouzhi/fwbvql/"
    resp=get_one_page(url)
    with open("第十一根手指.txt",'a+',encoding="utf-8") as f:
        f.writelines(resp)
    print("save finish")

def readSXS():
    url="http://www.daizhuzai.com/1/4.html"
    resp=get_one_page(url)
    parse_dzz(resp)
    


def ebook_Spy():
    #整体爬虫
    urlc="http://www.136book.com/fayiqinmingdishiyigenshouzhi/"
    resp=get_one_page(urlc)
    parse_con(resp) #解析目录页
    #parse_ebook_page(resp)

            
readSXS()
#save_one_url()

#ebook_Spy()


'''
目前爬的有：136小说网：www.136book.com  特点是最新章节和全书目录标签相同，需要用find_all() 再取结果的[1]再find
www.daizhuzai.com 涉及比较多的js呀，直接爬取得到的是<br/>正在转码，请稍后......</div>
所以需要进一步学习再来爬
http://www.quanshuwang.com/book/44/44683/ 
请参考http://blog.csdn.net/dyboy2017/article/details/77884514



'''