
# coding: utf-8


# ## 4种匹配方式

# 用到bs4的定位**解析**方式有两种：
# -   requests+BeautifulSoup+select css选择器
# 
# ```python
# em = Soup.select('em[class="f14 l24"] a')
# for i in em:
#     pass
# ```
# -   requests+BeautifulSoup+find_all进行信息提取
# 
# ```python
# em = Soup.find_all('em', attrs={'class': 'f14 l24'})
# for i in em:
#     pass
# ```
# 而用lxml库的话：
# -  requests+lxml/etree+xpath表达式
# 
# ```python
# con = etree.HTML(html.text)
# 
# title = con.xpath('//em[@class="f14 l24"]/a/text()')
# link = con.xpath('//em[@class="f14 l24"]/a/@href')
# 
# for i in zip(title, link):
#     pass
# ```
# (使用lxml库下的etree模块进行解析，然后使用xpath表达式进行信息提取，效率要略高于BeautifulSoup+select方法)
# -  requests+lxml/html/fromstring+xpath表达式
# 
# ```python
# con = HTML.fromstring(requests.get(url = url, headers = headers).text)
# title = con.xpath('//em[@class="f14 l24"]/a/text()')
# link = con.xpath('//em[@class="f14 l24"]/a/@href')
# 
# for i in zip(title, link):
#     pass
# ```
# 
# 当然还可以用正则进行定位。
# 
# 
# ## 通用代码
# 
# 查找小区类的爬虫整体思路是：传入小区名称分析其页面的返回结果或者模糊匹配的结果/含有提示信息的结果。下面的代码大部分采用xpath进行定位。分析思路是先过滤掉返回url显示无搜索到小区的情况，再之后是对有小区的情况进行解析定位。

import requests
from bs4 import BeautifulSoup
from lxml import etree
#获取单个页面
def get_one_page(url):#基本获取网页数据的框架
    try:
        r=requests.get(url,timeout=30)
        r.raise_for_status()
        r.encoding=r.apparent_encoding
        return r.text
    except:
        return -1  #页面没正常下下来


# In[ ]:

import xlrd
import xlwt  

def parseXlex():
    fpath='D:/SpiderWorkZoom/hangzUokoIndexUn.xlsx'
    save_path='D:/SpiderWorkZoom/hangzUokoIndex_out.xls'
    ncol=4  #名称所在列，从0计数
    a3 = xlrd.open_workbook(fpath)
    a4 = a3.sheet_by_name("Sheet1")
    a5 = a4.col_values(0)
    a6 = len(a5)  #行数
    print(a6)
    workbook = xlwt.Workbook()
    sheet = workbook.add_sheet("Sheet1")
    sheet.write(0, 0, 'dankName')
    sheet.write(0, 1, 'uokoName')
    for i in range(1, a6):
        dankName = a4.cell(i,ncol).value  #cell里填行数和列数，列数从0开始数
        re_ss=parseInputDName(dankName.strip(' '))  #调用解析函数
        if i%500==0:  #输出部分结果
            print(i,dankName,re_ss)
        sheet.write(i, 0,dankName)
        sheet.write(i, 1, re_ss)
    workbook.save(save_path)
    print('done')



# ## 几个网站的爬虫

# *注：采用xpath解析*

def parseInputDName(nstr):
    urlHZ='http://hangzhou.uoko.com/room/_'+nstr 
    urlBJ='http://beijing.uoko.com/room/_'+nstr #备选其他城市的
    urlWH='http://wuhan.uoko.com/room/_'+nstr

    return parseUokoUrl(urlHZ) #继续调用

def parseUokoUrl(url): #uoko的爬虫
    text=getOneUrl(url)
    if text!=-1:
        con = etree.HTML(text)
        rel_not_have = con.xpath('//*[@id="page-main"]/div[4]/div/div[2]/div/text()[2]')
        #print(rel_not_have)
        if rel_not_have==[]:
            try:  # 用xpath的方式
                rel_s = con.xpath('//*[@id="page-main"]/div[4]/div/ul/li[1]/div[3]/div[1]/text()')
                return rel_s[0]
            except:
                return 'null'
        elif rel_not_have[0]=='抢光啦！换个搜索词试试~': #.text
            return '无'
        else:
            print('err at here')
            return 'err'
    else:
        return  'text==-1'


