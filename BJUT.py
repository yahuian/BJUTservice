import re
import urllib

import requests
from bs4 import BeautifulSoup
from lxml import etree

VPN_BJUT_URL = 'https://vpn.bjut.edu.cn/prx/000/http/localhost/login'
VPN_BJUT_GDJWGL_URL = 'https://vpn.bjut.edu.cn/prx/000/http/gdjwgl.bjut.edu.cn/'

class Student:
    def __init__(self):
        self.session = None
        self.number = ''
        self.password = ''
        self.name = ''
        self.college = ''
        self.major = ''
        self.class_name = ''

    def login_vpn(self, number: str, password: str) -> bool:
        try:
            self.number = number
            self.password = password

            # post VPN_BJUT_URL
            self.session = requests.Session()
            data_vpn = {
                'uname': self.number,
                'pwd1': self.password
            }
            r_vpn = self.session.post(VPN_BJUT_URL, data=data_vpn)
            r_vpn.raise_for_status()
            print('welcome页面响应的url: ' + r_vpn.url)

            url_without_code = VPN_BJUT_GDJWGL_URL + 'default_vsso.aspx'
            data_vpn_gdjwgl = {
                'TextBox1': self.number,
                'TextBox2': self.password,
                'RadioButtonList1_2': '%D1%A7%C9%FA',  # “学生”的gbk编码
            }
            r_vpn_gdjwgl = self.session.post(url_without_code, data_vpn_gdjwgl)
            # 从主页获取学生的姓名
            print('gdjwgl页面成功登录后的url: ' + r_vpn_gdjwgl.url)
            content = r_vpn_gdjwgl.content.decode('gbk')
            html = etree.HTML(content)
            welcome_text = html.xpath('//*[@id="xhxm"]/text()')[0]
            self.name = welcome_text[0:-2]
            return True
        except:
            print('VPN登录失败')
            return False

    def login_without_code(self, number: str, password: str) -> bool:
        """无验证码登录,原理是教务有个接口本身是不需要输入验证码的"""
        self.number = number
        self.password = password

        self.session = requests.Session()  # 开启一次session
        url = VPN_BJUT_GDJWGL_URL + 'default_vsso.aspx'  # 感谢野生工大助手项目：https://chafen.bjut123.com/
        data = {
            'TextBox1': self.number,
            'TextBox2': self.password,
            'RadioButtonList1_2': '%D1%A7%C9%FA',  # “学生”的gbk编码
        }
        response = self.session.post(url, data)

        # 从主页获取学生的姓名
        content = response.content.decode('gbk')  # 网页源码是gb2312要先解码
        html = etree.HTML(content)
        try:
            welcome_text = html.xpath('//*[@id="xhxm"]/text()')[0]
            self.name = welcome_text[0:-2]
            return True
        except IndexError:  # 模拟登录失败
            return False

    def get_base_info(self) -> bool:
        """获取学生基本信息"""
        name_url = urllib.parse.quote(str(self.name.encode('gbk')))  # 学生名字的url编码
        base_info_url = VPN_BJUT_GDJWGL_URL + 'xsgrxx.aspx?xh=' + self.number + '&xm=' + name_url + '&gnmkdm=N121501'
        headers = {
            "Referer": VPN_BJUT_GDJWGL_URL + 'xs_main.aspx?xh=' + self.number
        }
        response = self.session.get(url=base_info_url, headers=headers)
        html = response.content.decode("gbk")
        soup = BeautifulSoup(html, "lxml")
        try:
            self.college = soup.find(id='lbl_xy').get_text() #学院
            self.major = soup.find(id='lbl_zymc').get_text() #专业名称
            self.class_name = soup.find(id='lbl_xzb').get_text() #行政班
        except AttributeError:  #获取学生个人信息失败
            return False
        return True

    def get_schedule(self, xn: str, xq: str) -> dict:
        """获取课程表信息"""
        # 教务这个接口好呀，都不用发post请求就可以拿到课表数据
        schedule_url = VPN_BJUT_GDJWGL_URL + 'xskb.aspx?xh=' + self.number + '&xhxx=' + self.number + xn + xq
        print('课表url')
        print(schedule_url)
        response = self.session.get(url=schedule_url)
        html = response.content.decode("gbk")
        soup = BeautifulSoup(html, "lxml")

        # 获取课表信息
        trs = soup.find(id='Table1').find_all('tr')
        time_table = []
        for index in range(0, len(trs)): #<table>标签: <tr>-行, <td>-表格单元
            for td in trs[index].find_all('td'):
                if td.string is None:
                    res = td.find_all(text=True)
                    i = 1
                    j = 0
                    while i < len(res):
                        i = i + 1
                        if i % 4 == 0:
                            temp_dir = {
                                'Name': res[4 * j],  # 课程名称
                                'Time': re.sub('[{}]', '', res[4 * j + 1]),  # 上课时间
                                'Teacher': res[4 * j + 2],  # 授课老师
                                'Location': res[4 * j + 3][0:-29]  # 上课地点
                            }
                            time_table.append(temp_dir)
                            j = j + 1

        # 获取实践课信息
        exercise_course = []
        table = soup.find(id='DataGrid1').find_all('tr')
        for index in range(1, len(table)):
            td_list = table[index].find_all('td')
            temp_dir = {
                'Name': td_list[0].get_text(),  # 简单数据清洗
                'Teacher': td_list[1].get_text(),
                'credit': td_list[2].get_text(),  # 学分
                'Time': td_list[3].get_text()
            }
            exercise_course.append(temp_dir)

        schedule = {
            'table': time_table,  # 课表
            'exercise': exercise_course  # 实践课
        }
        return schedule

    def get_examination(self) -> list:
        """查询考试信息"""
        name_url = urllib.parse.quote(str(self.name.encode('gbk')))  # 学生名字的url编码
        exam_url = VPN_BJUT_GDJWGL_URL + 'xskscx.aspx?xh=' + self.number + '&xm' + name_url + '&gnmkdm=N121603'
        headers = {
            "Referer": VPN_BJUT_GDJWGL_URL + 'xs_main.aspx?xh=' + self.number
        }
        response = self.session.get(url=exam_url, headers=headers)
        html = response.content.decode("gbk")
        soup = BeautifulSoup(html, "lxml")
        trs = soup.find(id='DataGrid1').find_all('tr')
        exam_list = []
        for index in range(1, len(trs)):
            td_list = trs[index].find_all('td')
            temp_dir = {
                # 'classNum':td_list[0].get_text(),    # 选课课号
                'className': td_list[1].get_text(),  # 课程名称
                # 'stuName':td_list[2].get_text(),     # 学生姓名
                'examTime': td_list[3].get_text(),  # 考试时间
                'examRoom': td_list[4].get_text(),  # 考试地点
                # 'examForm':td_list[5].get_text(),     # 考试形式
                'deskNum': td_list[6].get_text(),  # 座位号
                'school': td_list[7].get_text()  # 校区
            }
            exam_list.append(temp_dir)
        return exam_list

    def get_CET_exam(self) -> list:
        """CET考试信息"""
        name_url = urllib.parse.quote(str(self.name.encode('gbk')))  # 学生名字的url编码
        grade_url = VPN_BJUT_GDJWGL_URL + 'xsdjkscx.aspx?xh=' + self.number + '&xm' + name_url + '&gnmkdm=N121603'
        headers = {
            "Referer": VPN_BJUT_GDJWGL_URL + 'xs_main.aspx?xh=' + self.number
        }
        response = self.session.get(url=grade_url, headers=headers)
        html = response.content.decode("gbk")
        soup = BeautifulSoup(html, "lxml")
        trs = soup.find(id='DataGrid1').find_all('tr')
        info_list = []
        for index in range(1, len(trs)):
            td_list = trs[index].find_all('td')
            temp_dir = {
                'schoolYear': td_list[0].get_text(),  # 学年
                'schoolWeek': td_list[1].get_text(),  # 学期
                'gradeExamName': td_list[2].get_text(),  # 等级考试名称
                'idNumber': td_list[3].get_text(),  # 准考证号
                'examDate': td_list[4].get_text(),  # 考试日期
                'score': td_list[5].get_text(),  # 成绩
                'listening': td_list[6].get_text(),  # 听力成绩
                'reading': td_list[7].get_text(),  # 阅读成绩
                'writting': td_list[8].get_text(),  # 写作成绩
                'all': td_list[9].get_text()  # 综合成绩
            }
            info_list.append(temp_dir)
        return info_list

    def get_score(self, xn: str, xq: str) -> dict:
        """成绩查询"""
        name_url = urllib.parse.quote(str(self.name.encode('gbk')))  # 学生名字的url编码
        score_url = VPN_BJUT_GDJWGL_URL + 'xscj_gc.aspx?xh=' + self.number + '&xm=' + name_url + '&gnmkdm=N121605'
        headers = {
            "Referer": VPN_BJUT_GDJWGL_URL + 'xs_main.aspx?xh=' + self.number
        }
        response = self.session.get(url=score_url, headers=headers)

        html = response.content.decode("gbk")
        soup = BeautifulSoup(html, "lxml")
        view_state = soup.find(id="Form1").find_all('input')[0]['value']
        data = {
            "__VIEWSTATE": view_state,
            "ddlXN": xn,  # 设置学年
            "ddlXQ": xq,  # 设置学期
            "Button1": ''
        }
        headers = {
            "Referer": VPN_BJUT_GDJWGL_URL + 'xscj_gc.aspx?xh=' + self.number + '&xm=' + name_url + '&gnmkdm=N121605'
        }
        response = self.session.post(url=score_url, data=data, headers=headers)
        html = response.content.decode("gbk")
        soup = BeautifulSoup(html, "lxml")

        # 计算所选学年学期的GPA和加权平均分
        data_term = []  # 计入加权的课程
        data_other = []  # 不计入加权的课程
        data_minor = [] # 辅修专业课程(都计入辅修专业加权)
        table = soup.find(id="Datagrid1").find_all('tr')
        for index in range(1, len(table)):
            td_list = table[index].find_all('td')
            temp_dir = {
                # 'year':td_list[0].get_text(),        # 学年
                # 'term':td_list[1].get_text(),        # 学期
                # 'courseCode':td_list[2].get_text(),  # 课程代码
                'courseName': td_list[3].get_text(),  # 课程名称
                # 'courseAttribute':td_list[4].get_text(), # 课程性质
                'courseBelongTo': td_list[5].get_text(),  # 课程归属
                'credit': float(td_list[6].get_text()),  # 学分
                'g': float(td_list[7].get_text().replace(' ', '')),  # 绩点
                'score': td_list[8].get_text(),  # 成绩
                'minorTag': td_list[9].get_text(),  # 辅修标记
                'makeupScore': td_list[10].get_text(),  # 补考成绩
                # 'rebuildScore':td_list[11].get_text(),     # 重修成绩
                # 'collegeName':td_list[12].get_text(),        # 学院名称
                # 'remark':td_list[13].get_text(),             # 备注
                # 'rebuildTag':td_list[14].get_text(),         # 重修标记
                # 'englishName':td_list[15].get_text()         # 课程英文名
            }

            # 提出辅修专业课程
            if temp_dir['minorTag'] != '0':
                data_minor.append(temp_dir)
            # 创新创业学分，新生研讨课和第二课堂不计入加权和GPA
            elif temp_dir['score'] == '通过' or temp_dir['courseBelongTo'] == '第二课堂':
                # 去除多余字段
                del (temp_dir['courseBelongTo'])
                del (temp_dir['g'])
                del (temp_dir['minorTag'])
                data_other.append(temp_dir)
            else:
                data_term.append(temp_dir)

        # print('辅修课程')
        # print(data_minor)
        # print('其余课程')
        # print(data_other)
        # print('本专业课程')
        # print(data_term)

        # 本专业
        sum_g_mul_credit_term = 0.0 #∑GPA*学分
        sum_score_mul_credit_term = 0.0 #∑成绩*学分
        sum_credit_term = 0.0 #∑学分

        for data in data_term:
            sum_g_mul_credit_term += data['g'] * data['credit']
            sum_score_mul_credit_term += float(data['score']) * data['credit']
            sum_credit_term += data['credit']

            # 去除多余字段
            del (data['courseBelongTo'])
            del (data['g'])
            del (data['minorTag'])

        try:
            GPA_term = sum_g_mul_credit_term / sum_credit_term  # 学期GPA
            SCORE_term = sum_score_mul_credit_term / sum_credit_term  # 学期加权
        except ZeroDivisionError:
            GPA_term = 0.0
            SCORE_term = 0.0

        # 辅修专业
        sum_g_mul_credit_term_minor = 0.0 #∑GPA*学分
        sum_score_mul_credit_term_minor = 0.0 #∑成绩*学分
        sum_credit_term_minor = 0.0 #∑学分

        for data in data_minor:
            sum_g_mul_credit_term_minor += data['g'] * data['credit']
            sum_score_mul_credit_term_minor += float(data['score']) * data['credit']
            sum_credit_term_minor += data['credit']
            
            # 去除多余字段
            del (data['courseBelongTo'])
            del (data['g'])
            del (data['minorTag'])

        try:
            GPA_term_minor = sum_g_mul_credit_term_minor / sum_credit_term_minor #学期GPA
            SCORE_term_minor = sum_score_mul_credit_term_minor / sum_credit_term_minor #学期加权
        except ZeroDivisionError:
            GPA_term_minor = 0.0
            SCORE_term_minor = 0.0

        # 获取大学总GPA和总加权平均分
        data = {
            "__VIEWSTATE": view_state,
            "ddlXN": '',
            "ddlXQ": '',
            "Button2": ''
        }
        response = self.session.post(url=score_url, data=data, headers=headers)
        html = response.content.decode("gbk")
        soup = BeautifulSoup(html, "lxml")

        dataList_all = [] # 本专业所有课程成绩
        dataList_all_minor = [] # 辅修专业所有课程成绩

        table = soup.find(id="Datagrid1").find_all('tr')
        for index in range(1, len(table)):
            td_list = table[index].find_all('td')
            temp_dir = {
                'courseName': td_list[3].get_text(),  # 课程名称
                'courseAttribute': td_list[4].get_text(),  # 课程性质
                'courseBelongTo': td_list[5].get_text(),  # 课程归属
                'credit': float(td_list[6].get_text()),  # 学分
                'g': float(td_list[7].get_text().replace(' ', '')),  # 绩点
                'score': td_list[8].get_text(),  # 成绩
                'minorTag': td_list[9].get_text(),  # 辅修标记
                'makeupScore': td_list[10].get_text(),  # 补考成绩
                'rebuildTag': td_list[14].get_text()  # 重修标记
            }

            # 提出辅修专业成绩
            if temp_dir['minorTag'] != '0':
                dataList_all_minor.append(temp_dir)
            else:
                dataList_all.append(temp_dir)

        # 本专业
        sum_g_mul_credit_all = 0.0
        sum_score_mul_credit_all = 0.0
        sum_credit_all = 0.0
        tempList = []

        for data in dataList_all:
            # 创新创业学分，新生研讨课和第二课堂不计入本专业加权和GPA
            if data['score'] == '通过' or data['courseBelongTo'] == '第二课堂':
                pass
            else:
                # 首次就通过科目
                if float(data['score']) >= 60 and data['rebuildTag'] == '0':
                    sum_g_mul_credit_all += data['g'] * data['credit']
                    sum_score_mul_credit_all += float(data['score']) * data['credit']
                    sum_credit_all += data['credit']
                else:
                    if data['makeupScore'] == '60':  # 补考后通过
                        sum_g_mul_credit_all += 2.00 * data['credit']
                        sum_score_mul_credit_all += 60 * data['credit']
                        sum_credit_all += data['credit']

                    elif data['rebuildTag'] == '0':  # 补考没过，或者没参加补考，或者该课没有补考机会
                        tempList.append(data)  # 暂时先存放到tempList中

                    elif data['rebuildTag'] == '1':
                        if float(data['score']) >= 60:
                            # 重修后过了，得从tempList中删除以前没过的同一课程
                            for t in tempList:
                                if data['courseName'] == t['courseName']:
                                    tempList.remove(t)
                                    tempList.append(data)
                        else:  # 重修没过
                            tempList.append(data)

        for t in tempList:
            if t['courseAttribute'] == '通识教育选修课' or \
                    t['courseAttribute'] == '专业任选课' or \
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

        # print(sum_g_mul_credit_all)
        # print(sum_score_mul_credit_all)
        # print(sum_credit_all)

        try:
            GPA_all = sum_g_mul_credit_all / sum_credit_all  # 总GPA
            SCORE_all = sum_score_mul_credit_all / sum_credit_all  # 总加权
        except ZeroDivisionError:
            GPA_all = 0.0
            SCORE_all = 0.0

        # 辅修专业
        sum_g_mul_credit_all_minor = 0.0
        sum_score_mul_credit_all_minor = 0.0
        sum_credit_all_minor = 0.0
        tempList_minor = []

        for data in dataList_all_minor:
            # 创新创业学分，新生研讨课和第二课堂不计入本专业加权和GPA
            if data['score'] == '通过' or data['courseBelongTo'] == '第二课堂':
                pass
            else:
                # 首次就通过科目
                if float(data['score']) >= 60 and data['rebuildTag'] == '0':
                    sum_g_mul_credit_all_minor += data['g'] * data['credit']
                    sum_score_mul_credit_all_minor += float(
                        data['score']) * data['credit']
                    sum_credit_all_minor += data['credit']
                else:
                    if data['makeupScore'] == '60':  # 补考后通过
                        sum_g_mul_credit_all_minor += 2.00 * data['credit']
                        sum_score_mul_credit_all_minor += 60 * data['credit']
                        sum_credit_all_minor += data['credit']

                    elif data['rebuildTag'] == '0':  # 补考没过，或者没参加补考，或者该课没有补考机会
                        tempList_minor.append(data)  # 暂时先存放到tempList_minor中

                    elif data['rebuildTag'] == '1':
                        if float(data['score']) >= 60:
                            # 重修后过了，得从tempList中删除以前没过的同一课程
                            for t in tempList_minor:
                                if data['courseName'] == t['courseName']:
                                    tempList_minor.remove(t)
                                    tempList_minor.append(data)
                        else:  # 重修没过
                            tempList_minor.append(data)

        for t in tempList_minor:
            if t['courseAttribute'] == '通识教育选修课' or \
                    t['courseAttribute'] == '专业任选课' or \
                    t['courseAttribute'] == '专业限选课':
                tempList_minor.remove(t)  # 这三类选修课挂科了，重修没过或者没有参加重修，无所谓，不计入总加权

        # 多次重修没过的课程，选择最高分来计算加权
        try:
            for i in range(0, len(tempList_minor)):
                for j in range(1, len(tempList_minor)):
                    if tempList_minor[i]['courseName'] == tempList_minor[j]['courseName']:
                        if float(tempList_minor[i]['score']) > \
                                float(tempList_minor[j]['score']):
                            tempList_minor[j] = tempList_minor[i]
                        else:
                            tempList_minor[i] = tempList_minor[j]
        except IndexError:
            pass

        # 将这些特殊的课程和正常课程的加权合并
        for t in tempList_minor:
            sum_g_mul_credit_all_minor += t['g'] * t['credit']
            sum_score_mul_credit_all_minor += float(t['score']) * t['credit']
            sum_credit_all_minor += t['credit']

        try:
            GPA_all_minor = sum_g_mul_credit_all_minor / sum_credit_all_minor  # 总GPA(辅修专业)
            SCORE_all_minor = sum_score_mul_credit_all_minor / sum_credit_all_minor  # 总加权(辅修专业)
        except ZeroDivisionError:
            GPA_all_minor = 0.0
            SCORE_all_minor = 0.0

        # 辅修专业

        summery = {
            'SCORE_all': SCORE_all,  # 大学总加权
            'GPA_all': GPA_all,  # 大学总绩点
            'SCORE_term': SCORE_term,  # 本学期加权
            'GPA_term': GPA_term,  # 本学期绩点
            'SCORE_all_minor': SCORE_all_minor, #大学总加权(辅修)
            'GPA_all_minor': GPA_all_minor, # 大学总绩点(辅修)
            'SCORE_term_minor': SCORE_term_minor, #本学期总加权(辅修) 
            'GPA_term_minor': GPA_term_minor #本学期总绩点(辅修)
        }
        result = {
            'score': data_term,
            'other': data_other,
            'minor': data_minor,
            'summery': summery
        }
        return result
# TODO 将计算加权的逻辑放到客户端，减少服务器的压力
