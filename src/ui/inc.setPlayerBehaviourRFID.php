
<?php
/*
* GLOBAL settings for behaviour of placing or swiping RFID cards to
* control player play and stop
* SWIPENOTPLACE = Swiping starts the player
* PLACENOTSWIPE = Placing the card starts player, removal stops it
*/

if(isset($_POST['rfidSwipePlace']) && trim($_POST['rfidSwipePlace']) != "") {
    /*
    * make sure it is a value we can accept, do not just write whatever is in the POST
    */
    if(trim($_POST['rfidSwipePlace']) == "SWIPENOTPLACE") {
        $Swipe_or_Place = "SWIPENOTPLACE";
        $exec = 'echo "'.$Swipe_or_Place.'" > '.$conf['settings_abs'].'/Swipe_or_Place';
        if($debug == "true") {
            print $exec; print "<br>Swipe_or_Place: ".$Swipe_or_Place;
        }
        exec($exec);
    } elseif(trim($_POST['rfidSwipePlace']) == "PLACENOTSWIPE") {
        $Swipe_or_Place = "PLACENOTSWIPE";
        $exec = 'echo "'.$Swipe_or_Place.'" > '.$conf['settings_abs'].'/Swipe_or_Place';
        if($debug == "true") {
            print $exec; print "<br>Swipe_or_Place: ".$Swipe_or_Place;
        }
        exec($exec);
    } 
    // execute shell to create config file
    $exec = "sudo ".$conf['scripts_abs']."/inc.writeGlobalConfig.sh";   
    // execute shell to restart RFID Reader Service
    $exec = "sudo systemctl restart phoniebox-rfid-reader.service";
    if($debug == "true") {
        print $exec;
    }
    exec($exec);
} else {
    if($debug == "true") {
        print "<br>Swipe_or_Place: ".$Swipe_or_Place;
    }
}
?>

        <!-- input-group --> 
        <div class="col-md-6 col-sm-6">
              <h4><?php print $lang['settingsPlayoutBehaviourCardLabel']; ?></h4>
             
                <form name='swipeplace' method='post' action='<?php print $_SERVER['PHP_SELF']; ?>'>
                  <div class="input-group my-group">
                    <select id="rfidSwipePlace" name="rfidSwipePlace" class="form-control">
<?php
                        print "
                        <option value='SWIPENOTPLACE'";
                        if($Swipe_or_Place == "SWIPENOTPLACE") {
                            print " selected";
                        }
                        print ">".$lang['settingsPlayoutBehaviourCardSwipe'];
                        print "</option>\n";
                        print "
                        <option value='PLACENOTSWIPE'";
                        if($Swipe_or_Place == "PLACENOTSWIPE") {
                            print " selected";
                        }
                        print ">".$lang['settingsPlayoutBehaviourCardPlace'];
                        print "</option>\n";
?>
                    </select> 
                    <span class="input-group-btn">
                        <input type='submit' class="btn btn-default" name='submit' value='<?php print $lang['globalSet']; ?>'/>
                    </span>
                  </div>
                </form>              
            <span class="help-block"><?php print $lang['settingsPlayoutBehaviourCardHelp']; ?></span>
        </div>
        <!-- /input-group -->
