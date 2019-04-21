# CrazyliuBlog
刚学了点Flask，练练手做个记录自己的博客，顺便放些实用的小工具
目前想到的做的模块如下，后面会陆续更新

## 1. 用户认证
1. 用户登录
2. 用户登出
3. 用户注册
4. 修改密码
5. 重设密码
6. 修改邮件地址

## 2. 发表文章
1. 写文章
2. 修改文章
3. 查看文章
4. ..

## 3. 用户主页
1. 管理自己的文章 查看，修改，删除，修改文章状态
2. 查看自己的个人资料并修改
3. 查看自己关注的人的文章
4. 查看自己关注的人
5. 查看粉丝
6. 总览Overview

## 4. 实用工具
1. 条形码生成工具 包含单个和批量
2. 

## 5. api接口
1. 分成三部分 error, data, message
error为状态码，空表示成功，其他含义与HTTP协议状态码含义类似
401 未认证 402 注册失败
500 Internal Server Error
404 Not Found



2. api<br>
2.1 认证部分
/user/login
/user/register
/user/logout
/auth/validate_code

2.2 用户部分<br>
/user
/user/<<'id'>>
/user

2.3 文章部分

