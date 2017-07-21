
<legend>编辑模块</legend>
<form class="form-horizontal" method="post">
    <fieldset>

        <div class="control-group">
            <label for="name" class="control-label">模块名称：</label>
            <div class="col-lg-10">
                <input type="text" class="form-control" id="name" name="name" placeholder="name" value="<?php echo $this->data['name'];?>">（必填）
            </div>
        </div>
        <div class="control-group">
            <label for="lb_flag" class="control-label">负载选择：</label>
            <div class="col-lg-10">
                <select class="form-control" name="data[lb_flag]" id="select">
                    <?php
                        foreach($this->data['lbFlag'] as $val){
                            echo "<option ".($this->data['data']['lb_flag']==$val ? 'selected' : '').">$val</option>";
                        }
                    ?>
                </select>
            </div>
        </div>

        <div class="control-group">
            <label for="docker_flag" class="control-label">线上是否docker：</label>
            <div class="col-lg-10">
                <select class="form-control" name="data[docker_flag]" id="select">
                    <?php
                        foreach($this->data['dockerFlag'] as $val){
                            echo "<option ".($this->data['data']['docker_flag']==$val ? 'selected' : '').">$val</option>";
                        }
                    ?>
                </select>
            </div>
        </div>
        <div class="control-group">
            <label for="gray_docker_flag" class="control-label">灰度是否docker：</label>
            <div class="col-lg-10">
                <select class="form-control" name="data[gray_docker_flag]" id="select">
                    <?php
                        foreach($this->data['dockerFlag'] as $val){
                            echo "<option ".($this->data['data']['gray_docker_flag']==$val ? 'selected' : '').">$val</option>";
                        }
                    ?>
                </select>
            </div>
        </div>

        <div class="control-group">
            <label for="git_enabled" class="control-label">是否构建代码包：</label>
            <div class="col-lg-10">
                <select class="form-control" name="data[git_enabled]" id="select">
                    <?php
                        foreach($this->data['gitEnabled'] as $val){
                            echo "<option ".($this->data['data']['git_enabled']==$val ? 'selected' : '').">$val</option>";
                        }
                    ?>
                </select>选择False的话,从别的机器上传代码包,需要定义source_host/source_user等变量
            </div>
        </div>

        <div class="control-group">
            <label for="branch" class="control-label">分支：</label>
            <div class="col-lg-10">
                <input type="text" class="form-control" id="branch" name="data[branch]" placeholder="branch" value="<?php if(isset($this->data['data']['branch'])) echo $this->data['data']['branch'];?>">
            </div>
        </div>

        <div class="control-group">
            <label for="tag" class="control-label">tag：</label>
            <div class="col-lg-10">
                <input type="text" class="form-control" id="tag" name="data[tag]" placeholder="tag" value="<?php if(isset($this->data['data']['tag'])) echo $this->data['data']['tag'];?>">
            </div>
        </div>

        <div class="control-group">
            <label for="build_cmd" class="control-label">构建代码包命令：</label>
            <div class="col-lg-10">
                <input type="text" class="form-control" id="build_cmd" name="data[build_cmd]" placeholder="build_cmd" value="<?php if(isset($this->data['data']['build_cmd'])) echo $this->data['data']['build_cmd'];?>">
            </div>
        </div>

        <div class="control-group">
            <label for="ip" class="control-label">服务器IP：</label>
            <div class="col-lg-10">
                <input type="text" class="form-control" id="ip" name="data[ip]" placeholder="ip" value="<?php if(isset($this->data['data']['ip'])) echo $this->data['data']['ip'];?>"> (必填 多个ip 使用竖线（|）分割 ip = 1.1.1.1|2.2.2.2)
            </div>
        </div>
        <div class="control-group">
            <label for="gray_ip" class="control-label">灰度服务器IP：</label>
            <div class="col-lg-10">
                <input type="text" class="form-control" id="gray_ip" name="data[gray_ip]" placeholder="gray_ip" value="<?php if(isset($this->data['data']['gray_ip'])) echo $this->data['data']['gray_ip'];?>"> (默认为空 多个ip 使用竖线（|）分割 ip = 1.1.1.1|2.2.2.2)
            </div>
        </div>
        <div class="control-group">
            <label for="port" class="control-label">ssh端口：</label>
            <div class="col-lg-10">
                <input type="text" class="form-control" id="port" name="data[port]" placeholder="port" value="<?php if(isset($this->data['data']['port'])) echo $this->data['data']['port'];?>"> (不填默认是22)
            </div>
        </div>
        <div class="control-group">
            <label for="user" class="control-label">ssh用户名：</label>
            <div class="col-lg-10">
                <input type="text" class="form-control" id="user" name="data[user]" placeholder="user" value="<?php if(isset($this->data['data']['user'])) echo $this->data['data']['user'];?>"> (必填 多个用竖线（|）分割）
            </div>
        </div>

        <div class="control-group">
            <label for="password" class="control-label">ssh密码：</label>
            <div class="col-lg-10">
                <input type="text" class="form-control" id="password" name="data[password]" placeholder="password" value="<?php if(isset($this->data['data']['password'])) echo $this->data['data']['password'];?>">
            </div>
        </div>

        <div class="control-group">
            <label for="ssh_key" class="control-label">ssh_key：</label>
            <div class="col-lg-10">
                <input type="text" class="form-control" id="ssh_key" name="data[ssh_key]" placeholder="ssh_key" value="<?php if(isset($this->data['data']['ssh_key'])) echo $this->data['data']['ssh_key'];?>">
            </div>
        </div>

        <div class="control-group">
            <label for="package" class="control-label">代码包名称：</label>
            <div class="col-lg-10">
                <input type="text" class="form-control" id="package" name="data[package]" placeholder="package" value="<?php if(isset($this->data['data']['package'])) echo $this->data['data']['package'];?>"> (不填默认是模块名+".war")
            </div>
        </div>

        <div class="control-group">
            <label for="path" class="control-label">部署路径：</label>
            <div class="col-lg-10">
                <input type="text" class="form-control" id="path" name="data[path]" placeholder="path" value="<?php if(isset($this->data['data']['path'])) echo $this->data['data']['path'];?>">（必填）
            </div>
        </div>

        <div class="control-group">
            <label for="replicas" class="control-label">k8s副本数：</label>
            <div class="col-lg-10">
                <input type="text" class="form-control" id="replicas" name="data[replicas]" placeholder="replicas" value="<?php if(isset($this->data['data']['replicas'])) echo $this->data['data']['replicas'];?>">
            </div>
        </div>

        <div class="control-group">
            <label for="dns" class="control-label">容器的dns：</label>
            <div class="col-lg-10">
                <input type="text" class="form-control" id="dns" name="data[dns]" placeholder="dns" value="<?php if(isset($this->data['data']['dns'])) echo $this->data['data']['dns'];?>">（docker run选项,默认是127.0.0.1）
            </div>
        </div>

        <div class="control-group">
            <label for="vol_list" class="control-label">容器的卷：</label>
            <div class="col-lg-10">
                <input type="text" class="form-control" id="vol_list" name="data[vol_list]" placeholder="vol_list" value="<?php if(isset($this->data['data']['vol_list'])) echo $this->data['data']['vol_list'];?>">（docker run选项,多个用(|)分割,默认为空）
            </div>
        </div>

        <div class="control-group">
            <label for="port_list" class="control-label">容器暴露端口：</label>
            <div class="col-lg-10">
                <input type="text" class="form-control" id="port_list" name="data[port_list]" placeholder="port_list" value="<?php if(isset($this->data['data']['port_list'])) echo $this->data['data']['port_list'];?>">（docker run选项,多个用(|)分割,默认为空）
            </div>
        </div>

        <div class="control-group">
            <label for="check_url" class="control-label">检测URL：</label>
            <div class="col-lg-10">
                <input type="text" class="form-control" id="check_url" name="data[check_url]" placeholder="check_url" value="<?php if(isset($this->data['data']['check_url'])) echo $this->data['data']['check_url'];?>">（检测程序是否正常运行的API,默认为空）
            </div>
        </div>
        <div class="control-group">
            <label for="key_word" class="control-label">检测关键字：</label>
            <div class="col-lg-10">
                <input type="text" class="form-control" id="key_word" name="data[key_word]" placeholder="key_word" value="<?php if(isset($this->data['data']['key_word'])) echo $this->data['data']['key_word'];?>">（检测URL返回结果的关键字是否正确,默认为空）
            </div>
        </div>
        <div class="control-group">
            <label for="clone_flag" class="control-label">克隆选项：</label>
            <div class="col-lg-10">
                <input type="text" class="form-control" id="clone_flag" name="data[clone_flag]" placeholder="clone_flag" value="<?php if(isset($this->data['data']['clone_flag'])) echo $this->data['data']['clone_flag'];?>">（"1"表示要克隆,不填默认是"0"）
            </div>
        </div>

        <div class="control-group">
            <label for="url" class="control-label">远程仓库：</label>
            <div class="col-lg-10">
                <input type="text" class="form-control" id="url" name="data[url]" placeholder="url" value="<?php if(isset($this->data['data']['url'])) echo $this->data['data']['url'];?>">（必填）
            </div>
        </div>

        <div class="control-group">
            <label for="git_ip" class="control-label">本地仓库ip：</label>
            <div class="col-lg-10">
                <input type="text" class="form-control" id="git_ip" name="data[git_ip]" placeholder="git_ip" value="<?php if(isset($this->data['data']['git_ip'])) echo $this->data['data']['git_ip'];?>">（必填）
            </div>
        </div>

        <div class="control-group">
            <label for="git_user" class="control-label">本地仓库user：</label>
            <div class="col-lg-10">
                <input type="text" class="form-control" id="git_user" name="data[git_user]" placeholder="git_user" value="<?php if(isset($this->data['data']['git_user'])) echo $this->data['data']['git_user'];?>">（必填）
            </div>
        </div>

        <div class="control-group">
            <label for="git_password" class="control-label">本地仓库密码：</label>
            <div class="col-lg-10">
                <input type="text" class="git_password" id="git_password" name="data[git_password]" placeholder="git_password" value="<?php if(isset($this->data['data']['git_password'])) echo $this->data['data']['git_password'];?>">
            </div>
        </div>

        <div class="control-group">
            <label for="git_ssh_key" class="control-label">本地仓库ssh_key：</label>
            <div class="col-lg-10">
                <input type="text" class="git_ssh_key" id="git_ssh_key" name="data[git_ssh_key]" placeholder="git_ssh_key" value="<?php if(isset($this->data['data']['git_ssh_key'])) echo $this->data['data']['git_ssh_key'];?>">
            </div>
        </div>

        <div class="control-group">
            <label for="git_port" class="control-label">本地仓库ssh端口：</label>
            <div class="col-lg-10">
                <input type="text" class="form-control" id="git_port" name="data[git_port]" placeholder="git_port" value="<?php if(isset($this->data['data']['git_port'])) echo $this->data['data']['git_port'];?>">（不填默认是22）
            </div>
        </div>
        <div class="control-group">
            <label for="repo_path" class="control-label">本地仓库目录：</label>
            <div class="col-lg-10">
                <input type="text" class="form-control" id="repo_path" name="data[repo_path]" placeholder="repo_path" value="<?php if(isset($this->data['data']['repo_path'])) echo $this->data['data']['repo_path'];?>">（必填）
            </div>
        </div>

        <div class="control-group">
            <label for="more_args" class="control-label">更多参数：</label>
            <div class="col-lg-10">
                <table>
                    <tr><td>
                            <textarea name="data_more" class="form-control" rows="8" placeholder="k1=v1">
                                <?php
                                $unset_data = array('name','lb_flag','docker_flag','gray_docker_flag','git_enabled','branch','tag','build_cmd','ip','gray_ip','port','user','password','ssh_key','package','path','replicas','dns','vol_list','port_list','check_url','key_word','clone_flag','url','git_ip','git_user','git_password','git_ssh_key','git_port','repo_path');
                                foreach($unset_data as $k){
                                    if(isset($this->data['data'][$k])) unset($this->data['data'][$k]);
                                }

                                foreach($this->data['data'] as $k=>$v){
                                    echo "$k=$v\n";
                                }

                                ?>
                            </textarea>
                        </td><td>
                            (内容为k/v格式，以换行分割 如下:<br>
                            k1=v1<br>
                            k2=v2
                            <br>)
                        </td></tr></table>
            </div>
        </div>

        <div class="form-group">
            <div class="offset2">
                <button class="btn btn-default">取消</button>
                <button type="submit" class="btn btn-primary">提交</button>
            </div>
        </div>
    </fieldset>
</form>
