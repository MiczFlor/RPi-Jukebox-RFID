<?php

include("inc.header.php");
$debug="false"; // true|false
/*******************************************
* START HTML
*******************************************/

html_bootstrap3_createHeader("en","Phoniebox",$conf['base_url']);

?>
<body>
  <div class="container">

<?php
include("inc.navigation.php");

if($debug == "true") {
    print "<pre>";
    print "_POST:\n";
    print_r($_POST);
    print "</pre>";
}

?>

<div class="row">
  <div class="col-lg-12">
  <strong><?php print $lang['globalJumpTo']; ?>:</strong>
        <a href="#RFID" class="xbtn xbtn-default ">
        <i class='fa  fa-credit-card'></i> <?php print $lang['globalRFIDCards']; ?>
        </a> | 
        <a href="#volume" class="xbtn xbtn-default ">
        <i class='fa  fa-bullhorn'></i> <?php print $lang['globalVolumeSettings']; ?>
        </a> | 
        <a href="#autoShutdown" class="xbtn xbtn-default ">
        <i class='fa  fa-clock-o'></i> <?php print $lang['globalIdleShutdown']." / ".$lang['globalSleepTimer']; ?>
        </a> | 
        <a href="#wifi" class="xbtn xbtn-default ">
        <i class='fa  fa-wifi'></i> <?php print $lang['globalWifiSettings']; ?>
        </a> | 
        <a href="#externalInterfaces" class="xbtn xbtn-default ">
        <i class='fa  fa-usb'></i> <?php print $lang['globalExternalInterfaces']; ?>
        </a> 
  </div>
</div>
        <br/>
<div class="panel-group">
  <div class="panel panel-default">
    <div class="panel-heading">
      <h4 class="panel-title"><a name="RFID"></a>
         <i class='fa fa-credit-card'></i> <?php print $lang['indexManageFilesChips']; ?>
      </h4>
    </div><!-- /.panel-heading -->

      <div class="panel-body">
        <div class="row">
          <div class="col-lg-12">
                <a href="cardRegisterNew.php" class="btn btn-primary btn">
                <i class='fa  fa-plus-circle'></i> <?php print $lang['globalRegisterCard']; ?>
                </a>
          </div><!-- / .col-lg-12 -->
        </div><!-- /.row -->
      </div><!-- /.panel-body -->

    </div><!-- /.panel -->
</div><!-- /.panel-group -->

<div class="panel-group">
  <div class="panel panel-default">
    <div class="panel-heading">
      <h4 class="panel-title"><a name="volume"></a>
         <i class='fa fa-bullhorn'></i> <?php print $lang['globalVolumeSettings']; ?>
      </h4>
    </div><!-- /.panel-heading -->

    <div class="panel-body">
      <div class="row">
<?php
include("inc.setVolume.php");

include("inc.setMaxVolume.php");

include("inc.setVolumeStep.php");
?>
      </div><!-- / .row -->
    </div><!-- /.panel-body -->

  </div><!-- /.panel -->
</div><!-- /.panel-group -->

<div class="panel-group">
  <div class="panel panel-default">
    <div class="panel-heading">
      <h4 class="panel-title"><a name="autoShutdown"></a>
        <i class='fa fa-clock-o'></i> <?php print $lang['globalAutoShutdown']." ".$lang['globalSettings']; ?>
      </h4>
    </div><!-- /.panel-heading -->
    <div class="panel-body">

        <div class="row">

<?php
include("inc.setSleeptimer.php");
?>

        </div><!-- / .row -->

        <div class="row">
<?php
include("inc.setIdleShutdown.php");
?>
        </div><!-- / .row -->

    </div><!-- /.panel-body -->
    
  </div><!-- /.panel -->
</div><!-- /.panel-group -->

<div class="panel-group">
  <div class="panel panel-default">
    <div class="panel-heading">
      <h4 class="panel-title"><a name="wifi"></a>
        <i class='fa fa-wifi'></i> <?php print $lang['globalWifiSettings']; ?>
      </h4>
    </div><!-- /.panel-heading -->
    
      <div class="panel-body">
<?php
include("inc.setWifi.php");
?>
      </div><!-- /.panel-body -->
    
  </div><!-- /.panel -->
</div><!-- /.panel-group -->

<div class="panel-group">
  <div class="panel panel-default">
    <div class="panel-heading">
      <h4 class="panel-title"><a name="externalInterfaces"></a>
        <i class='fa fa-usb'></i> <?php print $lang['globalExternalInterfaces']; ?>
      </h4>
    </div><!-- /.panel-heading -->
    
      <div class="panel-body">
<?php
include("inc.setInputDevices.php");
?>
      </div><!-- /.panel-body -->
    
  </div><!-- /.panel -->
</div><!-- /.panel-group -->

</div><!-- /.container -->

</body>
</html>
