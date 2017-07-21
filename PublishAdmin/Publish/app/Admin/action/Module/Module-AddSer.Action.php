<?php
class ModuleAddSerAction extends ModuleAction 
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
        }


        if($do = $this->context->get('do')){
            $this->$do();
        }
	}

    public function addserType(){

        $this->template = strtolower($this->context->uri["module"]) . "-confirmupdate";  //这行必须有
        $this->data['templateBtn'] = '<a href="'. C('LtUrl')->generate('Module', 'AddSer', array('name'=>$this->data['name'], 'do'=>'directAddSer')).'"> <button type="button" class="btn btn-success btn-lg">确认扩容</button></a>
   ';

    }

    public function directAddSer(){

        $this->template = strtolower($this->context->uri["module"]) . "-confirmupdate"; //这行必须有
        $msg = '';

        //执行更新远程文件
        $info = $this->getLibObject("ShellService")->doShell($this->data['name'], 'Addserver', '-A');
        $msg = '';
        $out = '';
        if($info['status']===0){
            $msg = '扩容操作执行完成！';
            foreach($info['out'] as $val){
                $out .= $val."\n";
            }

        }else{
            $msg = '扩容操作未执行！';

        }


        $this->data['templateBtn'] = '<a href="'. C('LtUrl')->generate('Module', 'List').'"> <button type="button" class="btn btn-success btn-lg">'.$msg.' 返回到列表页</button></a><br />
   ';
        if($out) $this->data['templateBtn'] .= '<textarea name="content" class="span7" rows="8">'.$out.'</textarea><br />';
    }
}
