<!--
Boot Volume => the volume that will be set when the Phoniebox is booted
-->
        <!-- input-group -->
        <?php
        $maxvalueselect = round(($maxvolumevalue/5))*5;
        $bootvolvaluedisplay = round($bootvolumevalue);
        ?>
        <div class="col-md-4 col-sm-6">
            <div class="row" style="margin-bottom:1em;">
              <div class="col-xs-6">
              <h4><?php print $lang['settingsBootVol']; ?></h4>
                <form name='bootvolume' method='post' action='<?php print $_SERVER['PHP_SELF']; ?>'>
                  <div class="input-group my-group">
                    <select id="bootvolume" name="bootvolume" class="selectpicker form-control">
                      <option value='0'<?php
                          if($bootvolumevalue == 0) {
                              print " selected";
                          }
                      ?>><?php print $lang['globalOff']; ?></option>
                    <?php
                    $i = $maxvalueselect;
                    while ($i >= 5) {
                        print "
                        <option value='".$i."'";
                        if($bootvolvaluedisplay == $i) {
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
                  <div class="c100 p<?php print $bootvolvaluedisplay; ?>">
                    <span><?php
                        if ($bootvolumevalue == 0) {
                            print $lang['globalOff'];
                        } else {
                            print $bootvolumevalue."%";
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
