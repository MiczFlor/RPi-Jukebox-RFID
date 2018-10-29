<!--
Set Cover
Show covers on main page?
-->
<?php
if(isset($_POST['ShowCover']) && trim($_POST['ShowCover']) != "") {
    /*
    * make sure it is a value we can accept, do not just write whatever is in the POST
    */
    if(trim($_POST['ShowCover']) == "ON") {
        $ShowCover = "ON";
        $exec = 'echo "'.$ShowCover.'" > '.$conf['settings_abs'].'/ShowCover';
        if($debug == "true") {
            print $exec;
        } else {
            exec($exec);
        }
    } elseif(trim($_POST['ShowCover']) == "OFF") {
        $ShowCover = "OFF";
        $exec = 'echo "'.$ShowCover.'" > '.$conf['settings_abs'].'/ShowCover';
        if($debug == "true") {
            print $exec;
        } else {
            exec($exec);
        }
    } 
}
?>

<!-- input-group --> 
	<div class="row" style="margin-bottom:1em;">
	  <div class="col-md-6 col-xs-12">
	  <h4><?php print $lang['settingsCoverInfo']; ?></h4>
		<form name='ShowCover' method='post' action='<?php print $_SERVER['PHP_SELF']; ?>'>
		  <div class="input-group my-group">
			<select id="ShowCover" name="ShowCover" class="selectpicker form-control">
			<?php
				print "
				<option value='ON'";
				if($ShowCover == "ON") {
					print " selected";
				}
				print ">".$lang['settingsShowCoverON'];
				print "</option>\n";
				print "
				<option value='OFF'";
				if($ShowCover == "OFF") {
					print " selected";
				}
				print ">".$lang['settingsShowCoverOFF'];
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
