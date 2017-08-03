#!/usr/bin/python
# -*- coding: utf-8 -*-

import sys,os,pexpect,paramiko,time
from lib.check_status import check_all_server

class haixuan():
    def __init__(self,auto='',mod_name='',host='',port='',upload_dir='',local_backup_dir_prefix='',remote_dst_file='',user='',password='',ssh_key='',package='',is_compress='',source_host='',
                 source_user='',source_password='',source_path='',source_port='',action='',lb_flag='',stop_cmd='',start_cmd='',docker_path='',docker_ip='',docker_user='',docker_port='',docker_pwd='',
                 nginx_mod='',slb_mod='',check_url='',key_word='',check_mod='',ser_port='',package_mod='',docker_flag='',gray_docker_flag='',container_run='',k8s_container='',once_flag='',exclude_file='',
                 git_enabled='',image='',version='',Add_Server='',logger_root='',logger_console=''):
        self.auto = auto
        self.mod_name = mod_name
        self.host = host
        self.user = user
        self.password = password
        self.ssh_key = ssh_key
        self.port = port
        self.remote_dst_file = remote_dst_file
        today = time.strftime("%Y-%-m-%-d-%-H%-M", time.localtime())
        self.local_backup_dir = local_backup_dir_prefix + mod_name + "/" + today + "/"
        self.upload_dir = upload_dir
        self.package = package
        self.is_compress = is_compress
        self.source_host = source_host
        self.source_user = source_user
        self.source_password = source_password
        self.source_path = source_path
        self.source_port = source_port
        self.action = action
        self.lb_flag = lb_flag
        self.stop_cmd = stop_cmd
        self.start_cmd = start_cmd
        self.nginx_mod = nginx_mod
        self.slb_mod = slb_mod
        self.check_url = check_url
        self.key_word = key_word
        self.check_mod = check_mod
        self.ser_port = ser_port
        self.package_mod = package_mod
        self.docker_flag = docker_flag
        self.container_run = container_run
        self.k8s_container = k8s_container
        self.once_flag = once_flag
        self.exclude_file = exclude_file
        self.git_enabled = git_enabled
        self.gray_docker_flag = gray_docker_flag
        self.docker_path = docker_path
        self.docker_ip = docker_ip
        self.docker_user = docker_user
        self.docker_port = docker_port
        self.docker_pwd = docker_pwd
        self.image = image
        self.version = version
        self.Add_Server = Add_Server
        self.logger_root=logger_root
        self.logger_console=logger_console

    # 在远程主机上执行命令的函数
    def run_command(self, cmd):
        self.logger_root.info("exec cmd: %s" % cmd)
        self.logger_console.info("exec cmd: %s" % cmd)
        client = paramiko.SSHClient()
        client.load_system_host_keys()
        client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        if self.ssh_key != "":
            pkey = self.ssh_key
            key = paramiko.RSAKey.from_private_key_file(pkey)
            client.connect(hostname=self.host, port=int(self.port), username=self.user, pkey=key)
        else:
            client.connect(hostname=self.host, port=int(self.port), username=self.user, password=self.password,
                           timeout=10)
        stdin, stdout, stderr = client.exec_command(cmd)
        if self.password != "":
            stdin.write("%s\n" % self.password)  # 这两行是执行sudo命令要求输入密码时需要的
            stdin.flush()  # 执行普通命令的话不需要这两行
        err=stderr.read()
        out=stdout.read()
        client.close()
        self.logger_root.error(err)
        self.logger_console.error(err)
        return out

    def scp_source_package_to_local(self):
        #从远程主机上传代码包,或者代码目录到upload_dir(/home/update)下
        self.logger_root.info("scp_source_package_to_local")
        self.logger_console.info("scp_source_package_to_local")
        if self.source_host != '' and self.source_user != '' and self.source_port != '' and self.source_password != '' and self.source_path != '':
            #获取source server变量
            if self.source_path.endswith("/"):
                pass
            else:
                self.source_path = self.source_path + "/"
            #从source_host拷贝文件(jar包,war包,tgz包等)
            if self.is_compress:
                source_file = self.source_path + self.package
                target_file = self.upload_dir + self.package
                backup_cmd="scp -q -P%s -r %s@%s:%s %s" % (self.source_port,self.source_user,self.source_host,source_file,target_file)
            #从source_host拷贝模块目录
            else:
                source_path = self.source_path
                target_path = self.upload_dir + self.package + "/"
                if os.path.exists(target_path):
                    pass
                backup_cmd="rsync -q -e 'ssh -p %s' -avz --exclude=logs/ --exclude=log/ %s@%s:%s %s" % (self.source_port,self.source_user,self.source_host,source_path,target_path)
            self.logger_root.info(backup_cmd)
            self.logger_console.info(backup_cmd)
            try:
                outfile=pexpect.run (backup_cmd, events={'(?i)password': self.source_password+'\n','continue connecting (yes/no)?':'yes\n'},timeout=None)
                self.logger_root.info(outfile)
            except Exception as e:
                self.logger_console.error(e)
                self.logger_root.error(e)
                sys.exit("update failure")
        else:
            self.logger_root.error("git_enabled=False,Make sure you define source_host/source_path/source_user/source_password/source_port")
            self.logger_console.error("git_enabled=False,Make sure you define source_host/source_path/source_user/source_password/source_port")
            sys.exit("update failure")

    def mv_upload_file_to_backup_dir(self):
        self.logger_root.info("mv_upload_file_to_backup_dir %s" % self.host)
        self.logger_console.info("mv_upload_file_to_backup_dir %s" % self.host)
        #如果备份目录有更新包 则不用拷贝
        if os.path.exists(self.local_backup_dir):
            return 0
        else:
            os.path.exists(self.local_backup_dir) or os.makedirs(self.local_backup_dir)
        if self.is_compress:
            source_file=self.upload_dir + self.package
            if os.path.exists(source_file):
                self.logger_root.info("mv %s %s" % (source_file,self.local_backup_dir))
                self.logger_console.info("mv %s %s" % (source_file,self.local_backup_dir))
                os.system("mv %s %s" % (source_file,self.local_backup_dir))
            else:
                self.logger_root.error(" can't find " + source_file)
                self.logger_console.error(" can't find " + source_file)
                sys.exit("update failure")
        else:
            #如果没有压缩包 是否有文件夹
            source_file = self.upload_dir + self.package + "/"
            if os.path.exists(source_file):
                os.chdir(source_file)
                #如果有文件夹的话,将文件夹打包成self.package + ".tgz"的文件
                os.system("tar zcf %s.tgz %s" % (self.package,source_file))
                os.system("mv %s.tgz %s" % (self.package,self.local_backup_dir))
            #如果都没有 退出
            else:
                self.logger_root.error("You compress flag is False,But " +self.upload_dir + " can't find " + self.mod_name + " directory")
                self.logger_console.error("You compress flag is False,But " +self.upload_dir + " can't find " + self.mod_name + " directory")
                sys.exit("update failure")

    def stop_program(self):
        if self.action == "update":
            #调用nginx加注释方法，在发版主机stop之前先在nginx的配置文件里将其注释
            if self.lb_flag == "1":
                self.logger_root.info("[%s]执行加注释函数!" % self.host)
                self.slb_mod.dec_slb(self.host)
                time.sleep(40)
            elif self.lb_flag == "0":
                self.logger_root.info("[%s]执行加注释函数!" % self.host)
                self.nginx_mod.add(self.host)
                time.sleep(40)
        #关闭应用
        if self.stop_cmd:
            rcmd=self.stop_cmd
            self.logger_root.info(rcmd)
            self.run_command(rcmd)
        else:
            self.logger_root.error("未定义停止命令!退出发版系统!")
            self.logger_console.error("未定义停止命令!退出发版系统!")
            sys.exit("update failure")

    def start_program(self):
        #启动应用
        if self.start_cmd:
            rcmd=self.start_cmd
            self.logger_root.info(rcmd)
            self.run_command(rcmd)
        else:
            self.logger_root.error("未定义启动命令!退出发版系统!")
            self.logger_console.error("未定义启动命令!退出发版系统!")
            sys.exit("update failure")
        self.check_start_status()

    def check_start_status(self):
        if self.check_url == "":
            if self.start_check():
                start_flag=True
        elif self.start_check():
            time.sleep(10)
            for i in range(15):
                if self.mod_name == "gxb-sso" and self.check_mod.check_login():
                    self.logger_root.info("[%s] API 调用成功!" % self.host)
                    start_flag = True
                    break
                elif self.check_mod.check_status():
                    self.logger_root.info("[%s] API 调用成功!" % self.host)
                    start_flag = True
                    break
                else:
                    start_flag = False
                    time.sleep(10)
                    continue
        if not start_flag:
            self.logger_root.error("[%s] API 调用不成功!" % self.host)
            self.logger_console.error("[%s] API 调用不成功!" % self.host)
        if self.action == "update" and start_flag:
            # 调用nginx减注释方法，在发版主机启动后取消nginx注释
            self.logger_root.info("[%s]执行解注释函数!" % self.host)
            if self.lb_flag == "1":
                self.slb_mod.add_slb(self.host)
            elif self.lb_flag == "0":
                self.nginx_mod.dec(self.host)
        
    def start_check(self):
        if self.ser_port == "":
            return True
        for i in range(40):
            rcmd="sudo lsof -i:%s | grep -i LISTEN" % self.ser_port
            out = self.run_command(rcmd)
            if out == "":
                time.sleep(1)
                continue
            else:
                self.logger_root.info("[%s] 服务起来啦!" % self.host)
                return True

    def update(self):
        #同步更新到远程服务器
        if self.auto:
            if self.docker_flag != "2":
                self.logger_root.info("执行加注释函数!")
                self.logger_console.info("执行加注释函数!")
                if self.lb_flag == "1":
                    self.slb_mod.dec_slb(self.host)
                elif self.lb_flag == "0":
                    self.nginx_mod.add(self.host)
            if self.docker_flag == "1":
                ver=self.container_run.image2_func()
                if self.once_flag:
                    ver_path=os.path.dirname(os.path.abspath(__file__)) + "/.." + "/log/version.txt"
                    with open(ver_path,"a+") as f:
                        f.write("%s:%s\n" % (self.mod_name,ver))
                self.check_start_status()
            elif self.docker_flag == "2":
                ver = self.k8s_container.k8s_image_func()
                self.k8s_container.k8s_func(ver)
            else:
                if self.git_enabled:
                    if not os.path.exists(self.local_backup_dir):
                        self.package_mod.go()
                else:
                    self.scp_source_package_to_local()
                self.mv_upload_file_to_backup_dir()
                self.logger_root.info('start stop program')
                self.logger_console.info('start stop program')
                self.stop_program()
                self.logger_root.info('stop program ok')
                self.logger_console.info('stop program ok')
                rcmd='[ -d %s ] || mkdir -p %s' %  (self.remote_dst_file,self.remote_dst_file)
                self.logger_root.info(rcmd)
                self.logger_console.info(rcmd)
                self.run_command(rcmd)
                rcmd="rsync -e 'ssh -p %s' -avz --exclude-from=%s %s %s@%s:%s" % (self.port,self.exclude_file,self.local_backup_dir,self.user,self.host,self.remote_dst_file+"/")
                self.logger_root.info(rcmd)
                self.logger_console.info(rcmd)
                outfile=pexpect.run (rcmd, events={'(?i)password': self.password+'\n','continue connecting (yes/no)?':'yes\n'},timeout=None)
                self.start_program()

    def gray_update(self):
        # 灰度发版
        if self.auto:
            if self.git_enabled:
               if not os.path.exists(self.local_backup_dir):
                   self.package_mod.go()
            else:
               self.scp_source_package_to_local()
            self.mv_upload_file_to_backup_dir()
            if self.gray_docker_flag == "1" or self.gray_docker_flag == "2":
                if self.once_flag:
                    remote_dst = self.docker_path + "/" + self.mod_name
                    rcmd = "rsync -e 'ssh -p %s' -avz %s %s@%s:%s" % (self.docker_port, self.local_backup_dir, self.docker_user, self.docker_ip, remote_dst + "/")
                    self.logger_root.info(rcmd)
                    self.logger_console.info(rcmd)
                    outfile = pexpect.run(rcmd, events={'(?i)password': self.docker_pwd + '\n','continue connecting (yes/no)?': 'yes\n'}, timeout=None)
                global ver
                ver = self.image.image_func()
            if self.gray_docker_flag == "1":
                self.container_run.container_func(ver)
                self.check_start_status()
            elif self.gray_docker_flag == "2":
                self.k8s_container.k8s_func(ver)
            else:
                self.stop_program()
                rcmd = '[ -d %s ] || mkdir -p %s' % (self.remote_dst_file, self.remote_dst_file)
                self.run_command(rcmd)
                rcmd = "rsync -e 'ssh -p %s' -avz --exclude-from=%s %s %s@%s:%s" % (
                self.port, self.exclude_file, self.local_backup_dir, self.user, self.host, self.remote_dst_file + "/")
                self.logger_root.info(rcmd)
                self.logger_console.info(rcmd)
                outfile = pexpect.run(rcmd, events={'(?i)password': self.password + '\n',
                                                    'continue connecting (yes/no)?': 'yes\n'}, timeout=None)
                self.start_program()

    def backup(self):
        #备份操作
        self.logger_root.info("backup start")
        os.path.exists(self.local_backup_dir) or os.makedirs(self.local_backup_dir)
        backup_cmd="rsync -e 'ssh -p %s' -avz --exclude=logs/  %s@%s:%s %s" % (self.port,self.user,self.host,self.remote_dst_file,self.local_backup_dir)
        self.logger_root.info(backup_cmd)
        outfile=pexpect.run (backup_cmd, events={'(?i)password': self.password+'\n','continue connecting (yes/no)?':'yes\n'},timeout=None)
        self.logger_root.info(outfile)
        self.logger_root.info("%s backup successful!" % self.mod_name)
        sys.exit()

    def rollback(self):
        #回滚
        #如果没有指定版本，找出时间最近的一次版本进行回滚
        self.logger_root.info("start rollback")
        self.logger_console.info("start rollback")
        if self.docker_flag == "1":
            self.container_run.rollback_func(self.version,self.docker_flag)
        elif self.docker_flag == "2":
            self.k8s_container.rollback_func(self.version,self.docker_flag)
        else:
            if not self.version:
                local_backup_mod_dir=self.local_backup_dir + self.mod_name + "/"
                cmd='''ls -rt %s|tail -2|head -1''' % local_backup_mod_dir
                version=os.popen(cmd).read().rstrip()
            else:
                version=self.version
            #回滚目录
            self.back_dir=self.local_backup_dir + self.mod_name + "/" + version + "/"
            self.stop_program()
            rcmd="rsync -e 'ssh -p %s' -avz  --exclude-from=%s %s %s@%s:%s" % (self.port,self.exclude_file,self.back_dir + self.mod_name + "/",self.user,self.host,self.remote_dst_file+"/")
            self.logger_root.info(rcmd)
            self.logger_console.info(rcmd)
            outfile=pexpect.run (rcmd, events={'(?i)password': self.password+'\n','continue connecting (yes/no)?':'yes\n'},timeout=None)
            self.logger_root.info(outfile)
            self.start_program()

    def restart(self):
        # 重启模块
        if self.auto:
            if self.docker_flag != '2':
                self.logger_root.info("执行加注释函数!")
                self.logger_console.info("执行加注释函数!")
                if self.lb_flag == "1":
                    self.slb_mod.dec_slb(self.host)
                elif self.lb_flag == "0":
                    self.nginx_mod.add(self.host)
                time.sleep(10)
            if self.docker_flag == "1":
                #restart方式:
                rcmd = "sudo docker restart %s" % self.mod_name
                self.logger_root.info(rcmd)
                self.logger_console.info(rcmd)
                self.run_command(rcmd)
                #run方式(备用):
                #container_run.restart_func()
                #self.check_start_status()
            elif self.docker_flag == "2":
                pass
            else:
                self.stop_program()
                self.start_program()
            if self.docker_flag != '2':
                self.logger_root.info("执行减注释函数!")
                self.logger_console.info("执行减注释函数!")
                if self.lb_flag == "1":
                    self.slb_mod.add_slb(self.host)
                elif self.lb_flag == "0":
                    self.nginx_mod.dec(self.host)

    def check_server(self):
        if self.auto:
            if self.mod_name == "common":
                check_all_server()                
            if self.mod_name == "mysql":
                self.logger_root.info("[%s] 开始检测!" % self.host)
                self.logger_console.info("[%s] 开始检测!" % self.host)
                self.check_mod.check_mysql()
            elif self.mod_name == "redis":
                self.logger_root.info("[%s] 开始检测!" % self.host)
                self.logger_console.info("[%s] 开始检测!" % self.host)
                self.check_mod.check_redis()
            elif self.mod_name == "gxb-sso" and self.check_mod.check_login():
                self.logger_root.info("[%s] API 调用成功!" % self.host)
                self.logger_console.info("[%s] API 调用成功!" % self.host)
            elif self.check_mod.check_status():
                self.logger_root.info("[%s] API 调用成功!" % self.host)
                self.logger_console.info("[%s] API 调用成功!" % self.host)
            else:
                self.logger_root.error("[%s] API 调用不成功!" % self.host)
                self.logger_console.error("[%s] API 调用不成功!" % self.host)

    def Addserver(self):
        if self.auto and self.once_flag:
            if self.docker_flag == "1":
                self.Add_Server.add_server()
            elif self.docker_flag == "2":
                self.k8s_container.add_dec_server()

    def Decserver(self):
        if self.auto and self.once_flag:
            if self.docker_flag == "1":
                self.Add_Server.dec_server()
            elif self.docker_flag == "2":
                self.k8s_container.add_dec_server()

