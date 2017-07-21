#/usr/bin/env python
#-*- coding:utf-8 -*-
#Authot:Zhang Yan

import json,requests,os,sys,subprocess,pymysql
from ConfigParser import ConfigParser
import redis

class CheckStatus:
    def __init__(self,host="",port="",user="",password="",dbname="",url="",keyword="",logger_root='',logger_console=''):
        self.host=host
        self.port=port
        self.url="http://%s:%s/%s" % (host,port,url)
        self.keyword=keyword
        self.user=user
        self.password=password
        self.dbname=dbname
        self.logger_root=logger_root
        self.logger_console=logger_console

    def check_status(self):
        cmd = 'curl -XGET -m 10 -s -w "\n%%{http_code}\n%%{time_total}\n" %s' % self.url
        p = subprocess.Popen(cmd,shell=True,stdout=subprocess.PIPE,stderr=subprocess.STDOUT)
        out = p.stdout.read()
        out_list=out.split("\n")
        http_code=out_list[-3]
        response_time=out_list[-2]
        self.logger_root.info("[%s] http_code: %s" % (self.host,http_code))
        self.logger_root.info("[%s] response_time: %s" % (self.host,response_time))
        if self.keyword == "number" and out_list[0].isdigit():
            return True
        elif self.keyword in out:
            return True
    def check_login(self):
        values = {"userName": "18210413017", "password": "123456", "tenantId": "301"}
        headers = {"Content-Type": "application/json", "Cache-Control": "no-cache",
                   "Postman-Token": "afb42e6e-5463-3622-176f-91c8b8022dc5"}
        r = requests.post("http://gxb-app.gaoxiaobang.com/hybird-web/user/login", data=json.dumps(values), headers=headers)
        self.logger_root.info("[hybird-web login] http_code: %s" % r.status_code)
        info=r.text.encode("utf8")
        if "登录成功" in info:
            return True
        else:
            return False
    def check_redis(self):
        pool = redis.ConnectionPool(host=self.host, port=int(self.port))
        r = redis.Redis(connection_pool=pool)
        try:
            r.set("k1", "v1")
            self.logger_root.info("[%s:%s] set命令成功!" % (self.host,self.port))
            v = r.get("k1")
            if v == "v1":
                self.logger_root.info("[%s:%s] get 命令成功!" % (self.host,self.port))
                r.delete("k1")
                self.logger_root.info("[%s:%s] redis 正在运行!" % (self.host,self.port))
        except redis.exceptions.ReadOnlyError:
            self.logger_root.info("[%s:%s] 这是个只读的redis!" % (self.host,self.port))
            v = r.get("zy")
            if v == "zyzy":
                self.logger_root.info("[%s:%s] get 命令成功!" % (self.host,self.port))
    def check_mysql(self):
        conn = pymysql.connect(host=self.host, port=int(self.port), user=self.user, passwd=self.password, db=self.dbname)
        cursor = conn.cursor()
        self.logger_root.info("[%s] 创建表!" % self.host)
        try:
            cursor.execute("create table zy(id int,name varchar(20))")
            effect_row = cursor.execute("insert into zy values (1,'zyzy')")
            if effect_row == 1: self.logger_root.info("[%s] 插入数据成功!" % self.host)
            cursor.execute("select * from zy")
            row_1 = cursor.fetchone()
            if row_1 == (1, 'zyzy'): self.logger_root.info("[%s] 查询数据成功!" % self.host)
            self.logger_root.info("[%s] 删除表!" % self.host)
            cursor.execute("drop table zy")
        except pymysql.err.InternalError as e:
            if e[0] == 1290:
                self.logger_root.info("[%s] 这是个只读库!" % self.host)
                cursor.execute("select school_id from gxb_core.school_host where school_host_id=2")
                row_1 = cursor.fetchone()
                if row_1 == (109,): self.logger_root.info("[%s] 查询数据成功!" % self.host)
        cursor.close()
        conn.close()

