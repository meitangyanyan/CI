#/usr/bin/env python
#-*- coding:utf-8 -*-
#Authot:Zhang Yan

import sys,os,pexpect,fileinput,paramiko,datetime,time,commands,subprocess,logging
from ConfigParser import ConfigParser
from lib.log import fileConfig
from optparse import OptionParser

##########变量设置#################
#开始时间（结束后有个结束时间，两者相减即程序运行时间）
starttime=datetime.datetime.now()
#today="2014-5-21-101110"
today=time.strftime("%Y-%-m-%-d-%-H%-M",time.localtime())

#程序及配置文件所在路径
src_dir_prefix=os.path.dirname(os.path.abspath(__file__)) + "/"
#模块信息配置文件
mod_file=src_dir_prefix + "conf/modww.ini"
#同步需要排除的文件
exclude_file=src_dir_prefix + "conf/exclude.txt"

usage="USAGE: \nEXAMPLE: ./%prog -m mod_name -a action -A \n\t if rollback: ./%prog -m mod_name -a action -V rollback_version"
ver="V1.0.0"
parser = OptionParser(usage=usage,version=ver)
parser.add_option("-m", "--module", action="store", type="string",dest="mod_name",default="",help="the module name to deploy")
parser.add_option("-a", "--action", action="store", type="string",dest="action",default="",help="the action to perform")
parser.add_option("-A", "--auto", action="store_true",dest="auto",help="Select whether to deploy directly")
parser.add_option("-V", "--rollback_version", action="store",dest="version",default="",help="the timestamp of the docker mirror to roll back")

(options, args) = parser.parse_args()
mod_name = options.mod_name
action = options.action
version = options.version
auto = options.auto

fileConfig('%s/conf/logging.conf' % src_dir_prefix, mod_name)
logger_console = logging.getLogger('console')
logger_root = logging.getLogger('root')

from lib.addserver import AddServer
from lib.nginx import nginx
from lib.slb import SLB
from lib.docker import docker
from lib.check_status import CheckStatus
from lib.fabfile import Package
from lib.deploy import haixuan

#读取配置文件
#模块IP/路径/模块类型
#PS:如果有tomcat 还需指定tomcat路径（重启tomcat服务用）
if not os.path.exists(mod_file):
    logger_console.error("不能can not find module config file %s" % mod_file)
    logger_root.error("can not find module config file %s" % mod_file)
    sys.exit("update failure")

cf=ConfigParser()
cf.read(mod_file)
#本地主机同步目录(备份目录）
if cf.has_option('common',"local_backup_dir_prefix"):
    local_backup_dir_prefix=cf.get("common","local_backup_dir_prefix")
else:
    local_backup_dir_prefix="/home/backup/"

#程序上传目录(上传目录不需加日期 每次替换上次上传的版本)
if cf.has_option("common","path"):
    upload_dir=cf.get("common","path")
else:
    upload_dir="/home/update/"
if upload_dir.endswith("/"):
    pass
else:
    upload_dir = upload_dir + "/"

#配置文件多IP分隔符
if cf.has_option("common","s_field"):
    s_field=cf.get("common","s_field")
else:
    s_field='|'

cmd="ps aux|grep update.py |grep %s|grep %s|grep -v grep|wc -l" % (mod_name,action)
out=subprocess.Popen(cmd,shell=True,stdout=subprocess.PIPE,stderr=subprocess.PIPE)
if int(out.stdout.read()) > 1:
    logger_console.error("[%s]进程id已经存在,请不要重复[%s]!如需了解详情,请查看日志!" % (mod_name,action))
    logger_root.error("[%s]进程id已经存在,请不要重复[%s]!如需了解详情,请查看日志!" % (mod_name,action))
    sys.exit()

logger_root.info("[%s] 开始发版!!!!!" % starttime)
logger_console.info("[%s] 开始发版!!!!!" % starttime)
#如果没有指定模块名或者动作,打印错误并退出
if mod_name or action:
    pass
else:
    logger_root.error('''you don't have mod_name and action!\nuse -h get some help''')
    logger_console.error('''you don't have mod_name and action!\nuse -h get some help''')
    sys.exit("update failure")

