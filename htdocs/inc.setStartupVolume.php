<!--
Startup Volume Select Form
-->
        <!-- input-group -->
        <?php
        //$maxvolumevalue = exec("/usr/bin/sudo ".$conf['scripts_abs']."/playout_controls.sh -c=getmaxvolume");
        //$maxvolumevalue = 43.6;//debug
        $maxvalueselect = round(($maxvolumevalue/5))*5;
        $startupvaluedisplay = round($startupvolumevalue);
        ?>
        <div class="col-md-4 col-sm-6">
            <div class="row" style="margin-bottom:1em;">
              <div class="col-xs-6">
              <h4><?php print $lang['settingsStartupVol']; ?></h4>
                <form name='startupvolume' method='post' action='<?php print $_SERVER['PHP_SELF']; ?>'>
                  <div class="input-group my-group">
                    <select id="startupvolume" name="startupvolume" class="selectpicker form-control">
                      <option value='0'<?php
                          if($startupvolumevalue == 0) {
                              print " selected";
                          }
                      ?>><?php print $lang['globalOff']; ?></option>
                    <?php
                    $i = $maxvalueselect;
                    while ($i >= 5) {
                        print "
                        <option value='".$i."'";
                        if($startupvaluedisplay == $i) {
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
                  <div class="c100 p<?php print $startupvaluedisplay; ?>">
                    <span><?php
                        if ($startupvolumevalue == 0) {
                            print $lang['globalOff'];
                        } else {
                            print $startupvolumevalue."%";
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
