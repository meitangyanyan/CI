

<legend>模块列表</legend>
<table class="table table-striped table-hover ">
    <thead>
    <tr>
        <th>模块名称</th>
        <th>仓库路径</th>
        <th>ip</th>
        <th>服务端口</th>
        <th>分支</th>
     <!--   <th>配置详情</th> -->
        <th>操作</th>
    </tr>
    </thead>
    <tbody>
    <?php foreach($this->data['list'] as $key=>$val):
        if(empty($val)) continue;
        ?>
    <tr>
        <td><?php echo $key;?></td>
        <td><?php if(isset($val['repo_path'])){echo $val['repo_path'];unset($val['repo_path']);}?></td>
        <td><?php echo $val['ip'];unset($val['ip']);?></td>
        <td><?php if(isset($val['port_list'])){echo $val['port_list'];unset($val['port_list']);}?></td>
        <td><?php if(isset($val['branch'])){echo $val['branch'];unset($val['branch']);}?></td>
        <!--<td><?php
            if(isset($val['is_compress'])){
                echo "is_compress:".($val['is_compress'] ? "True" : "False")."<br />";
                unset($val['is_compress']);
            }
            foreach($val as $k=>$v){
                echo "$k:$v<br/>";
            }
            ?></td>-->
        <td><div class="bs-component" style="margin-bottom: 40px;">

                <a class="label label-warning" href="{url("Module","Edit",array('name'=>$key))}">编辑</a>
                <a class="label label-info" href="{url("Module","Gray",array('name'=>$key,'do'=>'GrayType'))}">灰度</a>
                <a class="label label-important" href="{url("Module","Update",array('name'=>$key,'do'=>'updateType'))}">上线</a>
                <a class="label label-danger" href="{url("Module","Rollback",array('name'=>$key))}">回滚</a>
                <a class="label label-info" href="{url("Module","AddSer",array('name'=>$key,'do'=>'addserType'))}">扩容</a>
                <a class="label label-warning" href="{url("Module","DecSer",array('name'=>$key,'do'=>'decserType'))}">缩容</a>
                <a class="label label-important" href="{url("Module","Restart",array('name'=>$key,'do'=>'restartType'))}">重启</a>
                <a class="label label-success" href="{url("Module","CheckSer",array('name'=>$key,'do'=>'CheckType'))}">检测</a>
                <!--<a class="label label-info"  href="{url("Module","Backup",array('name'=>$key))}">备份</a>
                <a class="label label-important" href="{url("Module","Replace",array('name'=>$key,'do'=>'replaceType'))}">替换</a>-->

            </div></td>
    </tr>
    <?php endforeach;?>

    </tbody>
</table>
