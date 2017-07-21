#/usr/bin/env python
#-*- coding:utf-8 -*-
#Authot:Zhang Yan

import paramiko
import sys,commands,os,datetime

class docker():
    def __init__(self,ip,port,user,password,ssh_key,url,path,mod_name,logger_root,logger_console,dns=None,vol_list=None,port_list=None,hostname=None,option=None,replicas=None):
        self.ip = ip
        self.port = port
        self.user = user
        self.pasword =password
        self.ssh_key=ssh_key
        self.url=url 
        self.path = path
        self.mod_name=mod_name
        self.container= mod_name
        self.dns=dns
        self.vol_list=vol_list
        self.port_list=port_list
        self.hostname=hostname
        self.option=option
        self.replicas=replicas
        self.logger_root=logger_root
        self.logger_console=logger_console

    def run_command(self,cmd):
        client=paramiko.SSHClient()
        client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        client.load_system_host_keys()
        if self.ssh_key != "":
            pkey = self.ssh_key
            key = paramiko.RSAKey.from_private_key_file(pkey)
            client.connect(hostname=self.ip, port=self.port, username=self.user, pkey=key)
        else:
            client.connect(hostname=self.ip, port=self.port,username=self.user,password=self.pasword,timeout=10)
        stdin,stdout,stderr = client.exec_command(cmd)
        if self.pasword != "":
            stdin.write("%s\n" % (self.pasword))  #这两行是执行sudo命令要求输入密码时需要的
            stdin.flush()                         #执行普通命令的话不需要这两行
        self.logger_console.error(stderr.read())
        self.logger_root.error(stderr.read())
        print(stderr.read())
        if stdout == "stdout":
            pass
        else:
            return stdout.read()
        client.close()

    def image_func(self):
        self.logger_root.info("开始执行image_func函数")
        version = datetime.datetime.now().strftime("%Y%m%d%H%M")
        path=self.path + "/" + self.mod_name
        cmd="sudo docker build -t %s/prod/%s:%s %s" % (self.url,self.mod_name,version,path)
        self.logger_root.info(cmd)
        self.logger_console.info(cmd)
        self.run_command(cmd)
        cmd="sudo docker images | grep %s | grep %s" % (self.mod_name,version)
        self.logger_root.info(cmd)
        self.logger_console.info(cmd)
        out=self.run_command(cmd)
        if out == "":
            self.logger_root.error("[%s] image build fail!" % self.mod_name)
            self.logger_console.error("[%s] image build fail!" % self.mod_name)
            sys.exit("update failure")
        cmd="sudo docker push %s/prod/%s:%s" % (self.url,self.mod_name,version)
        self.logger_root.info(cmd)
        self.logger_console.info(cmd)
        self.run_command(cmd)
        cmd="curl -s -X GET --header 'Accept: application/json' 'https://%s/api/repositories/tags?repo_name=prod%%2F%s' | grep %s" % (self.url,self.mod_name,version)
        #cmd="wget -q -O aa.txt https://%s/api/repositories/tags?repo_name=prod%%2F%s && grep %s aa.txt && rm -rf aa.txt" % (self.url,self.mod_name,version)
        self.logger_root.info(cmd)
        self.logger_console.info(cmd)
        out=self.run_command(cmd)
        if out == "":
            self.logger_root.error("[%s] image push fail!" % self.mod_name)
            self.logger_console.error("[%s] image push fail!" % self.mod_name)
            sys.exit("update failure")
        else:
            self.logger_root.info("[%s] image push sucess!" % self.mod_name)
            self.logger_console.info("[%s] image push sucess!" % self.mod_name)
        return version

    def start_docker(self,version):
        cmd = "sudo docker ps -a | grep %s" % self.container
        self.logger_root.info(cmd)
        self.logger_console.info(cmd)
        out = self.run_command(cmd)
        if out == "":
            pass
        else:
            cmd = "sudo docker stop %s" % self.container
            self.logger_root.info(cmd)
            self.logger_console.info(cmd)
            self.run_command(cmd)
            cmd = "sudo docker rm %s" % self.container
            self.logger_root.info(cmd)
            self.logger_console.info(cmd)
            self.run_command(cmd)
            cmd = '''sudo mv /home/gxb/data/logs/tomcatlog/%s/catalina.`date "+%%Y-%%m-%%d"`.log /home/gxb/data/logs/tomcatlog/%s/catalina.`date "+%%Y-%%m-%%d"`.log_old''' % (self.mod_name, self.mod_name)
            self.logger_root.info(cmd)
            self.logger_console.info(cmd)
            self.run_command(cmd)
        if len(self.vol_list) == 0:
            vol = ""
        else:
            self.vol_list=self.vol_list.split("|")
            aa = " -v ".join(self.vol_list)
            vol = "-v %s" % aa
            for i in self.vol_list:
                # /home/data/gxb-web/logs/:/usr/local/tomcat/logs/:rw
                dir = i.split(":")[0]
                cmd = "[ -d %s ] || mkdir %s" % (dir, dir)
                self.run_command(cmd)
        if len(self.port_list) == 0:
            export = ""
        else:
            self.port_list=self.port_list.split("|")
            bb = " -p ".join(self.port_list)
            export = "-p %s" % bb
            for i in self.port_list:
                port = i.split(":")[0]
                cmd = "/usr/sbin/lsof -i:%s | grep -i LISTEN" % port
                out = self.run_command(cmd)
                if out == "":
                    pass
                else:
                    self.logger_root.error("容器绑定的宿主机端口已被占用!")
                    self.logger_console.error("容器绑定的宿主机端口已被占用!")
                    sys.exit("update failure")
        if self.hostname == "":
            host = ""
        else:
            host = "--hostname=d-%s" % self.hostname
        if self.dns == "":
            dns = ""
        else:
            dns = "--dns=%s" % self.dns
        # 在启动容器时,对cpu和磁盘读写进行限制!
        #cmd = "cat /proc/cpuinfo | grep processor | wc -l"
        #out = int(self.run_command(cmd))
        #quota = (out - 2) * 100000
        #cmd = "sudo fdisk -l | grep Disk | grep -vE 'mapper|label|identifier' | awk '{print $2}'|awk -F':' '{print $1}'"
        #device_li = self.run_command(cmd).strip().split('\n')
        #dev_str=""
        #for i in device_li:
        #    dev_str=dev_str + "--device-read-iops %s:100 --device-write-iops %s:100 --device-read-bps %s:30mb --device-write-bps %s:30mb " % (i,i,i,i)
        #cmd = "sudo docker run -d  --restart=%s %s %s %s %s %s --cpu-quota=%d %s --name %s %s/prod/%s:%s" % (self.restart, dns, host, vol, export, self.option, quota,dev_str,self.container, self.url, self.mod_name, version)
        cmd = "sudo docker run -d  --restart=always %s %s %s %s %s --privileged --name %s %s/prod/%s:%s" % (dns, host, vol, export, self.option,self.container, self.url, self.mod_name, version)
        self.logger_root.info(cmd)
        self.logger_console.info(cmd)
        self.run_command(cmd)
        cmd = "sudo docker ps | grep %s | grep Up" % self.container
        self.logger_root.info(cmd)
        self.logger_console.info(cmd)
        out = self.run_command(cmd)
        if out.strip() == "":
            self.logger_root.error("[%s] container run fail!" % self.mod_name)
            self.logger_console.error("[%s] container run fail!" % self.mod_name)
            sys.exit("update failure")
        else:
            self.logger_root.info("[%s] container run sucess!" % self.mod_name)
            self.logger_console.info("[%s] container run sucess!" % self.mod_name)
            return True

    def container_func(self,version):
        cmd="sudo docker pull %s/prod/%s:%s" % (self.url,self.mod_name,version)
        self.logger_root.info(cmd)
        self.logger_console.info(cmd)
        out=self.run_command(cmd)
        cmd="sudo docker images | grep prod | grep %s | grep %s" % (self.mod_name,version)
        self.logger_root.info(cmd)
        self.logger_console.info(cmd)
        out=self.run_command(cmd)
        if out == "":
            self.logger_root.error("[%s] image pull fail!" % self.mod_name)
            self.logger_console.error("[%s] image pull fail!" % self.mod_name)
            sys.exit("update failure")
        else:
            self.logger_root.info("[%s] image pull sucess!" % self.mod_name)
            self.logger_console.info("[%s] image pull sucess!" % self.mod_name)
        flag=self.start_docker(version)
        if flag:
            cmd='''sudo sh -c "docker images | grep %s | grep -v %s | awk '{print $3}' | sort | uniq | xargs docker rmi -f"''' % (self.container,version)
            self.logger_root.info(cmd)
            self.logger_console.info(cmd)
            try:
                self.run_command(cmd)
            except Exception as e:
                self.logger_root.error(e)
                self.logger_console.error(e)
                sys.exit("update failure")
        #cmd="sudo docker logs --tail=100 %s" % self.container
        #self.logger_root.info(cmd)
        #out = self.run_command(cmd)
        #self.logger_root.info(out)

    def common_func(self):
        cmd = "curl -s -X GET --header 'Accept: application/json' 'https://%s/api/repositories/tags?repo_name=prod%%2F%s'" % (self.url, self.mod_name)
        self.logger_root.info(cmd)
        out = eval(self.run_command(cmd))
        if out == "":
            self.logger_root.error("[%s] image is not exist!" % self.mod_name)
            self.logger_console.error("[%s] image is not exist!" % self.mod_name)
            sys.exit("update failure")
        else:
            out.sort()
            return out
    def image2_func(self):
        tags=self.common_func()
        if tags[-1] == "latest":
            version=tags[-2]
            #version=tags[1]
        else:
            version=tags[-1]
            #version=tags[1]
        self.container_func(version)
        return version

    def rollback_func(self,version,docker_flag):
        if not version:
            tags = self.common_func()
            if tags[-1] == "latest":
                version = tags[-3]
            else:
                version = tags[-2]
        if docker_flag == "1":
            self.container_func(version)
        if docker_flag == "2":
            self.k8s_func(version)

    def restart_func(self):
        #备用:docker容器重启(run方式)
        cmd = '''sudo docker ps | grep %s | awk '{print $2}' | awk -F ":" '{print $2}' ''' % self.mod_name
        self.logger_root.info(cmd)
        self.logger_console.info(cmd)
        version = self.run_command(cmd)
        flag=self.start_docker(version)
        return flag

    def k8s_func(self,version):
        path=self.path + "/" + self.mod_name 
        if "-" in self.mod_name: 
            cmd='''kubectl -s http://10.44.160.64:1179 --namespace=gxb-gray get pod|grep %s-rc|awk '{print $1}'|awk -F "-" '{print $4}' ''' % self.container
        else:
            cmd='''kubectl -s http://10.44.160.64:1179 --namespace=gxb-gray get pod|grep %s-rc|awk '{print $1}'|awk -F "-" '{print $3}' ''' % self.container
        ver_old=self.run_command(cmd).strip()
        self.logger_root.info(cmd)
        self.logger_console.info(cmd)
        cmd="ls %s| grep %s-rc-%s.yml" % (path,self.container,ver_old)
        out=self.run_command(cmd).strip()
        self.logger_root.info(cmd)
        self.logger_console.info(cmd)
        if out == "":
            self.logger_root.error("[%s-rc-%s.yml] 旧的rc文件不存在!" % (self.container,ver_old))
            self.logger_console.error("[%s-rc-%s.yml] 旧的rc文件不存在!" % (self.container,ver_old))
            sys.exit("update failure")
        cmd = "sudo cp -f %s/%s-rc-%s.yml %s/%s-rc-v%s.yml" % (path,self.container,ver_old,path,self.container,version)
        self.logger_root.info(cmd)
        self.logger_console.info(cmd)
        self.run_command(cmd)
        cmd='''grep replicas %s/%s-rc-v%s.yml | awk -F ":" '{print $2}' ''' % (path,self.container,version)
        replicas_old=self.run_command(cmd).strip()
        cmd = '''sudo sh -c "cd %s && sed -i 's/name: %s-rc-%s/name: %s-rc-v%s/g' %s-rc-v%s.yml ; sed -i 's/replicas: %s/replicas: %s/g' %s-rc-v%s.yml ; sed -i 's/version: %s/version: v%s/g' %s-rc-v%s.yml ; sed -i 's/image: %s\/prod\/%s:%s/image: %s\/prod\/%s:%s/g' %s-rc-v%s.yml"''' % (
            path,self.container,ver_old,self.container,version,self.container,version,replicas_old,self.replicas,self.container,version,ver_old,version,self.container,
            version,self.url,self.container,ver_old.split("v")[1],self.url,self.container,version,self.container,version
        )
        self.logger_root.info(cmd)
        self.logger_console.info(cmd)
        self.run_command(cmd)
        cmd="sudo kubectl -s http://10.44.160.64:1179 --namespace=gxb-gray rolling-update %s-rc-%s -f %s/%s-rc-v%s.yml —update-period=10s" % (self.container,ver_old,path,self.container,version)
        self.logger_root.info(cmd)
        self.logger_console.info(cmd)
        self.run_command(cmd)
        cmd="sudo kubectl -s http://10.44.160.64:1179 --namespace=gxb-gray get pod | grep %s-rc-v%s | grep -i running" % (self.container,version)
        out=self.run_command(cmd)
        if out == "":
            self.logger_root.error("[%s] pod启动失败!" % self.container)
            self.logger_console.error("[%s] pod启动失败!" % self.container)
        else:
            self.logger_root.info("[%s] pod启动成功!" % self.container)
            self.logger_console.info("[%s] pod启动成功!" % self.container)
        cmd="sudo rm -rf %s/%s-rc-%s.yml" % (path,self.container,ver_old)
        self.run_command(cmd)

    def k8s_image_func(self):
        tags = self.common_func()
        if tags[-1] == "latest":
            version = tags[-2]
            # version=tags[1]
        else:
            version = tags[-1]
            # version=tags[1]
        return version

    def add_dec_server(self):
        cmd="kubectl -s http://10.44.160.64:1179 --namespace=gxb-gray get pod | grep %s | head -1 | awk '{print $1}'" % self.container
        out=self.run_command(cmd).strip().split("-")
        out.pop(-1)
        server="-".join(out)
        cmd="sudo kubectl -s http://10.44.160.64:1179 --namespace=gxb-gray scale replicationcontroller %s --replicas=%s" % (server,self.replicas)
        self.logger_root.info(cmd)
        self.logger_console.info(cmd)
        self.run_command(cmd)
