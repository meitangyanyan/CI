#!/usr/bin/env python
#__*__ coding:utf-8 __*__

import paramiko
import sys,os

class Package:
    def __init__(self,ip,user,port,password,ssh_key,url,repo_path,tag,build_cmd,upload_dir,package,logger_root,logger_console,branch="master",clone_flag=0):
        self.ip=ip
        self.user=user
        self.port=port
        self.pasword=password
        self.ssh_key=ssh_key
        self.url=url
        self.clone_flag=clone_flag
        self.repo_path=repo_path
        self.branch=branch
        self.tag=tag
        self.build_cmd=build_cmd
        self.upload_dir=upload_dir
        self.package=package
        self.logger_root=logger_root
        self.logger_console=logger_console

    def run_command(self, cmd):
        client = paramiko.SSHClient()
        client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        client.load_system_host_keys()
        if self.ssh_key != "":
            pkey = self.ssh_key
            key = paramiko.RSAKey.from_private_key_file(pkey)
            client.connect(hostname=self.ip, port=self.port, username=self.user, pkey=key)
        else:
            client.connect(hostname=self.ip, port=self.port, username=self.user, password=self.pasword, timeout=10)
        stdin, stdout, stderr = client.exec_command(cmd)
        if self.pasword != "":
            stdin.write("%s\n" % (self.pasword))  # 这两行是执行sudo命令要求输入密码时需要的
            stdin.flush()  # 执行普通命令的话不需要这两行
        err=stderr.read()
        out=stdout.read()
        client.close()
        self.logger_console.error(err)
        self.logger_root.error(err)
        return out

    def clone(self):
        if self.clone_flag == "1":  # 要克隆
            git_path = self.repo_path + ".git"
            cmd="grep url %s.git/config | awk -F '=' '{print $2}'" % self.repo_path
            out=self.run_command(cmd)
            if os.path.exists(git_path):
                if out == self.url:
                    self.logger_root.info("[%s] 仓库目录已经存在,不需要克隆!" % self.ip)
                    self.logger_console.info("[%s] 仓库目录已经存在,不需要克隆!" % self.ip)
                else:
                    cmd="chown -R %s.%s %s" % (self.user, self.user, self.repo_path)
                    self.run_command(cmd)
                    cmd="rm -rf %s.git* %s*" % (self.repo_path, self.repo_path)
                    self.run_command(cmd)
                    self.logger_root.info("[%s] 开始克隆远程仓库!仓库目录为:%s" % (self.ip, self.repo_path))
                    self.logger_console.info("[%s] 开始克隆远程仓库!仓库目录为:%s" % (self.ip, self.repo_path))
                    cmd='git clone %s %s' % (self.user, self.repo_path)
                    self.run_command(cmd)
            else:
                if not os.path.exists(self.repo_path):
                    self.logger_root.info("[%s] 创建仓库目录:%s" % (self.ip, self.repo_path))
                    self.logger_console.info("[%s] 创建仓库目录:%s" % (self.ip, self.repo_path))
                    cmd="mkdir -p %s && chown -R %s.%s %s" % (self.repo_path, self.user, self.user, self.repo_path)
                    self.run_command(cmd)
                self.logger_root.info("[%s] 开始克隆远程仓库!仓库目录为:%s" % (self.host, self.repo_path))
                self.logger_console.info("[%s] 开始克隆远程仓库!仓库目录为:%s" % (self.host, self.repo_path))
                cmd='git clone %s %s' % (self.url, self.repo_path)
                self.run_command(cmd)
            cmd = "grep url %s.git/config | awk -F '=' '{print $2}'" % self.repo_path
            out = self.run_command(cmd)
            if os.path.exists(git_path) and out == self.url:
                self.logger_root.info("[%s] 克隆成功!" % self.ip)
                self.logger_console.info("[%s] 克隆成功!" % self.ip)
            else:
                self.logger_root.error("[%s] [ERROR] 克隆失败!" % self.ip)
                self.logger_console.error("[%s] [ERROR] 克隆失败!" % self.ip)
                sys.exit("update failure")

    def git(self):
        if not os.path.exists(self.repo_path):
            self.logger_root.error("[%s] 仓库目录%s不存在!" % (self.ip,self.repo_path))
            self.logger_console.error("[%s] 仓库目录%s不存在!" % (self.ip,self.repo_path))
            sys.exit()
        if self.tag != "":
            self.logger_root.info('[%s] 切换到分支:%s！' % (self.ip, self.branch))
            self.logger_root.info('[%s] 在仓库目录%s:下git pull！' % (self.ip, self.repo_path))
            self.logger_root.info('[%s] 切换tag到:%s！' % (self.ip, self.tag))
            cmd="cd %s && git checkout %s && git pull && git checkout %s" % (self.repo_path,self.branch,self.tag)
            self.logger_root.info(cmd)
            self.logger_console.info(cmd)
            out=self.run_command(cmd)
            self.logger_root.info(out)
            self.logger_console.info(out)
        else:
            self.logger_root.info('[%s] 切换分支到:%s！' % (self.ip, self.branch))
            self.logger_root.info('[%s] 在仓库目录%s:下git pull origin %s！' % (self.ip, self.repo_path,self.branch))
            cmd="cd %s && git fetch && git checkout %s && git pull" % (self.repo_path,self.branch)
            self.logger_root.info(cmd)
            self.logger_console.info(cmd)
            out=self.run_command(cmd)
            self.logger_root.info(out)
            self.logger_console.info(out)

    def compire(self):
        cmd="cd %s && %s" % (self.repo_path,self.build_cmd)
        out=self.run_command(cmd)
        self.logger_root.info(out)
        self.logger_console.info(out)

    def upload(self):
        if "mvn" in self.build_cmd:
            if "-pl" in self.build_cmd:
                build_path = self.build_cmd.split(" ")[3]
            else:
                build_path = ""
            if build_path == "":
                source = self.repo_path + "/target/"
            else:
                source = self.repo_path + build_path + "/target/"
        else:
            source = self.repo_path
        if not os.path.exists(self.upload_dir):
            self.logger_root.error("[%s] [ERROR] 上传war包的目录upload_dir:%s不存在!" % (self.ip, self.upload_dir))
            self.logger_console.error("[%s] [ERROR] 上传war包的目录upload_dir:%s不存在!" % (self.ip, self.upload_dir))
            sys.exit("update failure")
        self.logger_root.info('[%s] [INFO] Upload new %s file.' % (self.ip, self.package))
        cmd="sudo mv %s %s" % (source + self.package,self.upload_dir + self.package)
        self.logger_root.info(cmd)
        self.logger_console.info(cmd)
        self.run_command(cmd)

    def go(self):
        self.clone()
        self.git()
        self.compire()
        self.upload()
