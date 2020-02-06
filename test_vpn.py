from BJUT import Student

stu = Student()
login = stu.login_vpn('16041527','xf408408','xf408408') #模拟登录
if login:
    print(stu.name + '\n' + stu.name + '\n')

    stu_base_info = stu.get_base_info() #获取学生基本信息
    if stu_base_info:
        print(stu.college + '\n' + stu.major + '\n' + stu.class_name + '\n')
    else:
        print('获取学生基本信息失败')
    
    stu_schedule = stu.get_schedule('2018-2019','1') #获取学生课表
    if stu_schedule:
        print(stu_schedule)
    else:
        print('获取课表失败')

    stu_score = stu.get_score('2018-2019',1)
    if stu_score:
        print(stu_score)
    else:
        print('获取成绩失败')
        
else:
    print('教务网站崩了')