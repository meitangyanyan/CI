<?php
class ModuleDockerAction extends ModuleAction 
{
	public function __construct() {
		parent::__construct ();
	}
	
	public function execute() {

        $this->data['name'] = $this->context->get('name');


        if(!$this->data['name']){
            $this->data['forward'] = 'goback';
            $this->code = 403;
            $this->layout = "resultPage";
            return;
        }

        //取得版本列表
        $moduleService = $this->getLibObject('ModuleService');
        $configs = $moduleService->getConfig();

        $backupDir = $configs['path']['backup_path'].'/'.$this->data['name'].'/*';
        $this->data['module_version'] = glob($backupDir);

        echo "get",$this->context->get('do');

        if($do = $this->context->get('do')){
            $this->$do();
            return;
        }
echo "exec done";

	}

    public function run(){
echo "run start";


        if($this->context->post('version_type')==1){

            //回滚
            $info = $this->getLibObject("ShellService")->doShell($this->data['name'], 'rollback');

        }elseif($this->context->post('version_type')==2){

            $version = $this->context->post("version");

            //回滚
            $info = $this->getLibObject("ShellService")->doShell($this->data['name'], 'rollback', '-V '.$version);

        }else{
            $info['status'] = 1;
        }



        $msg = '';
        $out = '';
        if($info['status']===0){
            $msg = '模块回滚操作执行完成！';
            foreach($info['out'] as $val){
                $out .= $val."\n";
            }

        }else{
            $msg = '模块回滚操作未执行！';

        }


        $this->data['templateBtn'] = '<a href="'. C('LtUrl')->generate('Module', 'List').'"> <button type="button" class="btn btn-success btn-lg">'.$msg.' 返回到列表页</button></a><br />
   ';
        if($out) $this->data['templateBtn'] .= '<textarea name="content" class="span7" rows="8">'.$out.'</textarea><br />';

        $this->template = strtolower($this->context->uri["module"]) . "-rollback" . strtolower($this->context->get("do"));
    }
}
