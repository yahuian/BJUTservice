'''
该版本为无验证码版
'''
import os
import sqlite3
from BJUT import BJUTjiaowu
from flask import Flask, request,jsonify,make_response,g

application = Flask(__name__) # 实例化一个程序

# 数据库文件的路径
DstDir = os.getcwd()
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


# 查空教室信息
# http://127.0.0.1:5000/freeroom?building=1&week=%e4%b8%80&currentweek=8&time1=1&time2=2
@application.route("/freeroom")
def freeroom():
    '查询空教室信息'
    building = 'classroom'+request.args.get('building') # 教学楼
    week ='"星期'+request.args.get('week')+'"'          # 星期
    currentweek=request.args.get('currentweek')         # 当前周 

    time1=str(request.args.get('time1'))
    time2=str(request.args.get('time2'))
    time='"*'+time1+','+time2+'*"'

    tempList=[]
    
    rooms=g.db.execute('SELECT room FROM '+building+'\
         WHERE week='+week+'\
         AND '+building+'.begin'+'<='+currentweek+'\
         AND '+building+'.end'+'>='+currentweek+'\
         AND time GLOB'+time)

    for r in rooms:
        tempstr="".join(tuple(r))
        tempList.append(tempstr[2:])
        temp=list(set(tempList)) # 去重复元素
        temp.sort() # 排序
    return jsonify(temp)


# 服务器开始运行
if __name__ == '__main__':
    application.run('0,0,0,0')