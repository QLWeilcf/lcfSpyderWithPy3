## 功能

模拟登录微信，并爬取一些数据；对数据进行分析和可视化


## 具体说明

1，模拟登录微信，并且爬取一些数据：昵称、微信号、城市、性别、是否星标好友、头像、个性签名、备注


2，统计：2.1性别统计饼状图；2.2好友地区分布(结合地图汇或者自己用PPT做，ArcGIS太用牛刀了)
2.3 备注+昵称：大致统计认识的好友比例
2.4 头像：人脸识别。结合openCV API 可以统计出有多少人用了人脸做头像。
2.5 其他拓展：以后有对微信相关操作的需求时可以从这个文件中选择函数




## 参考资料

-------------------
代码在：

更新于Git的代码为：weChatFriendsAnaly
将代码与大量备注分开了，主要的备注在这个readme里。

后记：（不打算同步到Git上的：）
#------
1.1 爬虫爬下来的json数据：(字典形式)
{'MemberList': [],--？
'SnsFlag': 17,--？
'IsOwner': 0,--？
'HideInputBarFlag': 0,
'ContactFlag': 3,--？
'City': '海淀',--城市
'Province': '北京',--省份
'Uin': 0,
'RemarkName': '***',--备注
'RemarkPYQuanPin': 'dua***anyi',--备注全拼，不包括符号
'RemarkPYInitial': 'D*KYY',--备注拼音大写，没什么用的项
'NickName': '*',--昵称
'PYQuanPin': '*',--昵称全拼
'PYInitial': '*',--昵称拼音首字母大写
'KeyWord': '',--？
'DisplayName': '',--？
'Sex': 1,--性别
'EncryChatRoomId': '',--？
'Signature': '******',--个性签名
'Alias': '****',--WeChatID
'AttrStatus': 3***9,--？
'StarFriend': 0,--是否星标好友 1:星标  0：非星标
'UniFriend': 0,
'AppAccountFlag': 0,
'VerifyFlag': 0,--验证标志 用来判断是否是公众号/服务号
'ChatRoomId': 0,
'OwnerUin': 0,
'MemberCount': 0,
'UserName': '@51aa4aa2********f08',
'Statues': 0,
'HeadImgUrl': '/cgi-bin/mmwebwx-bin/webwxgeticon?seq=6**9&username=@51*****f08&skey=@crypt_a**b_6f**d55b'}--头像的URL ？

