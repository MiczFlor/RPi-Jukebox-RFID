<!--
Maximum Volume Select Form
-->
        <!-- input-group -->          
        <?php
        $maxvolumevalue = exec("/usr/bin/sudo ".$conf['scripts_abs']."/playout_controls.sh -c=getmaxvolume");
        //$maxvolumevalue = 43.6;//debug
        $maxvalueselect = round(($maxvolumevalue/5))*5;
        $maxvaluedisplay = round($maxvolumevalue);
        ?>
        <div class="col-md-4 col-sm-6">
            <div class="row" style="margin-bottom:1em;">
              <div class="col-xs-6">
              <h4><?php print $lang['settingsMaxVol']; ?></h4>
                <form name='maxvolume' method='post' action='<?php print $_SERVER['PHP_SELF']; ?>'>
                  <div class="input-group my-group">
                    <select id="maxvolume" name="maxvolume" class="selectpicker form-control">
                    <?php
                    $i = 100;
                    while ($i >= 5) {
                        print "
                        <option value='".$i."'";
                        if($maxvalueselect == $i) {
                            print " selected";
                        }
                        print ">".$i."%</option>";
                        $i = $i - 5;  
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
                  <div class="c100 p<?php print $maxvaluedisplay; ?>">
                    <span><?php print $maxvaluedisplay; ?>%</span>
                    <div class="slice">
                        <div class="bar"></div>
                        <div class="fill"></div>
                    </div>
                  </div> 
              </div>
            </div><!-- ./row -->
        </div>
        <!-- /input-group -->
