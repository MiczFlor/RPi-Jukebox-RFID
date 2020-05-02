<!--
Send Wifi IP over Mail?
-->

<div class="panel-group">
  <div class="panel panel-default">
    <div class="panel-heading">
      <h4 class="panel-title"><a name="wlanIpRead"></a>
        <i class='mdi mdi-wifi'></i> <?php print $lang['settingsWlanReadNav']; ?>
      </h4>
    </div>

      <div class="panel-body">

<?php
if(isset($_POST['WlanIpReadYN']) && trim($_POST['WlanIpReadYN']) != "") {
    /*
    * make sure it is a value we can accept, do not just write whatever is in the POST
    */
    if(trim($_POST['WlanIpReadYN']) == "ON") {
        $WlanIpReadYN = "ON";
        $exec = 'echo "'.$WlanIpReadYN.'" > '.$conf['settings_abs'].'/WlanIpReadYN';
        if($debug == "true") {
            print $exec;
        } else {
            exec($exec);
        }
    } elseif(trim($_POST['WlanIpReadYN']) == "OFF") {
        $WlanIpReadYN = "OFF";
        $exec = 'echo "'.$WlanIpReadYN.'" > '.$conf['settings_abs'].'/WlanIpReadYN';
        if($debug == "true") {
            print $exec;
        } else {
            exec($exec);
        }
    } 
    // execute shell to create config file
    exec("sudo ".$conf['scripts_abs']."/inc.writeGlobalConfig.sh");
}
?>


      <div class="panel-body">

		<form name='WlanIpRead' method='post' action='<?php print $_SERVER['PHP_SELF']; ?>'>
		
        <fieldset>
        
            <!-- Form Name -->
            <legend><?php print $lang['settingsWlanReadInfo']; ?></legend>
            
            <!-- Select Basic -->
            <div class="form-group">
              <label class="col-md-4 control-label" for="selectbasic"><?php print $lang['settingsWlanReadQuest']; ?></label>
              <div class="col-md-6">        			
                <select id="WlanIpReadYN" name="WlanIpReadYN" class="selectpicker form-control">
            		<?php
            			print "
            			<option value='ON'";
            			if($WlanIpReadYN == "ON") {
            				print " selected";
            			}
            			print ">".$lang['settingsWlanReadON'];
            			print "</option>\n";
            			print "
            			<option value='OFF'";
            			if($WlanIpReadYN == "OFF") {
            				print " selected";
            			}
            			print ">".$lang['settingsWlanReadOFF'];
            			print "</option>\n";
            		?>
                </select><br/>
              </div>
            </div>
        
        </fieldset>		
		
    <!-- Button (Double) -->
    <div class="form-group">
        <label class="col-md-4 control-label" for="submit"></label>
        <div class="col-md-8">
            <br/>
            <button id="submit" name="sumbit" class="btn btn-success" value="submit">Submit</button>
            <br clear="all"><br>
        </div>
    </div>

		</form>
	  
	</div><!-- ./row -->
<!-- /input-group -->

      </div><!-- /.panel-body -->
  </div><!-- /.panel -->
</div><!-- /.panel-group -->
