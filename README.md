# autoBuild
Auto update svn source code ->build apk -> submit apk->send emails to testers.

Run:
just place all 3 files together, and open cmd run command: python autoBuild.py.

example Settings:

0. 版本控制: apk是生成release版, 还是debug版
1. apk源码SVN远端地址: https://192.168.1.0/svn/test3.1/test3.1/trunk;
2. apk源码SVN本地根目录: C:\SVNAndroidSourceCode3.1;
3. 生成apk的所在的本地目录: C:\SVNAndroidSourceCode3.1\cyb\build\outputs\apk;
4. apk生成后在本地哪儿提交: C:\SVNProject\testForAutomation;
5. 生成的apk所在的SVN远端地址: https://192.168.1.0/svn/TestTM/Android待测/advertise/;
6. 循环任务时间: 暂时无用;
7. 邮件服务器地址: 发送邮件用到的服务器地址;
8. 邮件发送者账户名: xxx@123.com;
9. 邮件发送者密码: xxxx;
10. 邮件接收者: (逗号分隔)123@123.com,456@456.com;
11. 邮件正文前缀: "最新版本已发布, 主要修改为xxx. apk地址如下:\n"
12. 流程控制: (需要做哪些步骤)
13. 保存配置: 保存配置到配置文件,方便下次直接读取;
14. 手动执行(一次): 点击后, 触发所有勾选流程, 从前到后.
15. 最右侧为实时日志区.方便查看.



