#coding=utf-8

import requests
from lxml import etree
import re

# 智联招聘上的企业名录爬虫；
#*城市和行业可定制，下面代码只获取了本人需要的信息*

#获取单个页面
def getOneUrl(url):
    try:
        r=requests.get(url,timeout=30)
        r.raise_for_status()
        r.encoding=r.apparent_encoding
        return r.text
    except:
        return -1  #页面没正常下下来

## companySpider
# *at zhilian.com*

tlst=['互联网','金融','文化']

def industrySpider(t="金融"): #主程序，目前只配置了3个行业的页面，其他页面请按需配置
	industry={"互联网":"http://company.zhaopin.com/beijing/210500/p","基金":"http://company.zhaopin.com/beijing/180000/p","文化传播":"http://company.zhaopin.com/beijing/2103003/p"}
	#210500 互联网;2105001 电子商务;160500 电子技术;1605001 半导体;1605002 集成电路;160400 计算机软件
	#300500 银行;180000 基金;1800001 证券;1800002 期货;1800003 投资
	#210300 媒体; 2103001 出版;  2103002 影视; 2103003 文化传播
	page=[[i,i+19] for i in range(1,51,20)] #[[1, 20], [21, 41]……] 因为循环时不取停用词，所以注意20和21的区别

	if t=="互联网":
		savep = './zhiliancompanylist/互联网页面下载'
		for k in page:
			parseCompanyzl(industry['互联网'], k, savep)
	elif t=="金融":
		savep = './zhiliancompanylist/金融页面下载'
		for k in page:
			parseCompanyzl(industry['基金'], k, savep)
	elif t=="文化":
		savep = './zhiliancompanylist/文化页面下载'
		for k in page:
			parseCompanyzl(industry['文化传播'], k, savep)
	else:
		print(t)


# **下面基本全部用xpath进行解析**，其他方式解析基本都可以用xpath实现，为了一致性只用一种。

## 获取所有行业
def getZlAllIndustryUrl():
	url = "http://company.zhaopin.com/beijing/210500/"
	t1=getOneUrl(url)
	if t1 != -1:
		try:
			con = etree.HTML(t1)
			rel_comment = con.xpath('//*[@id="industry"]/a') 
			for slst in rel_comment:
				a1 = slst.xpath('@href')[0]
				a2=slst.xpath('text()')[0]
				print(a1,a2)
		except Exception as exp:
			print(exp,'err at getZlAllIndustryUrl')

# 获取一个页面的所有公司列表；
#调用praseOneCompanysUrl(url)获取每个公司对应的地址和坐标
#（某种角度上说也是一个Geo项目）
def parseCompanyzl(url,rangelst,savep):
	all_compy=[]
	for i in range(rangelst[0],rangelst[1]+1):
		text=getOneUrl(url+str(i))
		if text!=-1:
			try:
				con = etree.HTML(text)
				rel_comment = con.xpath('/html/body/div[4]/div[1]/div[2]/form/div[1]/div[2]/ul/li/div')
				for slst in rel_comment:
					res_lst=['','','','','','','',''] # 坐标为火星坐标系-->高德地图
					#[0名称,1经度,2纬度,3公司地址,4人数,5url,6类别,7分类标签]
					res_lst[4] = slst.xpath('span[1]/text()')[0]  # 公司人数
					if praseTextPeo(res_lst[4])<400: #人数少于阈值就不记录了；
						continue

					res_lst[5]=slst.xpath('div[1]/a/@href')[0] #company url
					coorlst = praseOneCompanysUrl(res_lst[5])
					if len(coorlst)==2:
						res_lst[1], res_lst[2] =coorlst[0],coorlst[1]
					elif len(coorlst)==3:
						res_lst[1], res_lst[2],res_lst[3]= coorlst[0], coorlst[1],coorlst[2]
					else:
						print(coorlst,'i=',res_lst[5])
					res_lst[0] = slst.xpath('div[1]/a/text()')[0]  # company name
					res_lst[6] = slst.xpath('h3/a/text()')[0]  # company type eg:民营

					res_lst[7] = slst.xpath('span[2]/text()')[0]  # 公司分类
					#print(res_lst)
					all_compy.append(res_lst)
				print(i,all_compy[-1]) #单纯输出来看看
				#break
			except IndexError: #上面的continue可能会引发这个错误，当是最后一个元素还进入了continue语句时；
				#print(i,url,res_lst)
				pass
			except Exception as exp:
				if endPagePrase(text,i):
					lstWriteToCsv(all_compy,savep+'_'+str(rangelst[0])+'_'+str(i)+'.csv', 'a+')
					rangelst[1]=i
					print('end at:',i)
					return #不用 break,否则就改上面的保存页面
				print(exp,'err at parseCompanyzl()')
				print(i,url)
				print(res_lst)
				a34= slst.xpath('div[1]/a/text()')
				a35=a34[0]
				lstWriteToCsv(all_compy,'D:/outLog2018.csv', 'a+')
		else:
			print(url+str(i))
	spath=savep+'_'+str(rangelst[0])+'_'+str(rangelst[1])+'.csv'
	lstWriteToCsv(all_compy, spath,'w+')
	print('save at',spath)

