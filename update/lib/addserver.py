#/usr/bin/env python
#-*- coding:utf-8 -*-
#Authot:Zhang Yan

import subprocess,paramiko,sys,os

class AddServer:
    def __init__(self,mod_name,ip_list,restart,dns,vol_list,port_list,hostname,option,port,user,password,lb_ip_list,logger_root,logger_console):
        self.mod_name=mod_name
        self.ip_list=ip_list
        self.port=port
        self.user=user
        self.password=password
        self.restart = restart
        self.dns = dns
        self.vol_list = vol_list
        self.port_list = port_list
        self.hostname = hostname
        self.option = option
        self.lb_ip_list=lb_ip_list
        self.logger_root=logger_root
        self.logger_console=logger_console
    def run_comm(self,cmd):
        p = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
        out = p.stdout.read()
        return out
    def run_command(self,ip,cmd):
        client = paramiko.SSHClient()
        client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        client.load_system_host_keys()
        client.connect(hostname=ip, port=self.port, username=self.user, password=self.password)
        stdin, stdout, stderr = client.exec_command(cmd)
        stdin.write("%s\n" % (self.password))  # 这两行是执行sudo命令要求输入密码时需要的
        stdin.flush()  # 执行普通命令的话不需要这两行
        self.logger_console.error(stderr.read())
        self.logger_root.error(stderr.read())
        if stdout == "stdout":
            self.logger_root.info(stdout.read())
        else:
            return stdout.read()
        client.close()
    def common_func(self):
        for ip in self.lb_ip_list:
            cmd = 'sudo confd -onetime -backend etcd -node http://xxx:4001'
            self.logger_root.info(cmd)
            self.logger_console.info(cmd)
            self.run_command(ip, cmd)

    def add_server(self):
        ip_s=self.ip_list[0]
        ip_d_list=self.ip_list[1:]
        cmd="sudo docker ps | grep %s | awk '{print $2}'" % self.mod_name
        self.logger_root.info(cmd)
        self.logger_console.info(cmd)
        branch=self.run_command(ip_s,cmd)
        for ip_d in ip_d_list:
            cmd = "df -h | grep ossfs | awk '{print $1}'"
            out = self.run_command(ip_d, cmd)
            if "ossfs" not in out:
                self.logger_console.info("[%s]未挂载oss!如需挂载请用salt进行挂载!" % ip_d )
                self.logger_root.info("[%s]未挂载oss!如需挂载请用salt进行挂载!" % ip_d )
            cmd = "sudo docker ps | grep %s | grep -v grep" % branch
            self.logger_root.info(cmd)
            out = self.run_command(ip_d, cmd)
            if out == "":
                cmd="sudo docker pull %s" % branch
                self.logger_root.info(cmd)
                self.run_command(ip_d,cmd)
                cmd = "sudo docker images | grep %s" % self.mod_name
                self.logger_root.info(cmd)
                out = self.run_command(ip_d,cmd)
                if out == "":
                    self.logger_root.error("[%s] image pull fail!" % self.mod_name)
                    self.logger_console.error("[%s] image pull fail!" % self.mod_name)
                    sys.exit()
                else:
                    self.logger_root.info("[%s] image pull sucess!" % self.mod_name)
                cmd = "sudo docker ps -a | grep %s" % self.mod_name
                self.logger_root.info(cmd)
                out = self.run_command(ip_d,cmd)
                if out == "":
                    pass
                else:
                    cmd = "sudo docker stop %s" % self.mod_name
                    self.logger_root.info(cmd)
                    self.run_command(ip_d,cmd)
                    cmd = "sudo docker rm %s" % self.mod_name
                    self.logger_root.info(cmd)
                    self.run_command(ip_d,cmd)
                if len(self.vol_list) == 0:
                    vol = ""
                else:
                    aa = " -v ".join(self.vol_list)
                    vol = "-v %s" % aa
                    for i in self.vol_list:
                        # /home/data/gxb-web/logs/:/usr/local/tomcat/logs/:rw
                        dir = i.split(":")[0]
                        cmd = "[ -d %s ] || mkdir %s" % (dir, dir)
                        self.run_command(ip_d,cmd)
                if len(self.port_list) == 0:
                    export = ""
                else:
                    bb = " -p ".join(self.port_list)
                    export = "-p %s" % bb
                    for i in self.port_list:
                        port = i.split(":")[0]
                        cmd = "/usr/sbin/lsof -i:%s | grep -i LISTEN" % port
                        out = self.run_command(ip_d,cmd)
                        if out == "":
                            pass
                        else:
                            self.logger_root.error("容器绑定的宿主机端口已被占用!")
                            self.logger_console.error("容器绑定的宿主机端口已被占用!")
                            sys.exit()
                if self.hostname == "":
                    host = ""
                else:
                    host = "--hostname=%s" % self.hostname
                if self.dns == "":
                    dns = ""
                else:
                    dns = "--dns=%s" % self.dns
                cmd = "sudo docker run -d  --restart=%s %s %s %s %s %s --privileged --name %s %s" % (
                    self.restart, dns, host, vol, export, self.option, self.mod_name, branch)
                self.logger_root.info(cmd)
                self.run_command(ip_d,cmd)
                cmd = "sudo docker ps | grep %s | grep Up" % self.mod_name
                self.logger_root.info(cmd)
                out = self.run_command(ip_d,cmd)
                if out.strip() == "":
                    self.logger_root.error("[%s] container run fail!" % self.mod_name)
                    self.logger_console.error("[%s] container run fail!" % self.mod_name)
                    sys.exit()
                else:
                    self.logger_root.info("[%s] container run sucess!" % self.mod_name)
                    cmd = '''sudo sh -c "docker images | grep %s | grep -v %s | awk '{print $3}' | sort | uniq | xargs docker rmi -f"''' % (
                    self.mod_name, branch)
                    self.logger_root.info(cmd)
                    try:
                        self.run_command(ip_d,cmd)
                    except Exception as e:
                        self.logger_root.error(e)
                        self.logger_console.error(e)
            cmd='etcdctl set /nginx/%s/%s %s' % (self.mod_name,ip_d,ip_d)
            self.logger_root.info(cmd)
            self.run_comm(cmd)
            self.common_func()
    def dec_server(self):
        if self.mod_name == "common" or self.mod_name == "mysql" or self.mod_name == "redis" or self.mod_name == "docker" or self.mod_name == "lb":
            pass
        else:
            cmd = "etcdctl ls /nginx/%s | awk -F '/' '{print $4}'" % self.mod_name
            out = self.run_comm(cmd)
            etcd_ip_list = out.strip().split("\n")
            self.logger_root.info("nginx现在的机器: %s" % str(etcd_ip_list))
            self.logger_root.info("nginx需要的机器: %s" % str(self.ip_list))
            mod_ip_set = set(self.ip_list)
            etcd_ip_set = set(etcd_ip_list)
            add_list = list(mod_ip_set.difference(etcd_ip_set))
            del_list = list(etcd_ip_set.difference(mod_ip_set))
            self.logger_root.info("nginx添加的机器: %s" % str(add_list))
            self.logger_root.info("nginx删除的机器: %s" % str(del_list))
            for ip in add_list:
                cmd = 'etcdctl set /nginx/%s/%s %s' % (self.mod_name, ip, ip)
                out = self.run_comm(cmd)
            for ip in del_list:
                cmd = 'etcdctl rm /nginx/%s/%s' % (self.mod_name, ip)
                out = self.run_comm(cmd)
                self.common_func()
                cmd = "sudo docker ps -a | grep %s" % self.mod_name
                self.logger_root.info(cmd)
                out = self.run_command(ip,cmd)
                if out == "":
                    pass
                else:
                    cmd = "sudo docker stop %s" % self.mod_name
                    self.logger_root.info(cmd)
                    self.run_command(ip,cmd)
                    cmd = "sudo docker rm %s" % self.mod_name
                    self.logger_root.info(cmd)
                    self.run_command(ip,cmd)

