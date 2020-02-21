from BJUT import Student

stu = Student()
stu.login('16041527','xf408408','xf408408') #模拟登录

print(stu.name + '\n' + stu.name + '\n')

stu.get_base_info() #获取学生基本信息
print(stu.college + '\n' + stu.major + '\n' + stu.class_name + '\n')

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