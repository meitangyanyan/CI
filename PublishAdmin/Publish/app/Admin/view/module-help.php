
<legend>使用说明</legend>

    <?php 
        $file_handle = fopen("/usr/share/zabbix/PublishAdmin/publishModules/shell/readme", "r");
        $i=0;
        while (!feof($file_handle)) {
            $i++;
            $line=fgets($file_handle); 
            if (strstr($line,"模块")) {
                echo '<font color="green">',$line,'</font><br>';
                }
            else if (strstr($line,":")) {
                $b=explode(':',$line);
                echo '<font color="black">',$b[0],':','<font color="grey">',$b[1],'</font><br>';
                }
            else {
                echo $line,'<br>';
                }
            }          
            fclose($file_handle);
    ?>
