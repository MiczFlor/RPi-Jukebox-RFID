
<!--
Sleep Timer Set Form
-->
        <!-- input-group -->          
        <?php
        /*
        * Values for pulldown form
        */
        $shut_reduce_volume_vals = array(2,5,10,15,20,30,45,60,120,180,240);
        /*
        * Get shut_reduce_volume_ value
        */
        $shut_reduce_volume_value = exec("sudo atq -q t | awk '{print $5}'");
        if ($shut_reduce_volume_value != "") {
            $unixtime = time();
            /*
            * For the night owls: if the shutdown time is after midnight (and so on the next day), 
            * $shutdowntime is something like 00:30:00 and time() is e.g. 23:45:00.
            * strtotime($shutdowntime) returns the unix time for today and we get a negative 
            * value in the calculation below.
            * This is fixed by subtracting a day from the current time, as we only need the difference.
            */
            if ($unixtime > strtotime($shut_reduce_volume_value)) {
                $unixtime = $unixtime - 86400;
            }
            $remainingshut_reduce_volume_ = (strtotime($shut_reduce_volume_value)-$unixtime)/60;
            if($remainingshut_reduce_volume_ > 60) {
                $remainingshut_reduce_volume_ = 60;
            }
            $remainingshut_reduce_volume_select = round($remainingshut_reduce_volume_);
        }
        else {
            $remainingshut_reduce_volume_select = 0;
        }
        //$remainingshut_reduce_volume_select = 10; // debug
        ?>
        <div class="col-md-4 col-sm-6">
            <div class="row" style="margin-bottom:1em;">
              <div class="col-xs-6">
              <h4><?php print $lang['globalShutReduceVolume']; ?></h4>
                <form name='shutdownwithreducingvolume' method='post' action='<?php print $_SERVER['PHP_SELF']; ?>'>
                  <div class="input-group my-group">
                    <select id="shutdownwithreducingvolume" name="shutdownwithreducingvolume" class="selectpicker form-control">
                        <option value='0'><?php print $lang['globalOff']; ?></option>
                    <?php
                    foreach($shut_reduce_volume_vals as $i) {
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
                  <div class="orange c100 p<?php print round($remainingshut_reduce_volume_select*100/60); ?>">
                    <span><?php 
                        if($remainingshut_reduce_volume_select == 0) {
                            print $lang['globalOff'];
                        } else {
                            print $remainingshut_reduce_volume_select."min"; 
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
