<!--
Set Second Swipe
When you swipe the same RFID a second time, what happens? Start the playlist again? Toggle pause/play?
-->
<?php
if(isset($_POST['secondSwipe']) && trim($_POST['secondSwipe']) != "") {
    /*
    * make sure it is a value we can accept, do not just write whatever is in the POST
    */
    if(trim($_POST['secondSwipe']) == "RESTART") {
        $Second_Swipe = "RESTART";
        $exec = 'echo "'.$Second_Swipe.'" > '.$conf['settings_abs'].'/Second_Swipe';
        if($debug == "true") {
            print $exec;
        } else {
            exec($exec);
        }
    } elseif(trim($_POST['secondSwipe']) == "PAUSE") {
        $Second_Swipe = "PAUSE";
        $exec = 'echo "'.$Second_Swipe.'" > '.$conf['settings_abs'].'/Second_Swipe';
        if($debug == "true") {
            print $exec;
        } else {
            exec($exec);
        }
    } elseif(trim($_POST['secondSwipe']) == "SKIPNEXT") {
        $Second_Swipe = "SKIPNEXT";
        $exec = 'echo "'.$Second_Swipe.'" > '.$conf['settings_abs'].'/Second_Swipe';
        if($debug == "true") {
            print $exec;
        } else {
            exec($exec);
        }
    } elseif(trim($_POST['secondSwipe']) == "NOAUDIOPLAY") {
        $Second_Swipe = "NOAUDIOPLAY";
        $exec = 'echo "'.$Second_Swipe.'" > '.$conf['settings_abs'].'/Second_Swipe';
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
              <h4><?php print $lang['settingsSecondSwipeInfo']; ?></h4>
                <form name='secondSwipe' method='post' action='<?php print $_SERVER['PHP_SELF']; ?>'>
                  <div class="input-group my-group">
                    <select id="secondSwipe" name="secondSwipe" class="selectpicker form-control">
                    <?php
                        print "
                        <option value='RESTART'";
                        if($Second_Swipe == "RESTART") {
                            print " selected";
                        }
                        print ">".$lang['settingsSecondSwipeRestart'];
                        print "</option>\n";
                        print "
                        <option value='PAUSE'";
                        if($Second_Swipe == "PAUSE") {
                            print " selected";
                        }
                        print ">".$lang['settingsSecondSwipePause'];
                        print "</option>\n";
                        print "
                        <option value='SKIPNEXT'";
                        if($Second_Swipe == "SKIPNEXT") {
                            print " selected";
                        }
                        print ">".$lang['settingsSecondSwipeSkipnext'];
                        print "</option>\n";
                        print "
                        <option value='NOAUDIOPLAY'";
                        if($Second_Swipe == "NOAUDIOPLAY") {
                            print " selected";
                        }
                        print ">".$lang['settingsSecondSwipeNoAudioPlay'];
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
