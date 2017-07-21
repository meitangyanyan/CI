
<legend>新增模块</legend>
<form class="form-horizontal" method="post">
    <fieldset>

        <div class="control-group">
            <label for="name" class="control-label">模块名称：</label>
            <div class="col-lg-10">
                <input type="text" class="form-control" id="name" name="name" placeholder="name">（必填）
            </div>
        </div>
        <div class="control-group">
            <label for="select" class="control-label">模块类型：</label>
            <div class="col-lg-10">
                <select class="form-control" name="data[type]" id="select">
                    <?php
                    foreach($this->data['moduleType'] as $val){
                        echo "<option>$val</option>";
                    }
                    ?>
                </select>
            </div>
        </div>

        <div class="control-group">
            <label for="is_compress" class="control-label">上传文件是否是压缩包：</label>
            <div class="col-lg-10">
                <input type="text" class="form-control" id="is_compress" name="data[is_compress]" placeholder="is_compress">（True or False,不填默认False）
            </div>
        </div>

        <div class="control-group">
            <label for="clone_flag" class="control-label">克隆选项：</label>
            <div class="col-lg-10">
                <input type="text" class="form-control" id="clone_flag" name="data[clone_flag]" placeholder="clone_flag">（"1"表示要克隆,不填默认是"0"）
            </div>
        </div>

        <div class="control-group">
            <label for="url" class="control-label">远程仓库：</label>
            <div class="col-lg-10">
                <input type="text" class="form-control" id="url" name="data[url]" placeholder="url">（必填）
            </div>
        </div>

        <div class="control-group">
            <label for="repo_path" class="control-label">本地仓库目录：</label>
            <div class="col-lg-10">
                <input type="text" class="form-control" id="repo_path" name="data[repo_path]" placeholder="repo_path">（必填）
            </div>
        </div>

        <div class="control-group">
            <label for="branch" class="control-label">分支：</label>
            <div class="col-lg-10">
                <input type="text" class="form-control" id="branch" name="data[branch]" placeholder="branch">（必填）
            </div>
        </div>

        <div class="control-group">
            <label for="git_ip" class="control-label">本地仓库ip：</label>
            <div class="col-lg-10">
                <input type="text" class="form-control" id="git_ip" name="data[git_ip]" placeholder="git_ip">（必填）
            </div>
        </div>
        
        <div class="control-group">
            <label for="git_user" class="control-label">本地仓库user：</label>
            <div class="col-lg-10">
                <input type="text" class="form-control" id="git_user" name="data[git_user]" placeholder="git_user">（必填）
            </div>
        </div>

        <div class="control-group">
            <label for="git_password" class="control-label">本地仓库密码：</label>
            <div class="col-lg-10">
                <input type="text" class="form-control" id="git_password" name="data[git_password]" placeholder="git_password">（必填）
            </div>
        </div>

        <div class="control-group">
            <label for="git_port" class="control-label">本地仓库ssh端口：</label>
            <div class="col-lg-10">
                <input type="text" class="form-control" id="git_port" name="data[git_port]" placeholder="git_port">（不填默认22）
            </div>
        </div>

        <div class="control-group">
            <label for="path" class="control-label">部署路径：</label>
            <div class="col-lg-10">
                <input type="text" class="form-control" id="path" name="data[path]" placeholder="path">（必填）
            </div>
        </div>

        <div class="control-group">
            <label for="ip" class="control-label">服务器IP：</label>
            <div class="col-lg-10">
                <input type="text" class="form-control" id="ip" name="data[ip]" placeholder="ip">(必填 多个ip 使用竖线（|）分割 ip = 1.1.1.1|2.2.2.2)
            </div>
        </div>

        <div class="control-group">
            <label for="gray_ip" class="control-label">灰度服务器IP：</label>
            <div class="col-lg-10">
                <input type="text" class="form-control" id="gray_ip" name="data[gray_ip]" placeholder="gray_ip">(默认为空 多个ip 使用竖线（|）分割 ip = 1.1.1.1|2.2.2.2)
            </div>
        </div>
        <div class="control-group">
            <label for="port" class="control-label">ssh端口：</label>
            <div class="col-lg-10">
                <input type="text" class="form-control" id="port" name="data[port]" placeholder="port">(不填默认22)
            </div>
        </div>

        <div class="control-group">
            <label for="tomcat_path" class="control-label">tomcat路径：</label>
            <div class="col-lg-10">
                <input type="text" class="form-control" id="tomcat_path" name="data[tomcat_path]" placeholder="tomcat_path">
            </div>
        </div>

        <div class="control-group">
            <label for="ser_port" class="control-label">程序端口：</label>
            <div class="col-lg-10">
                <input type="text" class="form-control" id="ser_port" name="data[ser_port]" placeholder="ser_port">(必填)
            </div>
        </div>        

        <div class="control-group">
            <label for="user" class="control-label">ssh用户名：</label>
            <div class="col-lg-10">
                <input type="text" class="form-control" id="user" name="data[user]" placeholder="user">（用户名 多个用竖线（|）分割）
            </div>
        </div>

        <div class="control-group">
            <label for="password" class="control-label">ssh密码：</label>
            <div class="col-lg-10">
                <input type="text" class="form-control" id="password" name="data[password]" placeholder="password">（密码 多个用线（|）分割）
            </div>
        </div>

        <div class="control-group">
            <label for="docker_flag" class="control-label">docker选项：</label>
            <div class="col-lg-10">
                <input type="text" class="form-control" id="docker_flag" name="data[docker_flag]" placeholder="docker_flag">（使用docker:"1",默认为"0"）
            </div>
        </div>
        <div class="control-group">
            <label for="container" class="control-label">容器名：</label>
            <div class="col-lg-10">
                <input type="text" class="form-control" id="container" name="data[container]" placeholder="container">（使用docker的话必填）
            </div>
        </div>
        <div class="control-group">
            <label for="restart" class="control-label">docker run --restart=：</label>
            <div class="col-lg-10">
                <input type="text" class="form-control" id="restart" name="data[restart]" placeholder="restart">（默认为"always"）
            </div>
        </div>
        <div class="control-group">
            <label for="dns" class="control-label">docker run --dns=：</label>
            <div class="col-lg-10">
                <input type="text" class="form-control" id="dns" name="data[dns]" placeholder="dns">（默认为"127.0.0.1"）
            </div>
        </div>
        <div class="control-group">
            <label for="vol_list" class="control-label">docker run -v ：</label>
            <div class="col-lg-10">
                <input type="text" class="form-control" id="vol_list" name="data[vol_list]" placeholder="vol_list">（多个用竖线（|）分割,默认为空）
            </div>
        </div>
        <div class="control-group">
            <label for="port_list" class="control-label">docker run -p ：</label>
            <div class="col-lg-10">
                <input type="text" class="form-control" id="port_list" name="data[port_list]" placeholder="port_list">（多个用竖线（|）分割,默认为空）
            </div>
        </div>

        <div class="control-group">
            <label for="option" class="control-label">docker run其他参数 ：</label>
            <div class="col-lg-10">
                <input type="text" class="form-control" id="option" name="data[option]" placeholder="option">(默认为空）
            </div>
        </div>

        <div class="control-group">
            <label for="file_name" class="control-label">替换文件名：</label>
            <div class="col-lg-10">
                <input type="text" class="form-control" id="file_name" name="data[file_name]" placeholder="file_name">(默认为空）
            </div>
        </div>

        <div class="control-group">
            <label for="old_content" class="control-label">旧内容：</label>
            <div class="col-lg-10">
                <input type="text" class="form-control" id="old_content" name="data[old_content]" placeholder="old_content">(默认为空）
            </div>
        </div>

        <div class="control-group">
            <label for="new_content" class="control-label">新内容：</label>
            <div class="col-lg-10">
                <input type="text" class="form-control" id="new_content" name="data[new_content]" placeholder="new_content">(默认为空）
            </div>
        </div>

        <div class="control-group">
            <label for="is_compress2" class="control-label">更多参数：</label>
            <div class="col-lg-10">
                <table>
                    <tr><td>
                <textarea name="data_more" class="form-control" rows="8" placeholder="k1=v1">
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
                <button type="submit" class="btn btn-primary">提交</button>
            </div>
        </div>
    </fieldset>
</form>