# In[ ]:

## 附录：获取uoko小区列表的所有小区
def getAllBlock(url=None):
    #url = 'http://hangzhou.uoko.com/room/by0pg1/'
    text = getOneUrl(url)
    if text != -1:
        con = etree.HTML(text)  #//*[@id="page-main"]/div[4]/div/ul/li[1]
        all_lst = con.xpath('//*[@id="page-main"]/div[4]/div/ul/li')
        #all_lst = con.xpath('//*[@id="page-main"]/div[4]/div/ul')

        print(type(all_lst))
        if all_lst == []:
            print('end 11')
            return '0'
        else:  #目前采用txt文本保存，后期可改为Excel
            f=open('./hangzhouUoko_out.txt','a+')
            k = len(all_lst)  # 北京： 21
            print(k)
            for i in range(1, k + 1):
                try:
                    w_li = con.xpath('//*[@id="page-main"]/div[4]/div/ul/li[' + str(i) + ']/div[3]/div[1]/text()')
                    #print(w_li[0])
                    f.write(w_li[0]+'\n')
                except:
                    print('err at li')
            f.close()
            print('done')
    else:

        print('err with text==-1')


def getAllTwo():
    u1='http://hangzhou.uoko.com/room/by0pg'

    for j in range(1,13): #这个13还是有些难自动化
        getAllBlock(u1+str(j))
 
#getAllTwo() #调用主函数

### qk


# qk的一种更好的解析方式：

def postToQK(a):
    url_sh='http://www.qk365.com//keywordsSearch.do'  #上海
    url_hz='http://hz.qk365.com//keywordsSearch.do'
    
    d1={"keyword":a}

    r=requests.post(url_sh,data=d1)
    return r.text

def parseQKdata(a):
    text=postToQK(a)
    if text=='':
        return ('null','1')
    else:
        con = etree.HTML(text)
        k=con.xpath('//li')
        k_len=len(k)
        for  i in range(k_len):
            type_i=con.xpath('//li['+str(i+1)+']/div[@class="jarrow"]')
            n_i=con.xpath('//li['+str(i+1)+']/div/a')
            if type_i[0].text=='小区':
                #n_text=n_i[0].text.strip(' ')
                n_text=re.compile(r'[\u4e00-\u9fa5]+').search(n_i[0].text)[0]
                if (n_text==a):
                    return (n_text,'1')
                else: #最好手动查
                    return (n_text,'0') #返回值不同的类型
        return ('无','2') #提示框无小区标签 原则上可以填 无
def getQKtest2():

    fpath='./sk_qk/qk_sh_15_20k.xlsx'
    save_path='./sk_qk/qk_sh_way2_out15_20k.xls'

    a3 = xlrd.open_workbook(fpath)
    a4 = a3.sheet_by_name("Sheet1")
    a5 = a4.col_values(0)
    a6 = len(a5)  #行数
    print(a6)
    workbook = xlwt.Workbook()
    sheet = workbook.add_sheet("Sheet1")
    sheet.write(0, 0, 'dankName')
    sheet.write(0, 1, 'qkName')
    sheet.write(0,2, 'qktype')
    for i in range(1,a6):
        s3=a4.cell(i,4).value
        dankName =str( s3)  #cell里填行数和列数，列数从0开始数
        re_ss,re_t=parseQKdata(dankName.strip(' '))

        sheet.write(i, 0,dankName)
        sheet.write(i, 1, re_ss)
        sheet.write(i, 2, re_t)
        if i<20:
            print(i,dankName,re_ss,re_t)
        
    workbook.save(save_path)


## zhuke  zkroom

def getZhuKeTest(url,nstr):
    #url='http://www.zkroom.com/home/room/index.html?keywords=寰宇天下'
    #nstr='寰宇天下'
    text=getOneUrl(url)
    if text!=-1:  #//*[@id="xqzf"]/div[2]/div/div[3]/div/div/em
        con = etree.HTML(text)
        rel_s = con.xpath('//*[@id="list"]/ul/li[1]/div[1]/div[2]')
        print(rel_s)
        if rel_s==[]:
            return '无' #对于有特殊符号的，需要手动查
        else:
            re_s=rel_s[0].text
            return compliTwoStr(re_s,nstr)

    else:
        print(nstr,'text==-1')
        return  'text==-1'


