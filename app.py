from flask import Flask, jsonify, make_response, request

from BJUT import Student

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
    stu = Student()
    login = stu.login_without_code(number, password)

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
        resp = make_response('获取学生基本信息错误')
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
    login = stu.login_without_code(number, password)

    if not login:
        resp = make_response('请检查学号，密码是否正确')  # 自定义响应体
        resp.status = '400'  # 自定义响应状态码
        return resp

    info = stu.get_schedule(xn=xn, xq=xq)
    return jsonify(info)


# 考试信息查询
@application.route('/examination', methods=['POST'])
def examination():
    number = request.form.get("xh")
    password = request.form.get("mm")

    stu = Student()
    login = stu.login_without_code(number, password)

    if not login:
        resp = make_response('请检查学号，密码是否正确')  # 自定义响应体
        resp.status = '400'  # 自定义响应状态码
        return resp

    info = stu.get_examination()
    return jsonify(info)


# 等级考试查询
@application.route('/grade', methods=['POST'])
def grade_info():
    number = request.form.get("xh")
    password = request.form.get("mm")

    stu = Student()
    login = stu.login_without_code(number, password)

    if not login:
        resp = make_response('请检查学号，密码是否正确')  # 自定义响应体
        resp.status = '400'  # 自定义响应状态码
        return resp

    info = stu.get_grade_exam()
    return jsonify(info)


# 成绩查询
@application.route('/score', methods=['POST'])
def score():
    number = request.form.get("xh")
    password = request.form.get("mm")
    xn = request.form.get("xn")
    xq = request.form.get("xq")

    stu = Student()
    login = stu.login_without_code(number, password)

    if not login:
        resp = make_response('请检查学号，密码是否正确')  # 自定义响应体
        resp.status = '400'  # 自定义响应状态码
        return resp

    info = stu.get_score(xn=xn, xq=xq)
    return jsonify(info)


# 服务器开始运行
if __name__ == '__main__':
    application.run(debug=False)
