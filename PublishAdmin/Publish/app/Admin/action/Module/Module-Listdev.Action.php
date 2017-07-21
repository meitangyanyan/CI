<?php
class ModuleListdevAction extends ModuleActionDev
{
	public function execute() {
        $this->data['list'] = $this->getLibObject("ModuleService")->getList();
	}

}
