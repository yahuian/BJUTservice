import os
import re
import urllib
import requests
from lxml import etree
from bs4 import BeautifulSoup

# 教务系统
class BJUTjiaowu:
    '定义基本私有属性'
    __default2Url = "http://188.131.128.233/default2.aspx"    # 教务初始页面地址
    __checkCodeUrl = "http://188.131.128.233/CheckCode.aspx"  # 验证码地址

    __studentNumber=''    # 学号
    __password=''         # 密码
    __checkCode=''        # 验证码

    __studentName=''      # 姓名
    __college=''          # 学院
    __major=''            # 专业
    __class=''            # 班级

    __sessionID=''        # 标识用户身份的id

    def __init__(self):
        '构造函数'
    
    def getCheckCode(self):
        '获取验证码'
        s = requests.Session()
        response = s.get(self.__checkCodeUrl)
        image = response.content
        DstDir = os.getcwd()+"/consoleDev/"
        codeName = list(s.cookies)[0].value # 验证码的名字就是sessionID
        try:
            with open(DstDir + codeName + ".jpg", "wb") as jpg:
                jpg.write(image)
        except IOError:
            return "获取验证码失败"
        else:
            self.__sessionID=list(s.cookies)[0].value
            temp = {"sessionID":list(s.cookies)[0].value}
            return temp
    
    def login(self,studentNumber,password,checkCode):
        '登录教务管理系统'
        self.__studentNumber=studentNumber
        self.__password=password
        self.__checkCode=checkCode

        # 确保用户身份不变
        mycookie = {"ASP.NET_SessionId": self.__sessionID}
        s = requests.Session()
        requests.utils.add_dict_to_cookiejar(s.cookies, mycookie)

        # 获取__VIEWSTATE
        response = s.get(self.__default2Url)
        html = etree.HTML(response.content)
        viewState = html.xpath('//*[@id="form1"]/input/@value')[0]

        # 构建post数据，并登陆教务系统
        RadioButtonList1 = u"学生".encode('gb2312', 'replace')
        data = {
            "__VIEWSTATE": viewState,
            "txtUserName": studentNumber,
            "TextBox2": password,
            "txtSecretCode": checkCode,
            "RadioButtonList1": RadioButtonList1,
            "Button1": "",
            "lbLanguage": "",
            "hidPdrs": "",
            "hidsc": ""
            }
        headers = {
            "User-Agent":
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/7",
            }
        response = s.post(self.__default2Url,data,headers)
    
        # 从主页获取学生的姓名
        content = response.content.decode('gb2312') # 网页源码是gb2312要先解码
        html = etree.HTML(content)
        try:
            studentName = html.xpath('//*[@id="xhxm"]/text()')[0][0:-2]
            self.__studentName=studentName
            return '登录成功'
        except IndexError:
            return '请检查学号,密码,验证码是否有错'
    
    def loginNoCheckcode(self,studentNumber,password):
        '无验证码登录,原理是教务有个接口本身是不需要输入验证码的'
        self.__studentNumber=studentNumber
        self.__password=password
        
        s=requests.Session()

        url='http://188.131.128.233/default_vsso.aspx' # 感谢野生工大助手项目：https://chafen.bjut123.com/

        data={
            'TextBox1':self.__studentNumber,
            'TextBox2':self.__password,
            'RadioButtonList1_2':'%D1%A7%C9%FA', # “学生”的gbk编码
            'Button1':'',
        }
        headers = {
                    "User-Agent":
                    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/7",
                    }

        response = s.post(url,data,headers)

        # 从主页获取学生的姓名
        content = response.content.decode('gb2312') # 网页源码是gb2312要先解码
        html = etree.HTML(content)
        try:
            studentName = html.xpath('//*[@id="xhxm"]/text()')[0][0:-2]
            self.__studentName=studentName
            self.__sessionID=list(s.cookies)[0].value # 保留此次登录的sessionID
            return '登录成功'
        except IndexError:
            return '请检查学号,密码是否有错'

    def getBaseInfo(self):
        '获取学生基本信息'
        # 确保用户身份不变
        mycookie = {"ASP.NET_SessionId": self.__sessionID}
        s = requests.Session()
        requests.utils.add_dict_to_cookiejar(s.cookies, mycookie)

        # 获取学生基本信息
        urlStudentName = urllib.parse.quote(str(self.__studentName.encode('gb2312')))
        scheduleBaseUrl = "http://188.131.128.233/xskbcx.aspx?xh="+self.__studentNumber+"&xm="+urlStudentName+"&gnmkdm=N121603"
        headers = {
            "Referer": "http://188.131.128.233/xs_main.aspx?xh="+self.__studentNumber,
            "User-Agent":
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
            "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/71.0.3578.98 Safari/537.36"
            }
        response = s.get(url=scheduleBaseUrl, headers=headers)
        html = response.content.decode("gbk")
        soup = BeautifulSoup(html,"lxml")
        spans=soup.find(class_='trbg1').find_all('span')
        self.__college=spans[2].get_text()[3:]
        self.__major=spans[3].get_text()[3:]
        self.__class=spans[4].get_text()[3:]
        baseInfo={
            'studentNumber':self.__studentNumber, # 学号
            'studentName':self.__studentName,     # 姓名
            'college':self.__college,             # 学院
            'major':self.__major,                 # 专业
            'class':self.__class                  # 班级
        }
        return(baseInfo)

    def getSchedule(self):
        '获取课程表信息'
        # 确保用户身份不变
        mycookie = {"ASP.NET_SessionId": self.__sessionID}
        s = requests.Session()
        requests.utils.add_dict_to_cookiejar(s.cookies, mycookie)

        # 获取课表
        urlStudentName = urllib.parse.quote(str(self.__studentName.encode('gb2312')))
        scheduleBaseUrl = "http://188.131.128.233/xskbcx.aspx?xh="+self.__studentNumber+"&xm="+urlStudentName+"&gnmkdm=N121603"
        headers = {
            "Referer": "http://188.131.128.233/xs_main.aspx?xh="+self.__studentNumber,
            "User-Agent":
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
            "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/71.0.3578.98 Safari/537.36"
            }
        # 选择当前默认学期的课表
        response = s.get(url=scheduleBaseUrl, headers=headers)
        html=response.content.decode("gbk")

        # 可以设定特定学年,学期的课表
        '''
        html = etree.HTML(response.content)
        viewState = html.xpath('//*[@id="xskb_form"]/input/@value')[2]
        xnd = "2018-2019" # 设置学年
        xqd = "2" # 设置学期
        data = {
            "__EVENTTARGET": xqd,
            "__EVENTARGUMENT": "",
            "__VIEWSTATE":viewState,
            "xnd": xnd,
            "xqd": xqd
        }
        response = s.get(url= scheduleBaseUrl, data=data, headers=headers) # 默认页面用get方式，若涉及选择学期则用post方式
        html = response.content.decode("gbk")
        '''
        # 获取课表数据
        soup = BeautifulSoup(html,"lxml")
        dataList = []
        trs = soup.find(id='Table1').find_all('tr')
        for index in range(0,len(trs)):
            for td in trs[index].find_all('td'):
                if td.string==None:
                    res = td.find_all(text=True)
                    i = 1
                    j = 0
                    while i<len(res):
                        i = i+1
                        if i%4==0:
                            tempDir = {
                                'Name': res[4*j],                        # 课程名称
                                'Time': re.sub('[{}]', '', res[4*j+1]),  # 上课时间
                                'Teacher': res[4*j+2],                   # 授课老师 
                                'Location': res[4*j+3]                   # 上课地点
                            }    
                            dataList.append(tempDir)
                            j = j+1

        # 获取实践课信息
        dataList1=[]
        table=soup.find(id='DataGrid1').find_all('tr')
        if len(table)>1: # 有实践课程
            for index in range(1,len(table)):
                tdList=table[index].find_all('td')
                tempDir={
                    'Name':tdList[0].get_text(), # 简单数据清洗
                    'Teacher':tdList[1].get_text(),
                    'credit':tdList[2].get_text(), # 学分
                    'Time':tdList[3].get_text()
                }
                dataList1.append(tempDir)
        else:
            dataList1.append({})

        temp={
            'table':dataList,   # 课表
            'exercise':dataList1 # 实践课
        }

        return(temp)