#如果模块不在模块列表中，打印错误信息并退出
if not cf.has_section(mod_name):
    logger_root.error("mod_name %s not in mod_list\nmod_list must in \n %s \n\n see %s get more information" % (mod_name,cf.sections(),mod_file))
    logger_console.error("mod_name %s not in mod_list\nmod_list must in \n %s \n\n see %s get more information" % (mod_name,cf.sections(),mod_file))
    sys.exit("update failure")

if cf.has_option(mod_name,"git_enabled"):
    #git_enabled="True"的话:打代码包(默认),否则从别的环境传代码包
    git_enabled=eval(cf.get(mod_name,'git_enabled'))
else:
    git_enabled=True
if cf.has_option(mod_name,"stop_cmd"):
    #自定义停止命令
    stop_cmd = cf.get(mod_name,"stop_cmd")
else:
    stop_cmd = False
if cf.has_option(mod_name,"start_cmd"):
    #自定义启动命令
    start_cmd = cf.get(mod_name,"start_cmd")
else:
    start_cmd = False
if cf.has_option(mod_name,"package"):
    #代码包名
    package=cf.get(mod_name,"package")
else:
    package=mod_name + ".war"
if cf.has_option(mod_name,"is_compress"):
    is_compress=cf.get(mod_name,"is_compress")
else:
    is_compress=True
if cf.has_option(mod_name, 'path'):
    #如果是docker(k8s)环境的话:是yml所在目录,如果是非docker的话:是代码包/代码目录所在目录
    remote_dst_file = cf.get(mod_name, "path")
else:
    remote_dst_file = ""
if cf.has_option(mod_name, "check_url"):
    check_url = cf.get(mod_name, "check_url")
else:
    logger_root.info("没有设置监控url")
    check_url = ""
if cf.has_option(mod_name, "key_word"):
    key_word = cf.get(mod_name, "key_word")
else:
    logger_root.info("没有设置监控关键字")
    key_word = ""

if cf.has_option(mod_name, "docker_flag"):
    # docker_flag:1->docker :2->k8s 否则:不走容器,默认"1"
    docker_flag_t = cf.get(mod_name, "docker_flag")
else:
    docker_flag_t = "docker"
if docker_flag_t == "docker":
    docker_flag="1"
elif docker_flag_t == "k8s":
    docker_flag="2"
else:
    docker_flag="0"
if cf.has_option(mod_name,"gray_docker_flag"):
    # gray_docker_flag:1->docker :2->k8s 否则:不走容器,默认"1"
    gray_docker_flag_t = cf.get(mod_name,"gray_docker_flag")
else:
    gray_docker_flag_t = "docker"
if gray_docker_flag_t == "docker":
    gray_docker_flag="1"
elif gray_docker_flag_t == "k8s":
    gray_docker_flag="2"
else:
    gray_docker_flag="0"
if cf.has_option(mod_name, "port_list"):
    port_list = cf.get(mod_name, "port_list")
else:
    port_list = ""
if port_list == "":
    ser_port = ""
else:
    ser_port = port_list.split(":")[0]
if docker_flag == "1" or docker_flag == "2" or gray_docker_flag == "1" or gray_docker_flag == "2":
    if cf.has_option("docker", "ip"):
        docker_ip = cf.get("docker", "ip")
    else:
        logger_root.error("必须设置构建镜像的服务器的ip")
        logger_console.error("必须设置构建镜像的服务器的ip")
        sys.exit("update failure")
    if cf.has_option("docker", "port"):
        docker_port = int(cf.get("docker", "port"))
    else:
        docker_port = 22
    if cf.has_option("docker", "user"):
        docker_user = cf.get("docker", "user")
    else:
        logger_root.error("必须设置构建镜像的服务器的user")
        logger_console.error("必须设置构建镜像的服务器的user")
        sys.exit("update failure")
    if cf.has_option("docker", "password"):
        docker_pwd = cf.get("docker", "password")
    else:
        docker_pwd = ""
    if cf.has_option("docker","ssh_key"):
        docker_ssh_key=cf.get("docker","ssh_key")
    else:
        docker_ssh_key = ""
    if docker_ssh_key == "" and docker_pwd == "":
        logger_root.error("必须设置构建镜像的服务器的登录密码或者登录key")
        logger_console.error("必须设置构建镜像的服务器的登录密码或者登录key")
        sys.exit("update failure")
    if cf.has_option("docker", "path"):
        docker_path = cf.get("docker", "path")
    else:
        logger_root.error("必须设置dockfile所在目录")
        logger_console.error("必须设置dockfile所在目录")
        sys.exit("update failure")
    if cf.has_option("docker", "url"):
        docker_url = cf.get("docker", "url")
    else:
        docker_url = "http://docker.gaoxiaobang.com"
