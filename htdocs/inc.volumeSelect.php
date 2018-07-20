<!--
Volume Select Form
-->
        <!-- input-group -->          
        <?php
        $volumevalue = exec("/usr/bin/sudo ".$conf['scripts_abs']."/playout_controls.sh -c=getvolume");
        //$volumevalue = 73.6;//debug
        $volumevalueselect = round(($volumevalue/10))*10;
        $volumevaluedisplay = round($volumevalue);
        ?>
        <div class="col-md-4 col-sm-6">
            <div class="row" style="margin-bottom:1em;">
              <div class="col-xs-6">
              <h4>Volume</h4>
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
                        print ">".$i."%</option>";
                        $i = $i - 10;  
                    };
                    print "\n";
                    ?>
                    </select> 
                    <span class="input-group-btn">
                        <input type='submit' class="btn btn-default" name='submit' value='Set'/>
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
