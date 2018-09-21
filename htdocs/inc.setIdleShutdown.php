

<!--
Idle Shutdown Set Form
-->
        <!-- input-group -->          
        <?php
        /*
        * Values for pulldown form
        */
        $idletimervals = array(10,15,20,30,45,60);
        /*
        * Get idle time value
        */
        $idletimevalue = exec("/usr/bin/sudo ".$conf['scripts_abs']."/playout_controls.sh -c=getidletime");
        //$idletimevalue = 20;// debug
        /*
        * Now get the remaining time
        */
        if ($idletimevalue != "0") {
            $shutdowntime = exec("sudo atq -q i | awk '{print $5}'");
            $unixtime = time();
            /*
            * For the night owls: if the shutdown time is after midnight (and so on the next day), 
            * $shutdowntime is something like 00:30:00 and time() is e.g. 23:45:00.
            * strtotime($shutdowntime) returns the unix time for today and we get a negative 
            * value in the calculation below.
            * This is fixed by subtracting a day from the current time, as we only need the difference.
            */
            if ($unixtime > strtotime($shutdowntime)) {
                $unixtime = $unixtime - 86400;
            }
            $remainingtime = (strtotime($shutdowntime)-$unixtime)/60;
            $remainingtimedisplay = round($remainingtime);
            if($remainingtimedisplay > 60) {
                $remainingtimedisplay = 60;
            }
        }
        //$shutdowntime = 1;// debug
        //$remainingtimedisplay = 20;// debug
        ?>
        <div class="col-md-4 col-sm-6">
            <div class="row" style="margin-bottom:1em;">
              <div class="col-xs-6">
              <h4><?php print $lang['globalIdleShutdown']; ?></h4>
                <form name='idletime' method='post' action='<?php print $_SERVER['PHP_SELF']; ?>'>
                  <div class="input-group my-group">
                    <select id="idletime" name="idletime" class="selectpicker form-control">
                        <option value='0'<?php
                            if($idletimevalue == 0) {
                                print " selected";
                            }
                        ?>><?php print $lang['globalOff']; ?></option>
                    <?php
                    foreach($idletimervals as $i) {
                        print "
                        <option value='".$i."'";
                        if($idletimevalue == $i) {
                            print " selected";
                        }
                        print ">".$i."min</option>";
                    }
                    print "\n";
                    ?>
                    </select> 
                    <span class="input-group-btn">
                        <input type='submit' class="btn btn-default" name='submit' value='<?php print $lang['globalSet']; ?>'/>
                    </span>
                  </div>
                </form>
              </div>
              
              <div class="col-xs-6">
                  <div class="c100 p<?php print round($idletimevalue*100/60); ?>">
                    <span><?php 
                        if ($idletimevalue == 0) {
                            print $lang['globalOff'];
                        } else {
                            print $idletimevalue."min"; 
                        }
                    ?></span>
                    <div class="slice">
                        <div class="bar"></div>
                        <div class="fill"></div>
                    </div>
                  </div> 
              </div>
            </div><!-- ./row -->
        </div>
<?php
/*
* The following is showing the idle time
* Don't show it, if the idle swith off is OFF
*/
if ($idletimevalue != 0) {
?>
        <div class="col-md-4 col-sm-6">
            <div class="row" style="margin-bottom:1em;">
              <div class="col-xs-6">
              <h4><?php print $lang['globalIdleTime']; ?></h4>
              </div>
              
              <div class="col-xs-6">
                  <div class="orange c100 p<?php print round($remainingtimedisplay*100/60); ?>">
                    <span><?php 
                        if ($shutdowntime != "") {
                            print $remainingtimedisplay.'min';
                        }
                        else {
                            print $lang['globalNotIdle'];
                        }
                    ?></span>
                    <div class="slice">
                        <div class="bar"></div>
                        <div class="fill"></div>
                    </div>
                  </div> 
              </div>
            </div><!-- ./row -->
        </div>
<?php
}
?>
        <!-- /input-group -->