if docker_flag == "1" or gray_docker_flag == "1":
    if cf.has_option(mod_name, "dns"):
        dns = cf.get(mod_name, "dns")
    else:
        dns = ""
    if cf.has_option(mod_name, "vol_list"):
        vol_list = cf.get(mod_name, "vol_list")
    else:
        vol_list = ""
    if cf.has_option(mod_name, "option"):
        option = cf.get(mod_name, "option")
    else:
        option = ""
if docker_flag == "2" or gray_docker_flag == "2":
    if cf.has_option(mod_name, "replicas"):
        replicas = cf.get(mod_name, "replicas")
    else:
        replicas = "1"
if cf.has_option(mod_name, "lb_flag"):
    # lb_flag = "0":nginx,"1":slb,否则:不进行负载摘除添加操作
    lb_flag_t = cf.get(mod_name, "lb_flag")
else:
    lb_flag_t = "0"
if lb_flag_t == "nginx":
    lb_flag="0"
elif lb_flag_t == "slb":
    lb_flag="1"
else:
    lb_flag="2"
if lb_flag == "1":
    if cf.has_option(mod_name,"access_key_id"):
        access_key_id=cf.get(mod_name,"access_key_id")
    else:
        logger_root.error("[access_key_id]必须设置!")
        logger_console.error("[access_key_id]必须设置!")
        sys.exit("update failure")
    if cf.has_option(mod_name,"access_key_secret"):
        access_key_secret=cf.get(mod_name,"access_key_secret")
    else:
        logger_root.error("[access_key_secret]必须设置!")
        logger_console.error("[access_key_secret]必须设置!")
        sys.exit("update failure")
    if cf.has_option(mod_name,"region_id"):
        region_id=cf.get(mod_name,"region_id")
    else:
        logger_root.error("[aregion_id]必须设置!")
        logger_console.error("[region_id]必须设置!")
        sys.exit("update failure")
    if cf.has_option(mod_name, "slb_vser_id"):
        VServerGroupId = cf.get(mod_name, "slb_vser_id")
    else:
        logger_root.error("[slb_vser_id]必须设置虚拟服务器组id!")
        logger_console.error("[slb_vser_id]必须设置虚拟服务器组id!")
        sys.exit("update failure")
    if cf.has_option(mod_name, "slb_port"):
        slb_port = int(cf.get(mod_name, "slb_port"))
    else:
        slb_port = 80
    if cf.has_option(mod_name, "weight"):
        weight = int(cf.get(mod_name, "weight"))
    else:
        weight = 100
    slb_mod = SLB(access_key_id, access_key_secret, region_id, VServerGroupId, slb_port, weight,logger_root, logger_console)
    nginx_mod = ''