src_dir=os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
conf_file=src_dir + "/conf/mod.ini"
cf=ConfigParser()
cf.read(conf_file)
def check_all_server():
    mod_list = cf.sections()
    s_field="|"
    for mod in mod_list:
        if mod == "example" or mod == "common" or mod == "docker" or mod == "lb":
            continue
        self.logger_root.warning("------%s-------" % mod)
        if mod == "redis":
            if cf.has_option(mod,"ip"):
                ip_list = cf.get(mod, 'ip').split(s_field)
            else:
                self.logger_root.error("[%s] 必须设置redis服务器的ip" % mod)
                self.logger_console.error("[%s] 必须设置redis服务器的ip" % mod)
                sys.exit("update failure")
            if cf.has_option(mod,"port"):
                port_list = cf.get(mod,"port").split(s_field)
            else:
                self.logger_root.error("[%s] 必须设置redis服务器的port" % mod)
                self.logger_console.error("[%s] 必须设置redis服务器的port" % mod)
                sys.exit("update failure")
            index = 0
            for ip in ip_list:
                if len(port_list) == 1:
                    port=port_list[0]
                else:
                    port=port_list[index]
                obj = CheckStatus(host=ip,port=int(port))
                obj.check_redis()
                index += 1
        elif mod == "mysql":
            if cf.has_option(mod,"ip"):
                ip_list = cf.get(mod, "ip").split(s_field)
            else:
                self.logger_root.error("[%s] 必须设置mysql服务器的ip" % mod)
                self.logger_console.error("[%s] 必须设置mysql服务器的ip" % mod)
                sys.exit("update failure")
            if cf.has_option(mod, "port"):
                port_list = cf.get(mod, "port").split(s_field)
            else:
                self.logger_root.error("[%s] 必须设置mysql服务器的port" % mod)
                self.logger_console.error("[%s] 必须设置mysql服务器的port" % mod)
                sys.exit("update failure")
            if cf.has_option(mod,"user"):
                user_list = cf.get(mod,"user").split(s_field)
            else:
                self.logger_root.error("[%s] 必须设置mysql服务器的user" % mod)
                self.logger_console.error("[%s] 必须设置mysql服务器的user" % mod)
                sys.exit("update failure")
            if cf.has_option(mod, "password"):
                pwd_list = cf.get(mod, "password").split(s_field)
            else:
                self.logger_root.error("[%s] 必须设置mysql服务器的password" % mod)
                self.logger_console.error("[%s] 必须设置mysql服务器的password" % mod)
                sys.exit("update failure")
            if cf.has_option(mod, "dbname"):
                dbname_list = cf.get(mod, "dbname").split(s_field)
            else:
                self.logger_root.info("[%s] 必须设置mysql服务器的dbname" % mod)
                sys.exit()
            for ip in ip_list:
                ip_index = ip_list.index(ip)
                if len(port_list) == 1:
                    port = int(port_list[0])
                else:
                    port = int(port_list[ip_index])
                if len(user_list) == 1:
                    user = user_list[0]
                else:
                    user = user_list[ip_index]
                if len(pwd_list) == 1:
                    password = pwd_list[0]
                else:
                    password = port_list[ip_index]
                if len(dbname_list) == 1:
                    dbname = dbname_list[0]
                else:
                    dbname = dbname_list[ip_index]
                obj = CheckStatus(host=ip,port=port,user=user,password=password,dbname=dbname)
                obj.check_mysql()
        else:
            if cf.has_option(mod, "ip"):
                ip_list = cf.get(mod, "ip").split(s_field)
            else:
                self.logger_root.info("[%s] 必须设置服务器的ip" % mod)
                sys.exit()
            if cf.has_option(mod, "port_list"):
                port_list = cf.get(mod, "port_list")
            else:
                self.logger_root.info("[%s] 必须设置服务器的监听port" % mod)
                sys.exit()
            port = port_list.split(":")[0]
            if cf.has_option(mod, "check_url"):
                url = cf.get(mod, "check_url")
            else:
                self.logger_root.info("[%s] 没有设置监控的url!" % mod)
                url = ""
            if cf.has_option(mod, "key_word"):
                keyword = cf.get(mod, "key_word")
            else:
                self.logger_root.info("[%s] 没有设置监控的关键字!" % mod)
                keyword = ""
            if mod == "hybird-web":
                obj = CheckStatus()
                obj.check_login()
            for ip in ip_list:
                if url != "" and keyword != "":
                    obj=CheckStatus(host=ip,port=str(port),url=url,keyword=keyword)
                    if obj.check_status():
                        self.logger_root.info("[%s] API 调用成功!" % ip)
                    else:
                        self.logger_root.error("[%s] API 调用失败!" % ip)
                        self.logger_console.error("[%s] API 调用失败!" % ip)

