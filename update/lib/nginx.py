#!/usr/bin/env python
# -*- coding: utf-8 -*-
#Author ZhangYan

import paramiko


class nginx():
    def __init__(self,ip_list,port,user,path,ser_port,nginx_cmd,logger_root,logger_console,password="",ssh_key=""):
        self.ip_list = ip_list
        self.port = port
        self.user = user
        self.pasword =password
        self.path = path
        self.ser_port = ser_port
        self.ssh_key = ssh_key
        self.nginx_cmd = nginx_cmd
        self.logger_root=logger_root
        self.logger_console=logger_console


    def run_command(self,cmd,ip):
        client=paramiko.SSHClient()
        client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        client.load_system_host_keys()
        if self.ssh_key != "":
            pkey = self.ssh_key
            key = paramiko.RSAKey.from_private_key_file(pkey)
            client.connect(hostname=ip, port=self.port, username=self.user, pkey=key)
        else:
            client.connect(hostname=ip,port=self.port,username=self.user,password=self.pasword)
        stdin,stdout,stderr = client.exec_command(cmd)
        stdin.write("%s\n" % (self.pasword))  #这两行是执行sudo命令要求输入密码时需要的
        stdin.flush()                         #执行普通命令的话不需要这两行
        self.logger_console.error(stderr.read())
        self.logger_root.error(stderr.read())
        if stdout == "stdout":
            pass
        else:
            return stdout.read()
        client.close()


    def add(self,mod_ip):
        for ip in self.ip_list:
            nginx_path=self.path
            cmd = "grep 'server %s:%s' %s" % (mod_ip,self.ser_port,nginx_path)
            out = self.run_command(cmd,ip)
            if out != '':
                cmd = "grep 'server %s:%s' %s | grep '#' "  % (mod_ip, self.ser_port, nginx_path)
                out = self.run_command(cmd, ip)
                if out == '': #如果没有注释的话就加注释
                    self.logger_root.info("[%s] add #" % mod_ip)
                    self.logger_console.info("[%s] add #" % mod_ip)
                    cmd = "sudo sed -i 's/server %s:%s/#server %s:%s/' %s" % (mod_ip,self.ser_port,mod_ip,self.ser_port,nginx_path)
                    self.run_command(cmd,ip)
                    cmd = self.nginx_cmd
                    self.run_command(cmd,ip)
                    self.logger_root.info("[%s] add sucessful!" % mod_ip)
                    self.logger_console.info("[%s] add sucessful!" % mod_ip)


    def dec(self,mod_ip):
        for ip in self.ip_list:
            nginx_path=self.path
            cmd = "grep 'server %s:%s' %s" % (mod_ip,self.ser_port,nginx_path)
            out = self.run_command(cmd,ip)
            if out != '':
                self.logger_root.info("[%s] dec #" % mod_ip)
                self.logger_console.info("[%s] dec #" % mod_ip)
                cmd = "sudo grep 'server %s:%s' %s | grep '#' " % (mod_ip,self.ser_port,nginx_path)
                out = self.run_command(cmd,ip)
                if out != '':  #如果有注释的话就去掉注释
                    cmd = "sudo sed -i 's/#server %s:%s/server %s:%s/' %s" % (mod_ip,self.ser_port,mod_ip,self.ser_port,nginx_path)
                    self.run_command(cmd,ip)
                    cmd = self.nginx_cmd
                    self.run_command(cmd,ip)
                    self.logger_root.info("[%s] dec sucessful!" % mod_ip)
                    self.logger_console.info("[%s] dec sucessful!" % mod_ip)


