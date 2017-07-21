
<table border="1" class="table table-striped table-hover ">
    <thead>
    <tr>
        <th>模块名称</th>
        <th>ip</th>
        <th>服务端口</th>
        <th>分支</th>
     <!--   <th>配置详情</th> -->
    </tr>
    </thead>
    <tbody>
    <?php foreach($this->data['list'] as $key=>$val):
        if(empty($val)) continue;
        ?>
    <tr>
        <td><?php echo $key;?></td>
        <td><?php echo $val['ip'];unset($val['ip']);?></td>
        <td><?php if(isset($val['port_list'])){echo $val['port_list'];unset($val['port_list']);}?></td>
        <td><?php if(isset($val['branch'])){echo $val['branch'];unset($val['branch']);}?></td>
    </tr>
    <?php endforeach;?>

    </tbody>
</table>
