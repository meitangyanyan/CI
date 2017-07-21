<!DOCTYPE html>
<html lang="zh-CN"><head>
    <meta charset="utf-8">
    <title><?php if(isset($this->code)) echo '[' .$this->code . '] ' . $this->data['title']; else echo $this->data['title']; ?></title>
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <meta name="description" content="">
    <meta name="author" content="">
<?php
    $jumpTime = 3;$jumpTimeMic = 3000;
    $baseURL = '/PublishAdmin/Web_Entrance/Admin/';
    if ('200' != $this->code) {
        $jumpTime = 3;$jumpTimeMic = 3000;
    }
?>
<?php if (isset($this->data['forward']) && !empty($this->data['forward']) && $this->data['forward'] != "goback") {?>
    <meta http-equiv="refresh" content="<?php echo $jumpTime;?>;URL=<?php echo $this->data['forward']?>" />
<?php }?>
    <base href="<?php echo $baseURL; ?>">
    <!-- Le styles -->
    <link rel="stylesheet" type="text/css" href="<?php echo $baseURL; ?>style/bootstrap/css/upload.css">
    <link rel="stylesheet" type="text/css" href="<?php echo $baseURL; ?>style/bootstrap/css/bootstrap.css">


    <!--[if lte IE 6]>
    <link rel="stylesheet" type="text/css" href="<?php echo $baseURL; ?>style/bootstrap/css/bootstrap-ie6.css">
    <![endif]-->
    <!--[if lte IE 7]>
    <link rel="stylesheet" type="text/css" href="<?php echo $baseURL; ?>style/bootstrap/css/ie.css">
    <![endif]-->

    <style type="text/css">
        body {
            padding-top: 60px;
            padding-bottom: 40px;
        }
    </style>

    <!-- HTML5 shim, for IE6-8 support of HTML5 elements -->
    <!--[if lt IE 9]>
    <script src="http://html5shim.googlecode.com/svn/trunk/html5.js"></script>
    <![endif]-->

    <!-- Fav and touch icons -->
    <link rel="apple-touch-icon-precomposed" sizes="144x144" href="<?php echo $baseURL; ?>style/assets/ico/apple-touch-icon-144-precomposed.png">
    <link rel="apple-touch-icon-precomposed" sizes="114x114" href="<?php echo $baseURL; ?>style/assets/ico/apple-touch-icon-114-precomposed.png">
    <link rel="apple-touch-icon-precomposed" sizes="72x72" href="<?php echo $baseURL; ?>style/assets/ico/apple-touch-icon-72-precomposed.png">
    <link rel="apple-touch-icon-precomposed" href="<?php echo $baseURL; ?>style/assets/ico/apple-touch-icon-57-precomposed.png">
    <link rel="shortcut icon" href="<?php echo $baseURL; ?>style/assets/ico/favicon.png">
<?php if (isset($this->data [ "HEADERJQ" ]) && $this->data [ "HEADERJQ" ]){?>
    <script src="<?php echo $baseURL; ?>style/js/jquery.js?v=1" type="text/javascript"></script>
<?php }?>
<?php if (isset($this->data['forward']) && !empty($this->data['forward']) && $this->data['forward'] == 'goback'){?>
    <script type="text/javascript">
        setTimeout("history.go(-1)",<?php echo $jumpTimeMic;?>);
    </script>
<?php }?>
</head>
<body>
