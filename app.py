from flask import Flask, jsonify, make_response, request

from BJUT import Student

application = Flask(__name__)  # 实例化一个程序


# 主页
@application.route('/')
def index():
    return "<h1 style='color:blue'>智慧北工大</h1>"


# 获取学生基本信息
@application.route('/baseinfo', methods=['POST'])
def base_info():
    number = request.form.get('xh')
    password = request.form.get('mm')
    stu = Student()
    login = stu.login_vpn(number, password)

    if not login:
        resp = make_response('请检查学号，密码是否正确')  # 自定义响应体
        resp.status = '400'  # 自定义响应状态码
        return resp

    if stu.get_base_info():
        info = {
            'class': stu.class_name,
            'college': stu.college,
            'major': stu.major,
            'stuNum': stu.number,
            'sutName': stu.name,
        }
        return jsonify(info)
    else:
        resp = make_response('获取学生基本信息失败')
        resp.status = '500'
        return resp


# 查课表信息
@application.route('/schedule', methods=['POST'])
def schedule():
    number = request.form.get('xh')
    password = request.form.get('mm')
    xn = request.form.get("xn")
    xq = request.form.get("xq")

    stu = Student()
    login = stu.login_vpn(number, password)

    if not login:
        resp = make_response('请检查学号，密码是否正确')  # 自定义响应体
        resp.status = '400'  # 自定义响应状态码
        return resp

    info_schedule = stu.get_schedule(xn=xn, xq=xq)
    if info_schedule:
        return jsonify(info_schedule)
    else:
        return jsonify({'schedule':'no_schedule'})


# 考试信息查询
@application.route('/examination', methods=['POST'])
def examination():
    number = request.form.get("xh")
    password = request.form.get("mm")

    stu = Student()
    login = stu.login_vpn(number, password)

    if not login:
        resp = make_response('请检查学号，密码是否正确')  # 自定义响应体
        resp.status = '400'  # 自定义响应状态码
        return resp

    info_examination = stu.get_examination()
    if info_examination:
        return jsonify(info_examination)
    else:
        return jsonify({'examination': 'no_examination'})


# CET考试查询
@application.route('/cet', methods=['POST'])
def cet_info():
    number = request.form.get("xh")
    password = request.form.get("mm")

    stu = Student()
    login = stu.login_vpn(number, password)

    if not login:
        resp = make_response('请检查学号，密码是否正确')  # 自定义响应体
        resp.status = '400'  # 自定义响应状态码
        return resp

    info_cet = stu.get_CET_exam()
    if info_cet:
        return jsonify(info_cet)
    else:
        return jsonify({'grade':'no_grade'})

# 成绩查询
@application.route('/score', methods=['POST'])
def score():
    number = request.form.get("xh")
    password = request.form.get("mm")
    xn = request.form.get("xn")
    xq = request.form.get("xq")

    stu = Student()
    login = stu.login_vpn(number, password)

    if not login:
        resp = make_response('请检查学号，密码是否正确')  # 自定义响应体
        resp.status = '400'  # 自定义响应状态码
        return resp

    info_score = stu.get_score(xn=xn, xq=xq)
    if info_score:
        return jsonify(info_score)
    else:
        return jsonify({'score':'no_score'})


# 服务器开始运行
if __name__ == '__main__':
    application.run(debug=False)