def praseOneCompanysUrl(url): #解析公司对应的url页面，获取坐标和分类

	if url==None:
		return [''] #err
	if url == '':
		return ['']
	text=getOneUrl(url)
	if text!=-1:
		#可对公司类型作进一步限定，那些经营范围很广的，要求人数够多，加上手工判断
		try:
			c1 = etree.HTML(text)
			rel_c = c1.xpath('/html/body/div[2]/div[1]/div[1]/table/tr[5]/td[2]/button/@onclick')
			r_adds=c1.xpath('/html/body/div[2]/div[1]/div[1]/table/tr[5]/td[2]/span/text()')
			if rel_c ==[]:#有公司网站是5，否则是4
				rel_c=c1.xpath('/html/body/div[2]/div[1]/div[1]/table/tr[4]/td[2]/button/@onclick')
				r_adds = c1.xpath('/html/body/div[2]/div[1]/div[1]/table/tr[4]/td[2]/span/text()')
				r_adds=['无'] if r_adds==[] else r_adds
			if rel_c==[]: #这种情况懒得要地址了
				if 'index.html' in url:
					rel_c=c1.xpath('//*[@id="contact"]/a[1]/@href')
					if rel_c==[]:
						rel_c=c1.xpath('//*[@id="contactMap"]/@href')
			if rel_c==[]:
				#print('url at praseOneCompanysUrl',url)
				return ['无1','无1','无1']
			#tbody 并不能识别，这个可以加到xpath学习笔记里
			coor=re.compile('(-?\d+)\.?\d*')
			w0=rel_c[0] #可能会出现结果为-1的情况
			w1=re.compile('\(.+\)').search(w0)[0]
			w2=w1.split(',')
			cs2=coor.search(w2[-1])
			cs3=coor.search(w2[-2])
			try:
				cs4=str(r_adds[0],encoding='gbk')
			except:
				cs4=str(r_adds[0])
			if cs2==None and cs3==None: #不用or
				return ['00']
			return [cs2[0],cs3[0],cs4]

		except Exception as e2:
			print(e2,';err at praseOneCompanysUrl()',url)
			return ['无','无','无']
	return ['无3','无3','无3']

def praseTextPeo(itxt): #解析人数
	#输入例如：100-499人 还会有：20人以下
	# 返回一个数字，或者改为返回True or False
	if itxt=='':
		return 0
	n_c=re.compile('\d+')
	lst=n_c.findall(itxt)
	if lst==[]:
		print('err at praseTextPeo',itxt)
		return 10000
	return int(lst[-1])

def endPagePrase(text,i): #页面结束标识
	try:
		con = etree.HTML(text)
		rel_comment = con.xpath('/html/body/div[2]/div[1]/h1/text()')
		if rel_comment[0]=="对不起，您要访问的页面暂时没有找到":
			return True
		else:
			return False
	except Exception as e:
		print(e,'err at endPagePrase()')
		return False

#二维数组写为csv
def lstWriteToCsv(twodLst,spath,writeType='a+'):
	try:
		with open(spath,writeType) as f:
			for elst in twodLst:
				#['cname','2','3','4','5']
				one_record=','.join(elst)
				f.write(one_record+'\n')
	except Exception as e:
		print(e)
		print(one_record)
		try:
			with open(spath+'1.csv', writeType,encoding='UTF-8') as f:
				for elst in twodLst:
					# ['cname','2','3','4','5']
					one_record = ','.join(elst)
					f.write(one_record + '\n')
		except Exception as exp: #为了不影响for循环的运行
			print(exp)

#print(praseOneCompanysUrl('http://special.zhaopin.com/pagepublish/42876252/index.html'))
#parseCompanyzl()

#getZlAllIndustryUrl()
industrySpider()






