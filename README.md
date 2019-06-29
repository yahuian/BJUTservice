# BJUTservice
## 项目简介
本项目为微信小程序“工大小美”基础查询模块的后端代码。前端小程序[WE-BJUT](https://github.com/xiefeifeigithub/WE-BJUT)

![工大小美首页图片](https://github.com/YahuiAn/BJUTservice/raw/master/images/%E5%B7%A5%E5%A4%A7%E5%B0%8F%E7%BE%8E.png)
## 功能简介
**课表**：可以查询任意学年，任意学期的课表

**空教室**：可以查询空教室（本部一教，三教，四教）

**成绩**：可以查询任意学年，任意学期的成绩，包含学期加权平均分和GPA，以及大学总加权平均分和GPA的计算

**考试**：可以查看考试安排信息（注：只有教务系统中被录入的考试课程才可查询）

**等级考试**：可以查看CET考试的成绩（注：只有教务系统中被录入的成绩才可查询）
## 项目结构
images（展示图片）
- BJUTsevice结构图.png
- 工大小美.png

tools（该项目中用到的小工具）
- excel-db.py（有段时间教务系统中查空教室功能无法使用，该工具就是将全校本科生课程安排表数据读入到SQLite数据库）

BJUT.py（核心爬虫）

app.py（flask程序）
## 依赖项目
**反向代理**：[公网直接上教务系统](https://ibjut.cn)，项目地址[Reverse-Proxy-of-BJUT-gdjwgl](https://github.com/ZenBuilds/Reverse-Proxy-of-BJUT-gdjwgl)
## 特别鸣谢
**工大助手**：本项目的前身是[《工大助手》](https://github.com/cjw1115/BJUTHelper)项目，原本为C#写的跨平台APP，本项目用python对其核心功能进行重写。

**野生工大助手**：感谢[《野生工大助手》](https://github.com/wangyufeng0615/bjuthelper)项目中的无验证码登陆接口，让我们可以无需输入验证码即可登陆教务管理系统，用户体验非常好。
## 项目总体架构
![项目结构图](https://github.com/YahuiAn/BJUTservice/raw/master/images/BJUTservice%E7%BB%93%E6%9E%84%E5%9B%BE.png)

本项目位于Python爬虫数据解析模块
## 项目资源总结
**微信小程序**：[WE-BJUT](https://github.com/xiefeifeigithub/WE-BJUT)

**Python后端**：[BJUTservice](https://github.com/yahuian/BJUTservice)

**反向代理**：[Reverse-Proxy-of-BJUT-gdjwgl](https://github.com/ZenBuilds/Reverse-Proxy-of-BJUT-gdjwgl)

**工大助手**：[BJUTHelper](https://github.com/cjw1115/BJUTHelper)

**野生工大助手**：[bjuthtlper](https://github.com/wangyufeng0615/bjuthelper)