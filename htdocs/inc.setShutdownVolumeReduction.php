
<!--
Sleep Timer Set Form
-->
        <!-- input-group -->          
        <?php
        /*
        * Values for pulldown form
        */
        $shutdownvolumereductionvals = array(10,15,20,30,45,60,120,180,240);
        /*
        * Get shutdownvolumereduction value
        */
        $shutdownvolumereductionvalue = exec("sudo atq -q q | awk '{print $5}'");
        if ($shutdownvolumereductionvalue != "") {
            $unixtime = time();
            /*
            * For the night owls: if the shutdown time is after midnight (and so on the next day), 
            * $shutdowntime is something like 00:30:00 and time() is e.g. 23:45:00.
            * strtotime($shutdowntime) returns the unix time for today and we get a negative 
            * value in the calculation below.
            * This is fixed by subtracting a day from the current time, as we only need the difference.
            */
            if ($unixtime > strtotime($shutdownvolumereductionvalue)) {
                $unixtime = $unixtime - 86400;
            }
            $remainingshutdownvolumereduction = (strtotime($shutdownvolumereductionvalue)-$unixtime)/60;
            if($remainingshutdownvolumereduction > 60) {
                $remainingshutdownvolumereduction = 60;
            }
            $remainingshutdownvolumereductionselect = round($remainingshutdownvolumereduction);
        }
        else {
            $remainingshutdownvolumereductionselect = 0;
        }
        //$remainingshutdownvolumereductionselect = 10; // debug
        ?>
        <div class="col-md-4 col-sm-6">
            <div class="row" style="margin-bottom:1em;">
              <div class="col-xs-6">
              <h4><?php print $lang['globalShutdownVolumeReduction']; ?></h4>
                <form name='shutdownvolumereduction' method='post' action='<?php print $_SERVER['PHP_SELF']; ?>'>
                  <div class="input-group my-group">
                    <select id="shutdownvolumereduction" name="shutdownvolumereduction" class="selectpicker form-control">
                        <option value='0'><?php print $lang['globalOff']; ?></option>
                    <?php
                    foreach($shutdownvolumereductionvals as $i) {
                        print "
                        <option value='".$i."'";
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
                  <div class="orange c100 p<?php print round($remainingshutdownvolumereductionselect*100/60); ?>">
                    <span><?php 
                        if($remainingshutdownvolumereductionselect == 0) {
                            print $lang['globalOff'];
                        } else {
                            print $remainingshutdownvolumereductionselect."min"; 
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
        <!-- /input-group -->