elif lb_flag == "0":
    # 调用nginx类生成nginx加注释和解注释模块
    if cf.has_option(mod_name,"lb_ip"):
        ip_list = cf.get(mod_name,"lb_ip")
    elif cf.has_option("lb", "ip"):
        ip_list = cf.get("lb", "ip")
    else:
        logger_root.error("必须设置nginx服务器的ip!")
        logger_console.error("必须设置nginx服务器的ip!")
        sys.exit("update failure")
    if cf.has_option(mod_name,"lb_port"):
        lb_port = int(cf.get(mod_name,"lb_port"))
    elif cf.has_option("lb", "port"):
        lb_port = int(cf.get("lb", "port"))
    else:
        lb_port = 22
    if cf.has_option(mod_name,"lb_user"):
        lb_user=cf.get(mod_name,"lb_user")
    elif cf.has_option("lb", "user"):
        lb_user = cf.get("lb", "user")
    else:
        logger_root.error("必须设置nginx服务器的用户!")
        logger_console.error("必须设置nginx服务器的用户!")
        sys.exit("update failure")
    if cf.has_option(mod_name,"lb_passwd"):
        lb_passwd = cf.get(mod_name,"lb_passwd")
    elif cf.has_option("lb", "password"):
        lb_passwd = cf.get("lb", "password")
    else:
        lb_passwd = ""
    if cf.has_option(mod_name,"lb_ssh_key"):
        lb_ssh_key = cf.get(mod_name, "ssh_key")
    elif cf.has_option("lb","ssh_key"):
        lb_ssh_key=cf.get("lb","ssh_key")
    else:
        lb_ssh_key =""
    if lb_passwd == "" and lb_ssh_key == "":
        logger_root.error("必须设置nginx服务器的密码或者sshkey!")
        logger_console.error("必须设置nginx服务器的密码或者sshkey!")
        sys.exit("update failure")
    if cf.has_option(mod_name,"lb_path"):
        lb_path = cf.get(mod_name,"lb_path")
    elif cf.has_option("lb", "path"):
        lb_path = cf.get("lb", "path")
    else:
        logger_root.error("必须设置nginx服务的目录!")
        logger_console.error("必须设置nginx服务的目录!")
        sys.exit("update failure")
    if cf.has_option(mod_name,"nginx_cmd"):
        nginx_cmd=cf.get(mod_name,"nginx_cmd")
    elif cf.has_option("lb","nginx_cmd"):
        nginx_cmd=cf.get("lb","nginx_cmd")
    else:
        logger_root.error("必须设置nginx reload命令!")
        logger_console.error("必须设置nginx reload命令!")
        sys.exit("update failure")
    nginx_mod = nginx(ip_list=ip_list.split("|"), port=lb_port, user=lb_user,
                          path=lb_path,nginx_cmd=nginx_cmd,ser_port=ser_port, password=lb_passwd,ssh_key=lb_ssh_key,logger_root=logger_root,logger_console=logger_console)
    slb_mod=''

if cf.has_option(mod_name, "clone_flag"):
    #1的话克隆,0的话不克隆,默认不克隆
    clone_flag = cf.get(mod_name, "clone_flag")
else:
    clone_flag = 0
if cf.has_option(mod_name, "url"):
    git_url = cf.get(mod_name, "url")
else:
    logger_root.error("必须指定远程仓库的url!")
    logger_console.error("必须指定远程仓库的url!")
    sys.exit("update failure")
if cf.has_option(mod_name, "branch"):
    branch = cf.get(mod_name, "branch")
else:
    branch = "master"
if cf.has_option(mod_name, "tag"):
    tag = cf.get(mod_name, "tag")
else:
    tag = ""
if cf.has_option(mod_name, "git_ip"):
    git_host = cf.get(mod_name, "git_ip")
else:
    logger_root.error("必须设置本地仓库机器的ip!")
    logger_console.error("必须设置本地仓库机器的ip!")
    sys.exit("update failure")
if cf.has_option(mod_name, "git_port"):
    git_port = int(cf.get(mod_name, "git_port"))
else:
    git_port = 22
if cf.has_option(mod_name, "git_user"):
    git_user = cf.get(mod_name, "git_user")
else:
    logger_root.error("必须设置本地仓库机器的可登陆用户!")
    logger_console.error("必须设置本地仓库机器的可登陆用户!")
    sys.exit("update failure")
if cf.has_option(mod_name, "git_ssh_key"):
    git_ssh_key = cf.get(mod_name, "git_ssh_key")
else:
    git_ssh_key = ""
if cf.has_option(mod_name, "git_password"):
    git_password = cf.get(mod_name, "git_password")
else:
    git_password = ""
if git_password == "" and git_ssh_key == "":
    logger_root.error("必须设置本地仓库机器的登录密码或者key文件!")
    logger_console.error("必须设置本地仓库机器的登录密码或者key文件!")
    sys.exit("update failure")
if cf.has_option(mod_name, "repo_path"):
    repo_path = cf.get(mod_name, "repo_path")
    logger_root.info(repo_path)
else:
    logger_root.error("必须指定仓库目录!")
    logger_console.error("必须指定仓库目录!")
    sys.exit("update failure")
if repo_path.endswith("/"):
    pass
else:
    repo_path = repo_path + "/"
if cf.has_option(mod_name, "build_cmd"):
    build_cmd = cf.get(mod_name, "build_cmd")
