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
  <strong>Jump to:</strong>
        <a href="#RFID" class="btn btn-default ">
        <i class='fa  fa-credit-card'></i> RFID cards
        </a>
        <a href="#volume" class="btn btn-default ">
        <i class='fa  fa-bullhorn'></i> Volume Settings
        </a>
        <a href="#autoShutdown" class="btn btn-default ">
        <i class='fa  fa-clock-o'></i> Auto Shutdown / Sleep Timer
        </a>
        <a href="#wifi" class="btn btn-default ">
        <i class='fa  fa-wifi'></i> WiFi Settings
        </a>
        <a href="#externalInterfaces" class="btn btn-default ">
        <i class='fa  fa-usb'></i> External Devices & Interfaces
        </a>
  </div>
</div>
        <br/>
<div class="panel-group">
  <div class="panel panel-default">
    <div class="panel-heading">
      <h4 class="panel-title"><a name="RFID"></a>
         <i class='fa fa-credit-card'></i> Manage Files and Chips
      </h4>
    </div><!-- /.panel-heading -->

      <div class="panel-body">
        <div class="row">
          <div class="col-lg-12">
                <a href="cardRegisterNew.php" class="btn btn-primary btn">
                <i class='fa  fa-plus-circle'></i> Register new card ID
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
         <i class='fa fa-bullhorn'></i> Volume Settings
      </h4>
    </div><!-- /.panel-heading -->

    <div class="panel-body">
      <div class="row">
<?php
include("inc.volumeSelect.php");

include("inc.maxVolumeSelect.php");

include("inc.volumeStepSelect.php");
?>
      </div><!-- / .row -->
    </div><!-- /.panel-body -->

  </div><!-- /.panel -->
</div><!-- /.panel-group -->

<div class="panel-group">
  <div class="panel panel-default">
    <div class="panel-heading">
      <h4 class="panel-title"><a name="autoShutdown"></a>
        <i class='fa fa-clock-o'></i> Auto Shutdown Settings
      </h4>
    </div><!-- /.panel-heading -->
    <div class="panel-body">

        <div class="row">

<?php
include("inc.sleeptimerSelect.php");
?>

        </div><!-- / .row -->

        <div class="row">
<?php
include("inc.idleShutdownSelect.php");
?>
        </div><!-- / .row -->

    </div><!-- /.panel-body -->
    
  </div><!-- /.panel -->
</div><!-- /.panel-group -->

<div class="panel-group">
  <div class="panel panel-default">
    <div class="panel-heading">
      <h4 class="panel-title"><a name="wifi"></a>
        <i class='fa fa-wifi'></i> WiFi Settings
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
        <i class='fa fa-usb'></i> External Devices & Interfaces
      </h4>
    </div><!-- /.panel-heading -->
    
      <div class="panel-body">
<?php
include("inc.inputDevicesSettings.php");
?>
      </div><!-- /.panel-body -->
    
  </div><!-- /.panel -->
</div><!-- /.panel-group -->

</div><!-- /.container -->

</body>
</html>
