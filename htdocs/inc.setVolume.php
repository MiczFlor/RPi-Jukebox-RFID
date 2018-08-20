<!--
Volume Select Form
-->
        <!-- input-group -->          
        <?php
        $volumevalue = exec("/usr/bin/sudo ".$conf['scripts_abs']."/playout_controls.sh -c=getvolume");
        //$volumevalue = 73.6;//debug
        $volumevalueselect = round(($volumevalue/10))*10;
        $volumevaluedisplay = round($volumevalue);
		
        $maxvolumevalue = exec("/usr/bin/sudo ".$conf['scripts_abs']."/playout_controls.sh -c=getmaxvolume");
        $maxvalueselect = round(($maxvolumevalue/10))*10;
        $maxvaluedisplay = round($maxvolumevalue);
        ?>
        <div class="col-md-4 col-sm-6">
            <div class="row" style="margin-bottom:1em;">
              <div class="col-xs-6">
              <h4><?php print $lang['globalVolume']; ?></h4>
                <form name='volume' method='post' action='<?php print $_SERVER['PHP_SELF']; ?>'>
                  <div class="input-group my-group">
                    <select id="volume" name="volume" class="selectpicker form-control">
                    <?php
                    $i = 100;
                    while ($i >= 0) {
                        print "
                        <option value='".$i."'";
                        if($volumevalueselect == $i) {
                            print " selected";
                        }
			if($i > $maxvalueselect ) {
                            print " disabled";
                        }
			print ">".$i."%";
			if($i == $maxvalueselect ) {
                            print " limit";
                        }
                        print "</option>";
                        $i = $i - 10;  
                    };
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
                  <div class="c100 p<?php print $volumevaluedisplay; ?>">
                    <span><?php print $volumevaluedisplay; ?>%</span>
                    <div class="slice">
                        <div class="bar"></div>
                        <div class="fill"></div>
                    </div>
                  </div> 
              </div>
            </div><!-- ./row -->
        </div>
        <!-- /input-group -->
