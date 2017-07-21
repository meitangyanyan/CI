#/usr/bin/env python
#-*- coding:utf-8 -*-
#Authot:Zhang Yan
import subprocess,os,sys,paramiko
from ConfigParser import ConfigParser

def run_comm(cmd):
    p = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    out = p.stdout.read()
    return out
def run_command(ip,cmd):
    pwd="$1$gxb$HJONFlv7J6SvwFUj9Sidy1"
    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    client.load_system_host_keys()
    client.connect(hostname=ip, port=22, username="gxb", password=pwd)
    stdin, stdout, stderr = client.exec_command(cmd)
    stdin.write("%s\n" % (pwd))  # 这两行是执行sudo命令要求输入密码时需要的
    stdin.flush()  # 执行普通命令的话不需要这两行
    return stderr.read()

conf_file="/home/update/conf/mod.ini"
if not os.path.exists(conf_file):
    sys.exit("配置文件不存在!")
cf=ConfigParser()
cf.read(conf_file)

mod_list=cf.sections()
lb_ip_list=["lb1","lb2","lb4"]

for mod in mod_list:
    if mod == "common" or mod == "mysql" or mod == "redis" or mod == "docker" or mod == "lb":
        continue
    elif cf.has_option(mod,"ip"):
        mod_ip_list=cf.get(mod,"ip").split("|")
        cmd="etcdctl ls /nginx/%s | awk -F '/' '{print $4}'" % mod
        out=run_comm(cmd)
        etcd_ip_list = out.strip().split("\n")
        mod_ip_set=set(mod_ip_list)
        etcd_ip_set=set(etcd_ip_list)
        add_list=list(mod_ip_set.difference(etcd_ip_set))
        del_list=list(etcd_ip_set.difference(mod_ip_set))
        print "[%s] 添加: %s" % (mod,str(add_list))
        print "[%s] 删除: %s" % (mod,str(del_list))
        for ip in add_list:
            cmd = 'etcdctl set /nginx/%s/%s %s' % (mod, ip, ip)
            out = run_comm(cmd)
        for ip in del_list:
            cmd = 'etcdctl rm /nginx/%s/%s' % (mod, ip)
            out = run_comm(cmd)
for ip in lb_ip_list:
    cmd = 'sudo confd -onetime -backend etcd -node http://10.51.96.173:4001'
    out = run_command(ip,cmd)
    print out

