<?php
/*
* load language strings
*/
include("inc.langLoad.php");
?>

<nav class="navbar navbar-default">
  <div class="container-fluid">
    <!-- Brand and toggle get grouped for better mobile display -->
    <div class="navbar-header">
      <button type="button" class="navbar-toggle collapsed" data-toggle="collapse" data-target="#bs-example-navbar-collapse-1" aria-expanded="false">
        <span class="sr-only">Toggle navigation</span>
        <span class="icon-bar"></span>
        <span class="icon-bar"></span>
        <span class="icon-bar"></span>
      </button>
      <a class="navbar-brand" href="index.php"><?php print $lang['navBrand']; ?></a>
    </div>

    <!-- Collect the nav links, forms, and other content for toggling -->
    <div class="collapse navbar-collapse" id="bs-example-navbar-collapse-1">
      <ul class="nav navbar-nav">
        <li><a href='index.php' class='mainMenu'><i class='mdi mdi-home'></i> <?php print $lang['navHome']; ?></a></li>
	      <li><a href='settings.php' class='mainMenu'><i class='mdi mdi-settings'></i> <?php print $lang['navSettings']; ?></a></li>
        <li><a href='systemInfo.php' class='mainMenu'><i class='mdi mdi-information-outline'></i> <?php print $lang['navInfo']; ?></a></li>
        <li><a href='fileUpload.php' class='mainMenu'><i class='mdi mdi-upload-multiple'></i> <?php print $lang['fileUploadTitle']; ?></a></li>
      </ul>
      
<!-- sub menu -->
      <ul class="nav navbar-nav navbar-right">
        <li><a href='index.php?shutdown=true' class='mainMenu'><i class='mdi mdi-power'></i> <?php print $lang['navShutdown']; ?></a></li>
        <li><a href='index.php?reboot=true' class='mainMenu'><i class='mdi mdi-refresh'></i> <?php print $lang['navReboot']; ?></a></li>
      </ul>
<!-- / sub menu -->
    </div><!-- /.navbar-collapse -->
  </div><!-- /.container-fluid -->
</nav>
