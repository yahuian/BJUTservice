import logging

from flask import Flask, jsonify, make_response, request

from BJUT import Student
from logger import log

application = Flask(__name__)  # 实例化一个程序


# 主页
@application.route('/')
def index():
    return application.send_static_file('index.html')


# 获取学生基本信息
@application.route('/baseinfo', methods=['POST'])
def base_info():
    number = request.form.get('xh')
    password = request.form.get('mm')
    vpn_pwd = request.form.get('vpn_pwd')
    stu = Student()
    try:
        stu.login(number, vpn_pwd, password)
        stu.get_base_info()
    except Exception as e:
        resp = make_response({'msg': str(e)})
        resp.status = '500'
        return resp

    info = {
        'class': stu.class_name,
        'college': stu.college,
        'major': stu.major,
        'stuNum': stu.number,
        'sutName': stu.name,
    }
    return jsonify(info)


# 查课表信息
@application.route('/schedule', methods=['POST'])
def schedule():
    number = request.form.get('xh')
    password = request.form.get('mm')
    vpn_pwd = request.form.get('vpn_pwd')
    xn = request.form.get("xn")
    xq = request.form.get("xq")

    stu = Student()
    try:
        stu.login(number, vpn_pwd, password)
        schedule = stu.get_schedule(xn, xq)
    except Exception as e:
        log.error(str(e))
        resp = make_response({'msg': str(e)})
        resp.status = '500'
        return resp

    return jsonify(schedule)


# 考试信息查询
@application.route('/examination', methods=['POST'])
def examination():
    number = request.form.get("xh")
    password = request.form.get("mm")
    vpn_pwd = request.form.get('vpn_pwd')

    stu = Student()
    try:
        stu.login(number, vpn_pwd, password)
        exam = stu.get_examination()
    except Exception as e:
        log.error(str(e))
        resp = make_response({'msg': str(e)})
        resp.status = '500'
        return resp

    return jsonify(exam)


# CET考试查询
@application.route('/cet', methods=['POST'])
def cet_info():
    number = request.form.get("xh")
    password = request.form.get("mm")
    vpn_pwd = request.form.get('vpn_pwd')

    stu = Student()
    try:
        stu.login(number, vpn_pwd, password)
        exam = stu.get_CET_exam()
    except Exception as e:
        log.error(str(e))
        resp = make_response({'msg': str(e)})
        resp.status = '500'
        return resp

    return jsonify(exam)


# 成绩查询
@application.route('/score', methods=['POST'])
def score():
    number = request.form.get("xh")
    password = request.form.get("mm")
    vpn_pwd = request.form.get('vpn_pwd')
    xn = request.form.get("xn")
    xq = request.form.get("xq")

    stu = Student()
    try:
        stu.login(number, vpn_pwd, password)
        score = stu.get_score(xn, xq)
    except Exception as e:
        log.error(str(e))
        resp = make_response({'msg': str(e)})
        resp.status = '500'
        return resp

    return jsonify(score)


# 服务器开始运行
if __name__ == '__main__':
    application.run(debug=True)
