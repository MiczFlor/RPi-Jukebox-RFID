<!--
Send Wifi IP over Mail?
-->

<div class="panel-group">
  <div class="panel panel-default">
    <div class="panel-heading">
      <h4 class="panel-title"><a name="wlanIpEmail"></a>
        <i class='mdi mdi-wifi'></i> <?php print $lang['settingsWlanSendNav']; ?>
      </h4>
    </div>

      <div class="panel-body">

<?php
if(isset($_POST['WlanIpMailYN']) && trim($_POST['WlanIpMailYN']) != "") {
    /*
    * make sure it is a value we can accept, do not just write whatever is in the POST
    */
    if(trim($_POST['WlanIpMailYN']) == "ON") {
        $WlanIpMailYN = "ON";
        $exec = 'echo "'.$WlanIpMailYN.'" > '.$conf['settings_abs'].'/WlanIpMailYN';
        if($debug == "true") {
            print $exec;
        }
        exec($exec);
    } elseif(trim($_POST['WlanIpMailYN']) == "OFF") {
        $WlanIpMailYN = "OFF";
        $exec = 'echo "'.$WlanIpMailYN.'" > '.$conf['settings_abs'].'/WlanIpMailYN';
        if($debug == "true") {
            print $exec;
        }
        exec($exec);
    } 
    // Email address
    $WlanIpMailAddr = trim($_POST['WlanIpMailAddr']);
    if (filter_var($WlanIpMailAddr, FILTER_VALIDATE_EMAIL)) {
        $WlanIpMailAddr = htmlspecialchars($WlanIpMailAddr, ENT_QUOTES, 'UTF-8');
        $exec = 'echo "'.$WlanIpMailAddr.'" > '.$conf['settings_abs'].'/WlanIpMailAddr';
        if($debug == "true") {
            print $exec;
        }
        shell_exec($exec); // P36bd
    } else {
        echo "Invalid email address.";
    }
    // execute shell to create config file
    shell_exec("sudo ".$conf['scripts_abs']."/inc.writeGlobalConfig.sh"); // P36bd
}
?>


      <div class="panel-body">

		<form name='WlanIpMailYN' method='post' action='<?php print $_SERVER['PHP_SELF']; ?>'>
		
        <fieldset>
        
            <!-- Form Name -->
            <legend><?php print $lang['settingsWlanSendInfo']; ?></legend>
            
            <!-- Select Basic -->
            <div class="form-group">
              <label class="col-md-4 control-label" for="selectbasic"><?php print $lang['settingsWlanSendQuest']; ?></label>
              <div class="col-md-6">        			
                <select id="WlanIpMailYN" name="WlanIpMailYN" class="selectpicker form-control">
            		<?php
            			print "
            			<option value='ON'";
            			if($WlanIpMailYN == "ON") {
            				print " selected";
            			}
            			print ">".$lang['settingsWlanSendON'];
            			print "</option>\n";
            			print "
            			<option value='OFF'";
            			if($WlanIpMailYN == "OFF") {
            				print " selected";
            			}
            			print ">".$lang['settingsWlanSendOFF'];
            			print "</option>\n";
            		?>
                </select><br/>
              </div>
            </div>
            
            <!-- Text input-->
            <div class="form-group">
              <label class="col-md-4 control-label" for="textinput"><?php print $lang['globalEmail']; ?></label>  
              <div class="col-md-6">
              <input id="WlanIpMailAddr" name="WlanIpMailAddr" type="text" placeholder="Email address" class="form-control input-md" value="<?php
              if($WlanIpMailAddr != "") {
                  print $WlanIpMailAddr;
              }
              ?>">
              <!--span class="help-block">help</span-->  
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
