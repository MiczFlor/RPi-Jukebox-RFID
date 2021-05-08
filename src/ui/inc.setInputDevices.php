<ul class="list-group">
  <li class="list-group-item">
	<div class="row">
		<div class="col-xs-6">
<?php
$gpiostatus = exec("/bin/systemctl status phoniebox-gpio-control.service | grep running");
if ($gpiostatus != "") {
	print $lang['globalGpioButtons'].' <span class="label label-success">'.$lang['globalEnabled'].'</span>';
	print '</div><!-- / .col-xs-6 -->';
	print '<div class="col-xs-6">';
	print "<a href='?gpiostatus=turnoff' class='btn btn-sm btn-danger'><i class='mdi mdi-cancel'></i> ".$lang['globalSwitchOff']."</a>";
}
else {
	print $lang['globalGpioButtons'].' <span class="label label-danger">'.$lang['globalDisabled'].'</span>';
	print '</div><!-- / .col-xs-4 -->';
	print '<div class="col-xs-4">';
	print "<a href='?gpiostatus=turnon' class='btn btn-sm btn-success'><i class='mdi mdi-play'></i> ".$lang['globalSwitchOn']."</a>";
}
?>
		</div><!-- / .col-xs-6 -->
	</div><!-- / .row -->
  </li>

  <li class="list-group-item">
	<div class="row">
		<div class="col-xs-6">
<?php
$rfidstatus = exec("/bin/systemctl status phoniebox-rfid-reader.service | grep running");
if ($rfidstatus != "") {
	print $lang['globalRfidReader'].' <span class="label label-success">'.$lang['globalEnabled'].'</span>';
	print '</div><!-- / .col-xs-6 -->';
	print '<div class="col-xs-6">';
	print "<a href='?rfidstatus=turnoff' class='btn btn-sm btn-danger'><i class='mdi mdi-cancel'></i> ".$lang['globalSwitchOff']."</a>";
}
else {
	print $lang['globalRfidReader'].' <span class="label label-danger">'.$lang['globalDisabled'].'</span>';
	print '</div><!-- / .col-xs-4 -->';
	print '<div class="col-xs-4">';
	print "<a href='?rfidstatus=turnon' class='btn btn-sm btn-success'><i class='mdi mdi-play'></i> ".$lang['globalSwitchOn']."</a>";
}
?>
		</div><!-- / .col-xs-6 -->
	</div><!-- / .row -->
  </li>
<!--
Set Volume manager (mpd or amixer)
-->
<?php
if(isset($_POST['VolumeManager']) && trim($_POST['VolumeManager']) != "") {
    /*
    * make sure it is a value we can accept, do not just write whatever is in the POST
    */
    if(trim($_POST['VolumeManager']) == "mpd") {
        $VolumeManager = "mpd";
        $exec = 'echo "'.$VolumeManager.'" > '.$conf['settings_abs'].'/Volume_Manager';
        if($debug == "true") {
            print $exec;
        }
        exec($exec);
    } elseif(trim($_POST['VolumeManager']) == "amixer") {
        $VolumeManager = "amixer";
        $exec = 'echo "'.$VolumeManager.'" > '.$conf['settings_abs'].'/Volume_Manager';
        if($debug == "true") {
            print $exec;
        }
        exec($exec);
    } 
    // execute shell to create config file
    exec("sudo ".$conf['scripts_abs']."/inc.writeGlobalConfig.sh");
}
?>

<!-- input-group --> 
	<div class="row" style="margin-bottom:1em;">
	  <div class="col-md-6 col-xs-12">
	  <h4><?php print $lang['settingsVolumeManager']; ?></h4>
		<form name='VolumeManager' method='post' action='<?php print $_SERVER['PHP_SELF']; ?>'>
		  <div class="input-group my-group">
			<select id="VolumeManager" name="VolumeManager" class="selectpicker form-control">
			<?php
				print "
				<option value='mpd'";
				if($VolumeManager == "mpd") {
					print " selected";
				}
				print ">mpd";
				print "</option>\n";
				print "
				<option value='amixer'";
				if($VolumeManager == "amixer") {
					print " selected";
				}
				print ">amixer";
				print "</option>\n";
			?>
			</select> 
			<span class="input-group-btn">
				<input type='submit' class="btn btn-default" name='submit' value='<?php print $lang['globalSet']; ?>'/>
			</span>
		  </div>
		</form>
	  </div>
	  
	</div><!-- ./row -->
<!-- /input-group -->
</ul>
