<nav class="navbar navbar-default" style="position: -webkit-sticky; position: sticky; top: 0; z-index: 1000;">
  <div class="container-fluid">
    <!-- Brand and toggle get grouped for better mobile display -->
    <div class="navbar-header">
      <button type="button" class="navbar-toggle collapsed" data-toggle="collapse" data-target="#bs-example-navbar-collapse-1" aria-expanded="false">
        <span class="sr-only">Toggle navigation</span>
        <span class="icon-bar"></span>
        <span class="icon-bar"></span>
        <span class="icon-bar"></span>
      </button>
      <a class="navbar-brand" style="padding: 19.5px 15px 0px; height: 0px;" href="index.php"><?php print $lang['navBrand']; ?></a><br>
	  <div class="navbar-brand" style="padding: 0px 15px 0px; margin-top: 19.5px; height: 0px; font-size: 13px; color: white;"><?php 
	  if ($edition == "classic") { 
		print $lang['navEditionClassic']; 
	  } elseif ($edition == "plusSpotify") { 
		print $lang['navEditionPlusSpotify'];
	  }
	  ?></div>
    </div>

    <!-- Collect the nav links, forms, and other content for toggling -->
    <div class="collapse navbar-collapse" id="bs-example-navbar-collapse-1">
      <ul class="nav navbar-nav">
        <li><a href='index.php' class='mainMenu'><i class='mdi mdi-home'></i> <?php print $lang['navHome']; ?></a></li>
	      <li><a href='settings.php' class='mainMenu'><i class='mdi mdi-settings'></i> <?php print $lang['navSettings']; ?></a></li>
        <li><a href='systemInfo.php' class='mainMenu'><i class='mdi mdi-information-outline'></i> <?php print $lang['navInfo']; ?></a></li>
        <li><a href='manageFilesFolders.php' class='mainMenu'><i class='mdi mdi-folder-upload'></i> <?php print $lang['manageFilesFoldersTitle']; ?></a></li>
		<li><a href="cardRegisterNew.php" class="mainMenu"><i class='mdi mdi-cards-outline'></i> <?php print $lang['globalRegisterCardShort']; ?></a></li>
		<?php
		if ($edition == "plusSpotify") {
		print "<li><a href='http://".$conf['local_url'].":6680/iris' class='mainMenu' target='_blank'><i class='mdi mdi-spotify'></i>".$lang['Spotify']."</a></li>";
		}
		?>
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
