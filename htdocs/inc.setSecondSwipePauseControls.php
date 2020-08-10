<!--
Set Second Swipe Pause Controls
Some Controls cards are useful without an delay
-->
<?php
if(isset($_POST['secondSwipePauseControls']) && trim($_POST['secondSwipePauseControls']) != "") {
    /*
    * make sure it is a value we can accept, do not just write whatever is in the POST
    */
    if(trim($_POST['secondSwipePauseControls']) == "ON") {
        $Second_Swipe_Pause_Controls = "ON";
        $exec = 'echo "'.$Second_Swipe_Pause_Controls.'" > '.$conf['settings_abs'].'/Second_Swipe_Pause_Controls';
        if($debug == "true") {
            print $exec;
        } 
        exec($exec);
    } elseif(trim($_POST['secondSwipePauseControls']) == "OFF") {
        $Second_Swipe_Pause_Controls = "OFF";
        $exec = 'echo "'.$Second_Swipe_Pause_Controls.'" > '.$conf['settings_abs'].'/Second_Swipe_Pause_Controls';
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
              <h4><?php print $lang['settingsSecondSwipePauseControlsInfo']; ?></h4>
                <form name='secondSwipe' method='post' action='<?php print $_SERVER['PHP_SELF']; ?>'>
                  <div class="input-group my-group">
                    <select id="secondSwipePauseControls" name="secondSwipePauseControls" class="selectpicker form-control">
                    <?php
                        print "
                        <option value='ON'";
                        if($Second_Swipe_Pause_Controls == "ON") {
                            print " selected";
                        }
                        print ">".$lang['settingsSecondSwipePauseControlsOn'];
                        print "</option>\n";
                        print "
                        <option value='OFF'";
                        if($Second_Swipe_Pause_Controls == "OFF") {
                            print " selected";
                        }
                        print ">".$lang['settingsSecondSwipePauseControlsOff'];
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
