from BJUT import BJUTjiaowu

# 实例化一个对象
bjut=BJUTjiaowu()  

# 有验证码登录
'''
# 获取验证码
sessionID=bjut.getCheckCode()  
print(sessionID)

# 输入验证码
print('请输入验证码：')         
checkCode=input()

# 登录教务管理
tryLogin=bjut.login('16010328','281205ayh23',checkCode)
print(tryLogin)
'''
# 无验证码登录
tryLogin=bjut.loginNoCheckcode('16010328','281205ayh23')
print(tryLogin)

# 获取学生基本信息
info=bjut.getBaseInfo()
print('基本信息：') 
print(info)

# 获取课程表
schedule=bjut.getSchedule()
print('课程表：')
for s in schedule['table']:
    print(s)
print('实践课：')
for e in schedule['exercise']:
    print(e)