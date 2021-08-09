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
        }
        exec($exec);
    } elseif(trim($_POST['WlanIpReadYN']) == "OFF") {
        $WlanIpReadYN = "OFF";
        $exec = 'echo "'.$WlanIpReadYN.'" > '.$conf['settings_abs'].'/WlanIpReadYN';
        if($debug == "true") {
            print $exec;
        }
        exec($exec);
    } 
    // execute shell to create config file
    exec("sudo ".$conf['scripts_abs']."/inc.writeGlobalConfig.sh");
}
?>


	<div class="row" style="margin-bottom:1em;">
	  <div class="col-md-6 col-xs-12">
		<form name='WlanIpRead' method='post' action='<?php print $_SERVER['PHP_SELF']; ?>'>
            <h4><?php print $lang['settingsWlanReadInfo']; ?></h4>
              <div class="input-group my-group">        			
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
                </select>
    			<span class="input-group-btn">
    				<input type='submit' class="btn btn-default" name='submit' value='<?php print $lang['globalSet']; ?>'/>
    			</span>
              </div>
            </div>
        

		</form>
	  
	</div><!-- ./row -->
<!-- /input-group -->

      </div><!-- /.panel-body -->
  </div><!-- /.panel -->
</div><!-- /.panel-group -->
