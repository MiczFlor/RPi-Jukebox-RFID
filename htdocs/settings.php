<?php

include("inc.header.php");

/*******************************************
* START HTML
*******************************************/

html_bootstrap3_createHeader("en","Phoniebox",$conf['base_url']);

?>
<body>
  <div class="container">

<?php
include("inc.navigation.php");
?>

<div class="panel-group">
  <div class="panel panel-default">
    <div class="panel-heading">
      <h4 class="panel-title">
         <i class='fa fa-credit-card'></i> Manage Files and Chips
      </h4>
    </div><!-- /.panel-heading -->

      <div class="panel-body">
        <div class="row">
          <div class="col-lg-12">
            <!-- Button trigger modal -->
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
      <h4 class="panel-title">
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
      <h4 class="panel-title">
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
      <h4 class="panel-title">
        <i class='fa fa-keyboard-o'></i> Input Devices Settings
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