else:
    build_cmd = ""
if cf.has_option(mod_name, "package"):
    package = cf.get(mod_name, "package")
else:
    package = mod_name + ".war"
package_mod = Package(ip=git_host, user=git_user, port=git_port, password=git_password, ssh_key=git_ssh_key,
                      url=git_url, repo_path=repo_path, tag=tag, build_cmd=build_cmd, upload_dir=upload_dir,
                      package=package, branch=branch, clone_flag=clone_flag,logger_root=logger_root,logger_console=logger_console)

if cf.has_option(mod_name,"source_host"):
    source_host=cf.get(mod_name,"source_host")
else:
    source_host=''
if cf.has_option(mod_name,"source_user"):
    source_user=cf.get(mod_name,"source_user")
else:
    source_user=''
if cf.has_option(mod_name,"source_port"):
    source_port=cf.get(mod_name,"source_port")
else:
    source_port=''
if cf.has_option(mod_name,"source_password"):
    source_password=cf.get(mod_name,"source_password")
else:
    source_password=''
if cf.has_option(mod_name,"source_path"):
    source_path=cf.get(mod_name,"source_path")
else:
    source_path=''
if action == "gray_update":
    if cf.has_option(mod_name, 'gray_ip'):
        host_list = cf.get(mod_name, 'gray_ip').split(s_field)
    else:
        logger_root.error("[%s]此模块没有设置gray_ip" % mod_name)
        logger_console.error("[%s]此模块没有设置gray_ip" % mod_name)
        sys.exit("update failure")
else:
    if cf.has_option(mod_name,"ip"):
        host_list=cf.get(mod_name,'ip').split(s_field)
    else:
        logger_root.error("[%s]此模块没有设置ip" % mod_name)
        logger_console.error("[%s]此模块没有设置ip" % mod_name)
        sys.exit("update failure")
logger_root.info("主机列表: %s" % str(host_list))
logger_console.info("主机列表: %s" % str(host_list))

if cf.has_option(mod_name,'user'):
    user_list=cf.get(mod_name,'user').split(s_field)
if cf.has_option(mod_name,'password'):
    password_list=cf.get(mod_name,'password').split(s_field)
if cf.has_option(mod_name, "ssh_key"):
    ssh_key_list=cf.get(mod_name, "ssh_key").split(s_field)
if cf.has_option(mod_name,'port'):
    port_list=cf.get(mod_name,'port').split(s_field)
