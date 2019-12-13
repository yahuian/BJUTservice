from flask import Flask, jsonify, make_response, request
from BJUT import BJUTjiaowu

application = Flask(__name__)  # 实例化一个程序

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
        return jsonify(score)
    else:
        resp = make_response('请检查学号，密码是否正确')  # 自定义响应体
        resp.status = '400'  # 自定义响应状态码
        return resp


# 服务器开始运行
if __name__ == '__main__':
    application.run(debug=True)
