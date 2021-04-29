<?php

include("inc.header.php");

/*******************************************
* START HTML
*******************************************/

html_bootstrap3_createHeader("en","Settings | Phoniebox",$conf['base_url']);

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
        <i class='mdi mdi-cards-outline'></i> <?php print $lang['globalRFIDCards']; ?>
        </a> |
        <a href="#language" class="xbtn xbtn-default ">
        <i class='mdi mdi-emoticon'></i> <?php print $lang['globalLanguageSettings']; ?>
        </a> |
        <a href="#volume" class="xbtn xbtn-default ">
        <i class='mdi mdi-volume-high'></i> <?php print $lang['globalVolumeSettings']; ?>
        </a> |
        <a href="#autoShutdown" class="xbtn xbtn-default ">
        <i class='mdi mdi-clock-end'></i> <?php print $lang['globalIdleShutdown']." / ".$lang['globalSleepTimer']; ?>
        </a> |
        <a href="#wifi" class="xbtn xbtn-default ">
        <i class='mdi mdi-wifi'></i> <?php print $lang['globalWifiSettings']; ?>
        </a> |
        <!--a href="#wlanIpEmail" class="xbtn xbtn-default ">
        <i class='mdi mdi-wifi'></i> <?php print $lang['settingsWlanSendNav']; ?>
        </a>  |-->
        <a href="#wlanIpRead" class="xbtn xbtn-default ">
        <i class='mdi mdi-wifi'></i> <?php print $lang['settingsWlanReadNav']; ?>
        </a>  |
        <a href="#webInterface" class="xbtn xbtn-default ">
        <i class='mdi mdi-cards-outline'></i> <?php print $lang['settingsWebInterface']; ?>
        </a>  |
        <a href="#externalInterfaces" class="xbtn xbtn-default ">
        <i class='mdi mdi-usb'></i> <?php print $lang['globalExternalInterfaces']; ?>
        </a>  |
        <a href="#secondSwipe" class="xbtn xbtn-default ">
        <i class='mdi mdi-cards-outline'></i> <?php print $lang['settingsSecondSwipe']; ?>
        </a> |
        <a href="#DebugLogSettings" class="xbtn xbtn-default ">
        <i class='mdi mdi-text'></i> <?php print $lang['infoDebugLogSettings']; ?>
        </a>

  </div>
</div>
        <br/>
<div class="panel-group">
  <div class="panel panel-default">
    <div class="panel-heading">
      <h4 class="panel-title"><a name="RFID"></a>
         <i class='mdi mdi-cards-outline'></i> <?php print $lang['indexManageFilesChips']; ?>
      </h4>
    </div><!-- /.panel-heading -->

      <div class="panel-body">
        <div class="row">
          <div class="col-lg-12">
                <a href="cardRegisterNew.php" class="btn btn-primary btn">
                <i class='mdi mdi-cards-outline'></i> <?php print $lang['globalRegisterCard']; ?>
                </a>
          </div><!-- / .col-lg-12 -->
        </div><!-- /.row -->
      </div><!-- /.panel-body -->

    </div><!-- /.panel -->
</div><!-- /.panel-group -->

<div class="panel-group">
  <div class="panel panel-default">
    <div class="panel-heading">
      <h4 class="panel-title"><a name="language"></a>
         <i class='mdi mdi-emoticon'></i> <?php print $lang['globalLanguageSettings']; ?>
      </h4>
    </div><!-- /.panel-heading -->

    <div class="panel-body">
      <div class="row">
<?php
include("inc.setLanguage.php");
?>
      </div><!-- / .row -->
    </div><!-- /.panel-body -->

<div class="panel-group">
  <div class="panel panel-default">
    <div class="panel-heading">
      <h4 class="panel-title"><a name="language"></a>
         <i class='mdi mdi-emoticon'></i> <?php print $lang['settingsPlayoutBehaviourCard']; ?>
      </h4>
    </div><!-- /.panel-heading -->
    
    <div class="panel-body">
      <div class="row">