def compliTwoStr(a,b):
    #a:滨江区 西兴 寰宇天下 合租房 roomC
    #b:寰宇天下
    #a: 滨江区 西兴 寰宇天下 合租房 roomC
    #b:寰宇
    a_lst=a.split(' ')
    l_a=len(a_lst)
    if l_a>2:
        if b in a_lst[2]:
            return a_lst[2]
        elif b in a_lst[1]:
            return a_lst[1]
    else:
        return '0-长度不对-手动查'
    for c in a_lst:
        if c==b:
            return c
        else:
            print(a,a_lst,b)
            return '1-手动'

## haizhu 0409

def getHizhuT(url,nstr):
    #url='http://www.hizhu.com/Home/House/getsearchekey.html?city_code=001009001&keyword='
    #nstr='兆嘉园'
    d=getOneUrl(url+nstr)
    if d==-1:
        return 'text==-1'
    try:
        e=d.decode('utf-8')
        g=json.loads(e)
        d0=g['data']
        re_name='无'
        print(g)
        for dk in d0: #type(dk)==dict
            if dk['type_name']=='小区':
                if dk['estate_name'] == nstr:
                    return dk['estate_name']
                else:
                    re_name=praseHizhuStr(dk['estate_name'],nstr)
                    #return '000'
            else:
                pass
        return re_name
    except:
        print(nstr,d)
        return '0-手动'

def getHizhu(url,nstr):
    #url='http://www.hizhu.com/Home/House/getsearchekey.html?city_code=001009001&keyword='
    #nstr='兆嘉园'
    d=getOneUrl(url+nstr)
    if d==-1:
        return 'text==-1'
    try:
        e=d.decode('utf-8')
        g=json.loads(e)
        d0=g['data']
        if d0=='null':
            return 'data-null'
        #print(d0)
        re_name='无'
        for dk in d0: #type(dk)==dict
            if dk['type_name']=='小区':
                if dk['estate_name'] == nstr:
                    return dk['estate_name']
                else:
                    re_name=praseHizhuStr(dk['estate_name'],nstr)
                    #return '000'
            else:
                pass
        return re_name
    except:
        print(nstr,d)
        return '0-手动'

def getHizhu01(url,nstr):
    #url='http://www.hizhu.com/hangzhou/sqlist1/a0/b0/c0/d0/e0/fundefined/g0/h0/?key_self=2&key='
    #nstr='缤纷111'
    w='&search_id=11706d2d-bf6b-8d95-368c-600a57d068cf&type_no=0'
    text = getOneUrl(url + nstr+w  #id 是变化的，需要结合 getHizhuT使用
    if text != -1:
        con = etree.HTML(text)
        rel_s = con.xpath('/html/body/div[1]/div/div[4]/div[2]/ul/li[1]/div/div[1]/h3/a')
        if rel_s==[]:
            rel_s = con.xpath('/html/body/div[1]/div/div[4]/div[2]/ul/li[1]/div/div[1]/p[1]')
        if rel_s == []:
            rel_s = con.xpath('/html/body/div[1]/div/div[4]/div[2]/ul/li[1]/div/div[1]/h3/a')
        if rel_s==[]:
            print(nstr)
            return '1-00'
        print(rel_s)
        re_s = rel_s[0].text
        #print(re_s)
        ewlst = re.split(' · ',re_s)
        w_len=len(ewlst)
        if w_len==1:
            ewlst = re.split('\xa0·\xa0', re_s)
            w_len = len(ewlst)
            if w_len==1:
                print(ew_s,ewlst)
                return '1-111'

        re_name='无'
        for w in ewlst:
            if w==nstr:
                return w
            elif nstr in w:
                return w

        return re_name


    else:
        return 'text==-1'
### *上面haizhu那个是还不够完备的，值得优化                     
                



# 对一些公寓租赁网站的爬虫。

