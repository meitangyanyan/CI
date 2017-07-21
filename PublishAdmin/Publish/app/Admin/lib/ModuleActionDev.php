<?php
class ModuleActionDev extends LtAction {

    private $_libObjects = array();

	public function __construct() {
		parent::__construct ();
	}

    public function getLibObject($objectName){

        if(!isset($this->_libObjects[$objectName]) || !is_object($this->_libObjects[$objectName]))
            $this->_libObjects[$objectName] = new $objectName();
        return $this->_libObjects[$objectName];
    }
    
}
				