k=0
for host in host_list:
    if k == 0:
        once_flag = True
    else:
        once_flag = False
    k += 1
    host_index=host_list.index(host)
    try:
        #如果有多个IP/端口/用户/密码 则根据list中的index查找
        if cf.has_option(mod_name,'user') and len(user_list)>host_index:
            user=user_list[host_index]
        elif cf.has_option(mod_name,'user'):
            user=cf.get(mod_name,'user')
        else:
            logger_root.error("必须设置%s的登录用户名!" % host)
            logger_console.error("必须设置%s的登录用户名!" % host)
            sys.exit("update failure")
        if cf.has_option(mod_name,'password') and len(password_list)>host_index:
            password=password_list[host_index]
        elif cf.has_option(mod_name,'password'):
            password=cf.get(mod_name,'password')
        else:
            password=""
        if cf.has_option(mod_name,"ssh_key") and len(ssh_key_list)>host_index:
            ssh_key=ssh_key_list[host_index]
        elif cf.has_option(mod_name,'ssh_key'):
            ssh_key=cf.get(mod_name,'ssh_key')
        else:
            ssh_key=""
        if ssh_key == "" and password == "":
            logger_root.error("必须设置%s的登录密码或者key!" % host)
            logger_console.error("必须设置%s的登录密码或者key!" % host)
            sys.exit("update failure")
        if cf.has_option(mod_name,'port') and len(port_list)>host_index:
            port=port_list[host_index]
        elif cf.has_option(mod_name,'port'):
            port=cf.get(mod_name,'port')
        else:
            port=22
    except Exception as e:
        logger_root.error(e)
        logger_console.error(e)
        sys.exit("update failure")

    if docker_flag == "1" or docker_flag == "2" or gray_docker_flag == "1" or gray_docker_flag == "2":
        image = docker(ip=docker_ip, port=docker_port, user=docker_user, password=docker_pwd,ssh_key=docker_ssh_key, url=docker_url, path=docker_path, mod_name=mod_name,logger_root=logger_root,logger_console=logger_console)
    if docker_flag == "1" or gray_docker_flag == "1":
        #Add_Server = AddServer(mod_name, host_list, dns, vol_list.split("|"), port_list.split("|"), host, option, port, user, password,ip_list.split("|"),logger_root,logger_console)
        container_run=docker(ip=host, port=port, user=user, password=password,ssh_key=ssh_key, url=docker_url, path=docker_path,mod_name=mod_name, dns=dns, vol_list=vol_list, port_list=port_list,hostname=host,option=option,logger_root=logger_root,logger_console=logger_console)
    if docker_flag == "2" or gray_docker_flag == "2":
        k8s_container=docker(ip=host, port=port, user=user, password=password,ssh_key=ssh_key, url=docker_url, path=remote_dst_file,mod_name=mod_name, replicas=replicas,logger_root=logger_root,logger_console=logger_console)
    check_mod = CheckStatus(host=host,port=ser_port,user=user,password=password,dbname="",url=check_url,keyword=key_word,logger_root=logger_root,logger_console=logger_console)
    t=haixuan(
        auto=auto,mod_name=mod_name,host=host,port=port,local_backup_dir_prefix=local_backup_dir_prefix,user=user,password=password,ssh_key=ssh_key,package=package,is_compress=is_compress,source_host=source_host,upload_dir=upload_dir,
        source_user=source_user,source_password=source_password,source_path=source_path,source_port=source_port,action=action,lb_flag=lb_flag,stop_cmd=stop_cmd,start_cmd=start_cmd,docker_path=docker_path,docker_ip=docker_ip,
        docker_user=docker_user,docker_port=docker_port,docker_pwd=docker_pwd,nginx_mod=nginx_mod,slb_mod=slb_mod,check_url=check_url,key_word=key_word,check_mod=check_mod,ser_port=ser_port,package_mod=package_mod,
        docker_flag=docker_flag,gray_docker_flag=gray_docker_flag,container_run=container_run,k8s_container=k8s_container,once_flag=once_flag,exclude_file=exclude_file,git_enabled=git_enabled,image=image,version=version,Add_Server='',logger_root=logger_root,logger_console=logger_console)
    try:
        eval("t.%s()" % action)
    except Exception as e:
        logger_root.error(e)
        logger_console.error(e)
        sys.exit("update failure")

def clean_cdn_cache(mod_name):
    import subprocess
    if mod_name == 'cms-web':
        itemid="123"
        cmd="cdn接口命令"
    if mod_name == 'gxb-web':
        itemid="456"
        cmd="cdn接口命令"
    p = subprocess.Popen(cmd,shell=True,stdout=subprocess.PIPE,stderr=subprocess.STDOUT)
    out = p.stdout.read()
    if eval(out)["msg"] == "success":
        if eval(out)["result"][itemid] == 0:
            logger_root.info("[%s]cdn缓存刷新成功!" % mod_name)
            logger_console.info("[%s]cdn缓存刷新成功!" % mod_name)
        else:
            err_dic = {'cdn刷新返回信息列表'}
            logger_root.error("[%s]cdn缓存刷新失败! 错误信息:%s" % (mod_name,err_dic[eval(out)["result"][itemid]]))
            logger_console.error("[%s]cdn缓存刷新失败! 错误信息:%s" % (mod_name, err_dic[eval(out)["result"][itemid]]))
            sys.exit("update failure")
    else:
        logger_root.error("[%s]cdn缓存刷新失败! 错误信息:%s" % (mod_name,eval(out)["msg"]))
        logger_console.error("[%s]cdn缓存刷新失败! 错误信息:%s" % (mod_name, eval(out)["msg"]))
        sys.exit("update failure")
if action == 'update' and (mod_name == 'gxb-web' or mod_name == 'cms-web'):
    clean_cdn_cache(mod_name)
endtime=datetime.datetime.now()
logger_root.info("this program consumed %s seconds " % (endtime - starttime))
logger_console.info("this program consumed %s seconds " % (endtime - starttime))