<?php
include("inc.setPlayerBehaviourRFID.php");
?>
      </div><!-- / .row -->
    </div><!-- /.panel-body -->

  </div><!-- /.panel -->
</div><!-- /.panel-group -->

<div class="panel-group">
  <div class="panel panel-default">
    <div class="panel-heading">
      <h4 class="panel-title"><a name="volume"></a>
         <i class='mdi mdi-volume-high'></i> <?php print $lang['globalVolumeSettings']; ?>
      </h4>
    </div><!-- /.panel-heading -->

    <div class="panel-body">
      <div class="row">
<?php
include("inc.setVolume.php");
include("inc.setMaxVolume.php");
include("inc.setVolumeStep.php");
include("inc.setStartupVolume.php");
?>
      </div><!-- / .row -->
    </div><!-- /.panel-body -->

  </div><!-- /.panel -->
</div><!-- /.panel-group -->


<?php
$filename = $conf['settings_abs'].'/bluetooth-sink-switch';
if (file_exists($filename)) {
   if (strcmp(strtolower(trim(file_get_contents($filename))), "enabled") === 0) {
      include('inc.bluetooth.php');
   }
}
?>


<div class="panel-group">
  <div class="panel panel-default">
    <div class="panel-heading">
      <h4 class="panel-title"><a name="autoShutdown"></a>
        <i class='mdi mdi-clock-end'></i> <?php print $lang['globalAutoShutdown']." ".$lang['globalSettings']; ?>
      </h4>
    </div><!-- /.panel-heading -->
    <div class="panel-body">

        <div class="row">

<?php
include("inc.setStoptimer.php");
include("inc.setSleeptimer.php");
include("inc.setShutdownVolumeReduction.php");
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
        <i class='mdi mdi-wifi'></i> <?php print $lang['globalWifiSettings']; ?>
      </h4>
    </div><!-- /.panel-heading -->

      <div class="panel-body">
<?php
include("inc.setWifi.php");
?>
      </div><!-- /.panel-body -->

  </div><!-- /.panel -->
</div><!-- /.panel-group -->

<?php
/*
* This is work in progress. 
* If you were to have a local mailserver installed, 
* Phoniebox could send you the IP address over email.
* Useful if you move your Phoniebox into a new Wifi which
* assigns a dynmamic IP.
*/
include("inc.setWlanIpRead.php");
?>

<div class="panel-group">
  <div class="panel panel-default">
    <div class="panel-heading">
      <h4 class="panel-title"><a name="webInterface"></a>
        <i class='mdi mdi-cards-outline'></i> <?php print $lang['settingsWebInterface']; ?>
      </h4>
    </div><!-- /.panel-heading -->

      <div class="panel-body">

<?php
include("inc.setWebUI.php");
?>

      </div><!-- /.panel-body -->
  </div><!-- /.panel -->
</div><!-- /.panel-group -->

<div class="panel-group">
  <div class="panel panel-default">
    <div class="panel-heading">
      <h4 class="panel-title"><a name="externalInterfaces"></a>
        <i class='mdi mdi-usb'></i> <?php print $lang['globalExternalInterfaces']; ?>
      </h4>
    </div><!-- /.panel-heading -->

      <div class="panel-body">
<?php
include("inc.setInputDevices.php");
?>
      </div><!-- /.panel-body -->
  </div><!-- /.panel -->
</div><!-- /.panel-group -->

<div class="panel-group">
  <div class="panel panel-default">
    <div class="panel-heading">
      <h4 class="panel-title"><a name="secondSwipe"></a>
        <i class='mdi mdi-cards-outline'></i> <?php print $lang['settingsSecondSwipe']; ?>
      </h4>
    </div><!-- /.panel-heading -->

      <div class="panel-body">
<?php
include("inc.setSecondSwipe.php");
include("inc.setSecondSwipePause.php");
include("inc.setSecondSwipePauseControls.php");
?>
      </div><!-- /.panel-body -->

  </div><!-- /.panel -->
</div><!-- /.panel-group -->

<?php include("inc.setDebugLogConf.php"); ?>

</div><!-- /.container -->

</body>
<script src="js/jukebox.js">
</script>
</html>
