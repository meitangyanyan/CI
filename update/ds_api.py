#/usr/bin/env python
#__*__ coding:utf-8 __*__

from flask import Flask,request
from flask_restful import Api,Resource,reqparse
from ConfigParser import ConfigParser
import os,sys,subprocess,json

prefix=os.path.dirname(os.path.abspath(__file__))
cf=ConfigParser()
conf_file=prefix + "/conf/mod.ini"
if not os.path.exists(conf_file):
    print "配置文件不存在!"
    sys.exit()
cf.read(conf_file)

app = Flask(__name__)
api=Api(app)

result={"status":"0","message":None,"detail":None}
action_list=["update","gray_update"]

def run_comm(cmd):
    p = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    out = p.stdout.read()
    return out

class Deploy(Resource):
    def post(self):
        print request.headers
        data=eval(request.data)
        #data=request.data
        print "-"*30
        print data
        print "-"*30
        if type(data) != dict and type(data) == str:
            data=json.loads(data)
        print "="*30
        print data
        print "="*30
        if "action" in data:
            action=data["action"]
        else:
            action=None
        if "mod_name" in data:
            mod_name = data["mod_name"]
        else:
            mod_name=None
        if "branch" in data:
            branch=data["branch"]
        else:
            branch="master"
        if "tag" in data:
            tag=data["tag"]
        else:
            tag=None
        print action,mod_name,branch,tag
        if not cf.has_section(mod_name):
            result["message"]="no mod_name!"
            print result
            return result
        if action not in action_list:
            result["message"] ="no action!"
            print result
            return result
        cf.read(conf_file)
        if branch:
            cf.set(mod_name,"branch",branch)
        if tag:
            cf.set(mod_name,"tag",tag)
        cf.write(open(conf_file,"w"))
        cmd="python %s/update.py -m %s -a %s -A" % (prefix,mod_name,action)
        out=run_comm(cmd)
        if "update failure" in out:
            result["status"]="0"
            result["message"]="failure!"
        else:
            result["status"]="1"
            result["message"]="sucessful!"
        result["detail"] = out
        return result

class Modlist(Resource):
    def post(self):
        mod_list=[]
        dec_list=["common","docker","mysql","redis","lb"]
        for i in cf.sections():
            if i not in dec_list:
                mod_list.append(i)
        return mod_list

class Imagelist(Resource):
    def post(self):
        print request.headers
        data = eval(request.data)
        if type(data) != dict and type(data) == str:
            data = json.loads(data)
        if "mod_name" in data:
            mod_name = data["mod_name"]
        else:
            mod_name = None
        if not cf.has_section(mod_name):
            result["message"] = "no mod_name!"
            return result
        url = "xxx"#docker镜像私库地址
        cmd = "curl -s -X GET --header 'Accept: application/json' 'https://%s/api/repositories/tags?repo_name=prod%%2F%s'" % (url, mod_name)
        p = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
        out = eval(p.stdout.read())
        image_list=sorted(out, reverse=True)
        return image_list

api.add_resource(Deploy,"/deploy")
api.add_resource(Modlist,"/modlist")
api.add_resource(Imagelist,"/imagelist")

if __name__ == "__main__":
    app.run(debug=True,threaded=True)
