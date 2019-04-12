from BJUT import BJUTjiaowu

bjut=BJUTjiaowu()

sessionID=bjut.getCheckCode() # 获取验证码
print(sessionID)
print('请输入验证码：')
checkCode=input()
#tryLogin=bjut.login('16010328','281205ayh23/',checkCode) # 登录教务管理
tryLogin=bjut.login('17167111','zxc31263600.',checkCode)
print(tryLogin)
bjut.getSchedule() # 获取课程表