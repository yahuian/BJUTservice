import os
import sqlite3

from flask import Flask, g, jsonify, make_response, request

import bjut_rooms
from BJUT import BJUTjiaowu

application = Flask(__name__)  # 实例化一个程序

# 数据库文件的路径
DstDir = os.getcwd()  # 项目根目录
DATABASE_URI = DstDir+"/freeRoom.db"


# 连接数据库
@application.before_request
def before_request():
    g.db = sqlite3.connect(DATABASE_URI)


# 关闭数据库
@application.teardown_request
def teardown_request(exception):
    if hasattr(g, 'db'):
        g.db.close()


# 主页
@application.route('/')
def index():
    return "<h1 style='color:blue'>智慧北工大</h1>"


# 获取学生基本信息
@application.route('/baseinfo', methods=['POST'])
def baseinfo():
    studentNumber = request.form.get("xh")
    password = request.form.get("mm")

    bjut = BJUTjiaowu()
    isLogin = bjut.loginNoCheckcode(studentNumber, password)  # 登录

    if isLogin is True:
        '登录成功'
        baseInfo = bjut.getBaseInfo()  # 基本信息
        return jsonify(baseInfo)
    else:
        resp = make_response('请检查学号，密码是否正确')  # 自定义响应体
        resp.status = '400'  # 自定义响应状态码
        return resp


# 查课表信息
@application.route('/schedule', methods=['POST'])
def schedule():
    studentNumber = request.form.get("xh")
    password = request.form.get("mm")
    xn = request.form.get("xn")
    xq = request.form.get("xq")

    bjut = BJUTjiaowu()
    isLogin = bjut.loginNoCheckcode(studentNumber, password)  # 登录
    if isLogin is True:
        '登录成功'
        table = bjut.getSchedule(xn, xq)    # 课表
        return jsonify(table)
    else:
        resp = make_response('请检查学号，密码是否正确')  # 自定义响应体
        resp.status = '400'  # 自定义响应状态码
        return resp


# 考试信息查询
@application.route('/examination', methods=['POST'])
def examination():
    studentNumber = request.form.get("xh")
    password = request.form.get("mm")

    bjut = BJUTjiaowu()
    isLogin = bjut.loginNoCheckcode(studentNumber, password)  # 登录
    if isLogin is True:
        '登录成功'
        examInfo = bjut.getExamination()
        return jsonify(examInfo)
    else:
        resp = make_response('请检查学号，密码是否正确')  # 自定义响应体
        resp.status = '400'  # 自定义响应状态码
        return resp


# 等级考试查询
@application.route('/grade', methods=['POST'])
def gradeinfo():
    studentNumber = request.form.get("xh")
    password = request.form.get("mm")

    bjut = BJUTjiaowu()
    isLogin = bjut.loginNoCheckcode(studentNumber, password)  # 登录
    if isLogin is True:
        '登录成功'
        examInfo = bjut.getGradeExam()
        return jsonify(examInfo)
    else:
        resp = make_response('请检查学号，密码是否正确')  # 自定义响应体
        resp.status = '400'  # 自定义响应状态码
        return resp


# 成绩查询
@application.route('/score', methods=['POST'])
def score():
    studentNumber = request.form.get("xh")
    password = request.form.get("mm")
    xn = request.form.get("xn")
    xq = request.form.get("xq")

    bjut = BJUTjiaowu()
    isLogin = bjut.loginNoCheckcode(studentNumber, password)  # 登录
    if isLogin is True:
        '登录成功'
        score = bjut.getScore(xn=xn, xq=xq)  # 查成绩
        return(jsonify(score))
    else:
        resp = make_response('请检查学号，密码是否正确')  # 自定义响应体
        resp.status = '400'  # 自定义响应状态码
        return resp


# 查空教室信息
# http://127.0.0.1:5000/freeroom?building=1&week=%e4%b8%80&currentweek=8&time1=1&time2=2
@application.route("/freeroom")
def freeroom():
    '查询空教室信息'

    building = 'classroom'+request.args.get('building')  # 教学楼
    week = '"星期'+request.args.get('week')+'"'          # 星期
    currentweek = request.args.get('currentweek')         # 当前周

    time1 = str(request.args.get('time1'))
    time2 = str(request.args.get('time2'))
    times = []
    if time1 == '1' and time2 == '4':
        times = ['"第1,2节"', '"第3,4节"']  # 上午
    elif time1 == '5' and time2 == '8':
        times = ['"第5,6节"', '"第7,8节"']  # 下午
    elif time1 == '9' and time2 == '12':
        times = ['"第9,10节"', '"第11,12节"']  # 晚上
    else:
        times = ['"第'+time1+','+time2+'节"', '""']

    timeValue = '('+times[0]+','+times[1]+')'

    if (week == '"星期六"' or week == '"星期日"') and building == 'classroom1':
        return jsonify(['正常情况，一教周末只有二三层小教室开放，节假日除外'])
    elif (week == '"星期六"' or week == '"星期日"') and building == 'classroom4':
        return jsonify(['正常情况，四教周末3，4，5层开放，节假日除外'])
    else:   # 写这样的SQL真是难受死了
        rooms = g.db.execute('select room FROM '+building+' \
            WHERE week='+week+' \
                AND '+currentweek+' BETWEEN week1 AND week2 \
                    AND time in '+timeValue)

        tempList = []
        temp = []

        for r in rooms:
            tempstr = "".join(tuple(r))
            tempList.append(tempstr)
            temp = list(set(tempList))  # 去重复元素
            temp.sort()  # 排序

        if building == 'classroom1':
            room = list(set(bjut_rooms.classroom1).difference(
                set(temp)))  # 可以自习的教室-有课的教室=空闲教室
            room.sort()
            return jsonify(room)
        elif building == 'classroom3':
            room = list(set(bjut_rooms.classroom3).difference(set(temp)))
            room.sort()
            return jsonify(room)
        else:
            for t in temp:
                for c in bjut_rooms.classroom4:
                    if t in c:
                        bjut_rooms.classroom4.remove(c)
            return jsonify(bjut_rooms.classroom4)


# 服务器开始运行
if __name__ == '__main__':
    application.run(debug=True)
