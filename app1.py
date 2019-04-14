'''
该版本为无验证码版
'''
from BJUT import BJUTjiaowu
from flask import Flask, request,jsonify,make_response

application = Flask(__name__) # 实例化一个程序

# 主页
@application.route('/')
def index():
    return "<h1 style='color:blue'>智慧北工大</h1>"

# 查课表信息
# http://127.0.0.1:5000/schedule?xh=16010328&mm=281205ayh23
@application.route('/schedule')
def schedule():
    studentNumber = request.args.get("xh")
    password = request.args.get("mm")

    bjut=BJUTjiaowu()
    isLogin=bjut.loginNoCheckcode(studentNumber,password) # 登录
    if isLogin==True:
        '登录成功'
        baseInfo=bjut.getBaseInfo() # 基本信息
        table=bjut.getSchedule()    # 课表
        temp=[baseInfo,table]
        return jsonify(temp)
    else:
        resp=make_response('请检查学号，密码是否正确') #自定义响应体
        resp.status='400' # 自定义响应状态码
        return resp

# 服务器开始运行
if __name__ == '__main__':
    application.run('0.0.0.0')