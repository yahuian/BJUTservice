import os
import re
import urllib
import requests
from lxml import etree
from bs4 import BeautifulSoup


class BJUTjiaowu:
    '定义基本私有属性'
    __default2Url = "http://39.105.71.59/default2.aspx"    # 教务初始页面地址
    __checkCodeUrl = "http://39.105.71.59/CheckCode.aspx"  # 验证码地址

    __studentNumber = ''    # 学号
    __password = ''         # 密码
    __checkCode = ''        # 验证码

    __studentName = ''      # 姓名
    __college = ''          # 学院
    __major = ''            # 专业
    __class = ''            # 班级

    __sessionID = ''        # 标识用户身份的id

    def __init__(self):
        '构造函数'

    def login(self, studentNumber, password, checkCode):
        '登录教务管理系统'
        self.__studentNumber = studentNumber
        self.__password = password
        self.__checkCode = checkCode

        # 确保用户身份不变
        mycookie = {"ASP.NET_SessionId": self.__sessionID}
        s = requests.Session()
        requests.utils.add_dict_to_cookiejar(s.cookies, mycookie)

        # 获取__VIEWSTATE
        response = s.get(self.__default2Url)
        html = etree.HTML(response.content)
        viewState = html.xpath('//*[@id="form1"]/input/@value')[0]

        # 构建post数据，并登陆教务系统
        RadioButtonList1 = u"学生".encode('gbk', 'replace')
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
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64)\
            AppleWebKit/537.36 (KHTML, like Gecko) Chrome/7",
        }
        response = s.post(self.__default2Url, data, headers)

        # 从主页获取学生的姓名
        # 网页源码是gb2312要先解码,有同学名字超出gb2312编码,所以换成范围更大的gbk
        content = response.content.decode('gbk')
        html = etree.HTML(content)
        try:
            studentName = html.xpath('//*[@id="xhxm"]/text()')[0][0:-2]
            self.__studentName = studentName
            return '登录成功'
        except IndexError:
            return '请检查学号,密码,验证码是否有错'

    def loginNoCheckcode(self, studentNumber, password):
        '无验证码登录,原理是教务有个接口本身是不需要输入验证码的'
        self.__studentNumber = studentNumber
        self.__password = password

        s = requests.Session()

        # 感谢野生工大助手项目：https://chafen.bjut123.com/
        url = 'http://39.105.71.59/default_vsso.aspx'

        data = {
            'TextBox1': self.__studentNumber,
            'TextBox2': self.__password,
            'RadioButtonList1_2': '%D1%A7%C9%FA',  # “学生”的gbk编码
            'Button1': '',
        }
        headers = {
            "User-Agent":
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64)\
            AppleWebKit/537.36 (KHTML, like Gecko) Chrome/7",
        }

        response = s.post(url, data, headers)

        # 从主页获取学生的姓名
        content = response.content.decode('gbk')  # 网页源码是gb2312要先解码
        html = etree.HTML(content)
        try:
            studentName = html.xpath('//*[@id="xhxm"]/text()')[0][0:-2]
            self.__studentName = studentName
            self.__sessionID = list(s.cookies)[0].value  # 保留此次登录的sessionID
            return True
        except IndexError:
            return False

    def getBaseInfo(self):
        '获取学生基本信息'
        # 确保用户身份不变
        mycookie = {"ASP.NET_SessionId": self.__sessionID}
        s = requests.Session()
        requests.utils.add_dict_to_cookiejar(s.cookies, mycookie)

        # 获取学生基本信息
        urlStudentName = urllib.parse.quote(
            str(self.__studentName.encode('gbk')))
        baseInfoUrl = "http://39.105.71.59/xsgrxx.aspx?xh=" + \
            self.__studentNumber+"&xm="+urlStudentName+"&gnmkdm=N121501"
        headers = {
            "Referer": "http://39.105.71.59/xs_main.aspx?xh=" +
            self.__studentNumber,
            "User-Agent":
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64)\
            AppleWebKit/537.36 (KHTML, like Gecko)\
            Chrome/71.0.3578.98 Safari/537.36"
        }
        response = s.get(url=baseInfoUrl, headers=headers)
        html = response.content.decode("gbk")
        soup = BeautifulSoup(html, "lxml")

        self.__studentNumber = soup.find(id='xh').get_text()
        self.__studentName = soup.find(id='xm').get_text()
        self.__college = soup.find(id='lbl_xy').get_text()
        self.__major = soup.find(id='lbl_zymc').get_text()
        self.__class = soup.find(id='lbl_xzb').get_text()

        baseinfo = {
            'stuNum': self.__studentNumber,
            'sutName': self.__studentName,
            'college': self.__college,
            'major': self.__major,
            'class': self.__class
        }
        return(baseinfo)

    def getSchedule(self, xn, xq):
        '获取课程表信息'
        # 确保用户身份不变
        mycookie = {"ASP.NET_SessionId": self.__sessionID}
        s = requests.Session()
        requests.utils.add_dict_to_cookiejar(s.cookies, mycookie)
        # 教务这个接口好呀，都不用发post请求就可以拿到课表数据
        scheduleUrl = "http://39.105.71.59/xskb.aspx?xh=" + \
            self.__studentNumber \
            + "&xhxx=" + self.__studentNumber + xn + xq
        response = s.get(url=scheduleUrl)
        html = response.content.decode("gbk")
        soup = BeautifulSoup(html, "lxml")
        dataList = []
        trs = soup.find(id='Table1').find_all('tr')
        for index in range(0, len(trs)):
            for td in trs[index].find_all('td'):
                if td.string is None:
                    res = td.find_all(text=True)
                    i = 1
                    j = 0
                    while i < len(res):
                        i = i+1
                        if i % 4 == 0:
                            tempDir = {
                                'Name': res[4*j],                        # 课程名称
                                'Time': re.sub('[{}]', '', res[4*j+1]),  # 上课时间
                                'Teacher': res[4*j+2],                   # 授课老师
                                'Location': res[4*j+3][0:-29]            # 上课地点
                            }
                            dataList.append(tempDir)
                            j = j+1
        # 获取实践课信息
        dataList1 = []
        table = soup.find(id='DataGrid1').find_all('tr')
        if len(table) > 1:  # 有实践课程
            for index in range(1, len(table)):
                tdList = table[index].find_all('td')
                tempDir = {
                    'Name': tdList[0].get_text(),  # 简单数据清洗
                    'Teacher': tdList[1].get_text(),
                    'credit': tdList[2].get_text(),  # 学分
                    'Time': tdList[3].get_text()
                }
                dataList1.append(tempDir)
        else:
            dataList1.append({})
        temp = {
            'table': dataList,   # 课表
            'exercise': dataList1  # 实践课
        }
        return(temp)

    def getExamination(self):
        '查询考试信息'
        # 确保用户身份不变
        mycookie = {"ASP.NET_SessionId": self.__sessionID}
        s = requests.Session()
        requests.utils.add_dict_to_cookiejar(s.cookies, mycookie)

        # 获取考试信息
        urlStudentName = urllib.parse.quote(
            str(self.__studentName.encode('gbk')))
        examinationUrl = "http://39.105.71.59/xskscx.aspx?xh=" + \
            self.__studentNumber+"&xm="+urlStudentName+"&gnmkdm=N121603"
        headers = {
            "Referer": "http://39.105.71.59/xs_main.aspx?xh=" +
            self.__studentNumber,
            "User-Agent":
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
            "AppleWebKit/537.36 (KHTML, like Gecko)\
            Chrome/71.0.3578.98 Safari/537.36"
        }
        response = s.get(url=examinationUrl, headers=headers)
        html = response.content.decode("gbk")
        soup = BeautifulSoup(html, "lxml")
        trs = soup.find(id='DataGrid1').find_all('tr')
        examList = []
        if len(trs) > 1:
            for index in range(1, len(trs)):
                tdList = trs[index].find_all('td')
                tempDir = {
                    # 'classNum':tdList[0].get_text(),    # 选课课号
                    'className': tdList[1].get_text(),   # 课程名称
                    # 'stuName':tdList[2].get_text(),     # 学生姓名
                    'examTime': tdList[3].get_text(),     # 考试时间
                    'examRoom': tdList[4].get_text(),     # 考试地点
                    # 'examForm':tdList[5].get_text(),     # 考试形式
                    'deskNum': tdList[6].get_text(),      # 座位号
                    'school': tdList[7].get_text()       # 校区
                }
                examList.append(tempDir)
            return examList
        else:
            return examList

    def getGradeExam(self):
        '等级考试信息'
        # 确保用户身份不变
        mycookie = {"ASP.NET_SessionId": self.__sessionID}
        s = requests.Session()
        requests.utils.add_dict_to_cookiejar(s.cookies, mycookie)

        # 获取等级考试信息
        urlStudentName = urllib.parse.quote(
            str(self.__studentName.encode('gbk')))
        gradeExamURL = "http://39.105.71.59/xsdjkscx.aspx?xh=" + \
            self.__studentNumber+"&xm="+urlStudentName+"&gnmkdm=N121603"
        headers = {
            "Referer": "http://39.105.71.59/xs_main.aspx?xh=" +
            self.__studentNumber,
            "User-Agent":
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
            "AppleWebKit/537.36 (KHTML, like Gecko)\
            Chrome/71.0.3578.98 Safari/537.36"
        }
        response = s.get(url=gradeExamURL, headers=headers)
        html = response.content.decode("gbk")
        soup = BeautifulSoup(html, "lxml")
        trs = soup.find(id='DataGrid1').find_all('tr')
        infoList = []
        if len(trs) > 1:
            for index in range(1, len(trs)):
                tdList = trs[index].find_all('td')
                tempDir = {
                    'schoolYear': tdList[0].get_text(),      # 学年
                    'schoolWeek': tdList[1].get_text(),      # 学期
                    'gradeExamName': tdList[2].get_text(),   # 等级考试名称
                    'idNumber': tdList[3].get_text(),        # 准考证号
                    'examDate': tdList[4].get_text(),        # 考试日期
                    'score': tdList[5].get_text(),           # 成绩
                    'listening': tdList[6].get_text(),       # 听力成绩
                    'reading': tdList[7].get_text(),         # 阅读成绩
                    'writting': tdList[8].get_text(),        # 写作成绩
                    'all': tdList[9].get_text()              # 综合成绩
                }
                infoList.append(tempDir)
            return infoList
        else:
            return infoList

    def getScore(self, xn, xq):
        '成绩查询'
        # 确保用户身份不变
        mycookie = {"ASP.NET_SessionId": self.__sessionID}
        s = requests.Session()
        requests.utils.add_dict_to_cookiejar(s.cookies, mycookie)

        # 获取特定学年和学期的成绩
        urlStudentName = urllib.parse.quote(
            str(self.__studentName.encode('gbk')))
        scoreBaseUrl = "http://39.105.71.59/xscj_gc.aspx?xh=" + \
            self.__studentNumber+"&xm="+urlStudentName+"&gnmkdm=N121605"
        headers = {
            "Referer": "http://39.105.71.59/xs_main.aspx?xh=" +
            self.__studentNumber,
            "User-Agent":
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
            "AppleWebKit/537.36 (KHTML, like Gecko)\
            Chrome/71.0.3578.98 Safari/537.36"
        }
        response = s.get(url=scoreBaseUrl, headers=headers)
        html = response.content.decode("gbk")
        soup = BeautifulSoup(html, "lxml")
        viewState = soup.find(id="Form1").find_all('input')[0]['value']
        data = {
            "__VIEWSTATE": viewState,
            "ddlXN": xn,  # 设置学年
            "ddlXQ": xq,  # 设置学期
            "Button1": ''
        }
        response = s.post(url=scoreBaseUrl, data=data, headers=headers)
        html = response.content.decode("gbk")
        soup = BeautifulSoup(html, "lxml")

        # 获取考试成绩
        dataList_term = []  # 计入加权的课程
        dataList_other = []  # 不计入加权的课程
        table = soup.find(id="Datagrid1").find_all('tr')
        if len(table) > 1:  # 有成绩
            for index in range(1, len(table)):
                tdList = table[index].find_all('td')
                tempDir = {
                    # 'year':tdList[0].get_text(),        # 学年
                    # 'term':tdList[1].get_text(),        # 学期
                    # 'courseCode':tdList[2].get_text(),  # 课程代码
                    'courseName': tdList[3].get_text(),   # 课程名称
                    # 'courseAttribute':tdList[4].get_text(), # 课程性质
                    'courseBelongTo': tdList[5].get_text(),   # 课程归属
                    'credit': float(tdList[6].get_text()),               # 学分
                    'g': float(tdList[7].get_text().replace(' ', '')),    # 绩点
                    'score': tdList[8].get_text(),              # 成绩
                    'minorTag': tdList[9].get_text(),           # 辅修标记
                    'makeupScore': tdList[10].get_text(),       # 补考成绩
                    # 'rebuildScore':tdList[11].get_text(),     # 重修成绩
                    # 'collegeName':tdList[12].get_text(),        # 学院名称
                    # 'remark':tdList[13].get_text(),             # 备注
                    # 'rebuildTag':tdList[14].get_text(),         # 重修标记
                    # 'englishName':tdList[15].get_text()         # 课程英文名
                }
                # 辅修双学位，创新创业学分，新生研讨课和第二课堂不计入加权和GPA
                if tempDir['minorTag'] != '0' or tempDir['score'] == '通过' \
                        or tempDir['courseBelongTo'] == '第二课堂':
                    # 去除多余字段
                    del(tempDir['courseBelongTo'])
                    del(tempDir['g'])
                    del(tempDir['minorTag'])
                    dataList_other.append(tempDir)
                else:
                    dataList_term.append(tempDir)

        sum_g_mul_credit_term = 0.0
        sum_score_mul_credit_term = 0.0
        sum_credit_term = 0.0

        for data in dataList_term:
            sum_g_mul_credit_term += data['g'] * data['credit']
            sum_score_mul_credit_term += float(data['score']) * data['credit']
            sum_credit_term += data['credit']

            # 去除多余字段
            del(data['courseBelongTo'])
            del(data['g'])
            del(data['minorTag'])

        try:
            GPA_term = sum_g_mul_credit_term / sum_credit_term  # 学期GPA
            SCORE_term = sum_score_mul_credit_term / sum_credit_term  # 学期加权
        except ZeroDivisionError:
            GPA_term = 0.0
            SCORE_term = 0.0

        # 获取大学所有成绩
        data = {
            "__VIEWSTATE": viewState,
            "ddlXN": '',
            "ddlXQ": '',
            "Button2": ''
        }
        response = s.post(url=scoreBaseUrl, data=data, headers=headers)
        html = response.content.decode("gbk")
        soup = BeautifulSoup(html, "lxml")
        # 获取考试成绩
        dataList_all = []
        table = soup.find(id="Datagrid1").find_all('tr')
        if len(table) > 1:  # 有成绩
            for index in range(1, len(table)):
                tdList = table[index].find_all('td')
                tempDir = {
                    'courseName': tdList[3].get_text(),   # 课程名称
                    'courseAttribute': tdList[4].get_text(),  # 课程性质
                    'courseBelongTo': tdList[5].get_text(),   # 课程归属
                    'credit': float(tdList[6].get_text()),               # 学分
                    'g': float(tdList[7].get_text().replace(' ', '')),    # 绩点
                    'score': tdList[8].get_text(),           # 成绩
                    'minorTag': tdList[9].get_text(),        # 辅修标记
                    'makeupScore': tdList[10].get_text(),    # 补考成绩
                    'rebuildTag': tdList[14].get_text()      # 重修标记
                }
                dataList_all.append(tempDir)

        sum_g_mul_credit_all = 0.0
        sum_score_mul_credit_all = 0.0
        sum_credit_all = 0.0
        tempList = []

        for data in dataList_all:
            # 辅修双学位，创新创业学分，新生研讨课和第二课堂不计入加权和GPA
            if data['minorTag'] != '0' or data['score'] == '通过'\
                     or data['courseBelongTo'] == '第二课堂':
                pass
            else:
                # 首次就通过科目
                if float(data['score']) >= 60 and data['rebuildTag'] == '0':
                    sum_g_mul_credit_all += data['g'] * data['credit']
                    sum_score_mul_credit_all += float(
                        data['score']) * data['credit']
                    sum_credit_all += data['credit']
                else:
                    if data['makeupScore'] == '60':  # 补考后通过
                        sum_g_mul_credit_all += 2.00 * data['credit']
                        sum_score_mul_credit_all += 60 * data['credit']
                        sum_credit_all += data['credit']

                    elif data['rebuildTag'] == '0':  # 补考没过，或者没参加补考，或者该课没有补考机会
                        tempList.append(data)   # 暂时先存放到tempList中

                    elif data['rebuildTag'] == '1':
                        if float(data['score']) >= 60:
                            # 重修后过了，得从tempList中删除以前没过的同一课程
                            for t in tempList:
                                if data['courseName'] == t['courseName']:
                                    tempList.remove(t)
                                    tempList.append(data)
                        else:   # 重修没过
                            tempList.append(data)

        for t in tempList:
            if t['courseAttribute'] == '通识教育选修课' or\
                t['courseAttribute'] == '专业任选课' or\
                    t['courseAttribute'] == '专业限选课':
                tempList.remove(t)  # 这三类选修课挂科了，重修没过或者没有参加重修，无所谓，不计入总加权

        # 多次重修没过的课程，选择最高分来计算加权
        try:
            for i in range(0, len(tempList)):
                for j in range(1, len(tempList)):
                    if tempList[i]['courseName'] == tempList[j]['courseName']:
                        if float(tempList[i]['score']) > \
                             float(tempList[j]['score']):
                            tempList[j] = tempList[i]
                        else:
                            tempList[i] = tempList[j]
        except IndexError:
            pass

        # 将这些特殊的课程和正常课程的加权合并
        for t in tempList:
            sum_g_mul_credit_all += t['g'] * t['credit']
            sum_score_mul_credit_all += float(t['score']) * t['credit']
            sum_credit_all += t['credit']

        try:
            GPA_all = sum_g_mul_credit_all / sum_credit_all  # 总GPA
            SCORE_all = sum_score_mul_credit_all / sum_credit_all  # 总加权
        except ZeroDivisionError:
            GPA_all = 0.0
            SCORE_all = 0.0

        summmery = {
            'SCORE_all': SCORE_all,  # 大学总加权
            'GPA_all': GPA_all,      # 大学总绩点
            'SCORE_term': SCORE_term,  # 本学期加权
            'GPA_term': GPA_term  # 本学期绩点
        }
        temp = {
            'score': dataList_term,
            'other': dataList_other,
            'summery': summmery
        }
        return(temp)
