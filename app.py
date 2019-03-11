import json
import os
import re
import urllib
import datetime
import requests
from bs4 import BeautifulSoup
from flask import Flask, render_template, request,jsonify
from lxml import etree

# 初始化相关参数
default2Url = "http://188.131.128.233/default2.aspx"
checkCodeUrl = "http://188.131.128.233/CheckCode.aspx"

app = Flask(__name__) # 实例化一个程序


# 客户端第一次发送请求，我们返回验证码和cookieID
@app.route('/get')
def getCode():
    s = requests.Session()
    response = s.get(checkCodeUrl)
    image = response.content
    DstDir = os.getcwd()+"/static/"
    timenow = datetime.datetime.now().strftime('%Y-%m-%d_%H-%M-%S')
    try:
        with open(DstDir + timenow + "code.jpg", "wb") as jpg:
            jpg.write(image)
    except IOError:
        print("IO Error\n")
    codeName = timenow + "code.jpg"
    temp = {"sessionID":list(s.cookies)[0].value,"codeName":codeName}
    return jsonify(temp)

# 以查询字符串的形式发送get请求，
# 例如：http://127.0.0.1:5000/?xh=16010328&mm=12%26%3d%2f23%23&yzm=1234&id=axvebh55qcaz0b55sozmqt55
# 注意此处必须采用url编码
@app.route('/')
def login():
    studentNumber = request.args.get("xh")
    password = request.args.get("mm")
    checkCode = request.args.get("yzm")
    cookieID = request.args.get("id")

    # 确保用户身份和第一次是一样的
    mycookie = {"ASP.NET_SessionId": cookieID}
    s = requests.Session()
    requests.utils.add_dict_to_cookiejar(s.cookies, mycookie)

    # 使用xpath获取__VIEWSTATE
    response = s.get(default2Url)
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
    response = s.post(default2Url,data,headers)
    
    # 从主页获取学生的姓名
    content = response.content.decode('gb2312') # 网页源码是gb2312要先解码
    html = etree.HTML(content)
    try:
        studentName = html.xpath('//*[@id="xhxm"]/text()')[0][0:3]
    except IndexError:
        return "请检查学号，密码，验证码是否正确"
    else:
        # 获取课表
        urlStudentName = urllib.parse.quote(str(studentName.encode('gb2312')))
        scheduleBaseUrl = "http://188.131.128.233/xskbcx.aspx?xh="+studentNumber+"&xm="+urlStudentName+"&gnmkdm=N121603"
        headers = {
            "Referer": "http://188.131.128.233/xs_main.aspx?xh="+studentNumber,
            "User-Agent":
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/71.0.3578.98 Safari/537.36"
        }
        response = s.get(url=scheduleBaseUrl, headers=headers)
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
        soup = BeautifulSoup(html,"lxml")
        dataList = []
        tempDir = {}
        trs = soup.find(id='Table1').find_all('tr')
        for tr in trs:
            for td in tr.find_all('td'):
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
        return jsonify(dataList)


# 服务器开始运行
if __name__ == '__main__':
    app.run()