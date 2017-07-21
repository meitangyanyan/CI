#/usr/bin/env python
#-*- coding:utf-8 -*-
#Authot:Zhang Yan

from aliyunsdkcore.client import AcsClient
from aliyunsdkslb.request.v20140515 import RemoveVServerGroupBackendServersRequest,AddVServerGroupBackendServersRequest,DescribeVServerGroupAttributeRequest
from aliyunsdkecs.request.v20140526 import DescribeInstancesRequest
import json,re,sys
import subprocess

class SLB:
    def __init__(self,access_key_id,access_key_secret,region_id,VServerGroupId,port,logger_root,logger_console,weight=''):
        self.client = AcsClient(
            access_key_id,
            access_key_secret,
            region_id
        )
        self.VServerGroupId = VServerGroupId
        self.port = port
        self.weight = weight
        self.logger_console=logger_console
        self.logger_root=logger_root
    def get_ecs_id(self,dec_ip):
        pt = re.compile("^((?:(2[0-4]\d)|(25[0-5])|([01]?\d\d?))\.){3}(?:(2[0-4]\d)|(255[0-5])|([01]?\d\d?))$")
        res = re.match(pt,dec_ip)
        print res.group()
        if not res:
            cmd = 'grep -w %s /etc/hosts' % dec_ip
            p = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
            if p.stdout.read() == "":
                self.logger_root.info("[%s] /etc/hosts文件里没有配置此主机名" % dec_ip)
                self.logger_console.info("[%s] /etc/hosts文件里没有配置此主机名" % dec_ip)
                sys.exit()
            else:
                dec_ip = p.stdout.read().strip().split()[0]
        request=DescribeInstancesRequest.DescribeInstancesRequest()
        InnerIpAddresses=[dec_ip]
        request.set_InnerIpAddresses(InnerIpAddresses)
        res = self.client.do_action_with_exception(request)
        res = json.loads(res)
        ecs_id=res['Instances']['Instance'][0]['InstanceId']
        return ecs_id


    def get_backendservers(self):
        request = DescribeVServerGroupAttributeRequest.DescribeVServerGroupAttributeRequest()
        request.set_VServerGroupId(self.VServerGroupId)
        res = self.client.do_action_with_exception(request)
        res = json.loads(res)
        temp = res["BackendServers"]["BackendServer"]
        BackendServers=[]
        aa={}
        for i in temp:
            aa['ServerId']=str(i['ServerId'])
            aa['Port']=i['Port']
            aa['Weight']=i['Weight']
            BackendServers.append(aa)
        return BackendServers

    def common(self,request,BackendServers):
        request.set_BackendServers(BackendServers)
        res = self.client.do_action_with_exception(request)
        return res

    def dec_slb(self,dec_ip):
        #删除节点
        request=RemoveVServerGroupBackendServersRequest.RemoveVServerGroupBackendServersRequest()
        request.set_VServerGroupId(self.VServerGroupId)
        ecs_id=self.get_ecs_id(dec_ip)
        # 删除节点的话:BackendServers要删除的节点
        BackendServers = [
            {'ServerId': str(ecs_id), 'Port': self.port},
        ]
        res=self.common(request,BackendServers)
        self.logger_console.info("slb加注释")
        self.logger_root.info("slb加注释")
        self.logger_root.info(res)
        return res

    def add_slb(self,dec_ip):
        #添加节点
        request=AddVServerGroupBackendServersRequest.AddVServerGroupBackendServersRequest()
        request.set_VServerGroupId(self.VServerGroupId)
        #添加节点的话:BackendServers要所有节点
        # BackendServers = [
        #     {'ServerId': 'i-2zeb3hjhdcuoqikqrjzu', 'Port': '80'},
        #     {'ServerId': 'i-2ze0hm1pb2afhex6htds', 'Port': '80'}
        # ]
        ecs_id = self.get_ecs_id(dec_ip)
        add_ser={'ServerId': str(ecs_id), 'Port': self.port, 'Weight': self.weight}
        BackendServers = self.get_backendservers()
        BackendServers.append(add_ser)
        res=self.common(request, BackendServers)
        self.logger_console.info("slb解注释")
        self.logger_root.info("slb解注释")
        self.logger_root.info(res)
        return res


