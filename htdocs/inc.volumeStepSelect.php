<!--
Volume Up/Down Percent Form
-->
        <!-- input-group -->          
        <?php
        $volstepvalue = exec("/usr/bin/sudo ".$conf['scripts_abs']."/playout_controls.sh -c=getvolstep");
        //$volstepvalue = 3.6;//debug
        $volstepvalueselect = round($volstepvalue);
        $volstepvaluedisplay = round($volstepvalue);
        ?>
        <div class="col-md-4 col-sm-6">
            <div class="row" style="margin-bottom:1em;">
              <div class="col-xs-6">
              <h4><?php print $lang['settingsVolChangePercent']; ?></h4>
                <form name='volstep' method='post' action='<?php print $_SERVER['PHP_SELF']; ?>'>
                  <div class="input-group my-group">
                    <select id="volstep" name="volstep" class="selectpicker form-control">
                    <?php
                    $i = 1;
                    while ($i <= 15) {
                        print "
                        <option value='".$i."'";
                        if($volstepvalueselect == $i) {
                            print " selected";
                        }
                        print ">".$i."%</option>";
                        $i++;  
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
                  <div class="c100 p<?php print $volstepvaluedisplay; ?>">
                    <span><?php print $volstepvaluedisplay; ?>%</span>
                    <div class="slice">
                        <div class="bar"></div>
                        <div class="fill"></div>
                    </div>
                  </div> 
              </div>
            </div><!-- ./row -->
        </div>
        <!-- /input-group -->
