<!--
Set Second Swipe Pause
What if the cards is swiped again too fast? Here you can set a pause time.
-->
<?php
if(isset($_POST['secondSwipePause']) && trim($_POST['secondSwipePause']) != "") {
    /*
    * make sure it is a value we can accept, do not just write whatever is in the POST
    */
    if(trim($_POST['secondSwipePause']) == "0") {
        $Second_Swipe_Pause = "0";
        $exec = 'echo "'.$Second_Swipe_Pause.'" > '.$conf['settings_abs'].'/Second_Swipe_Pause';
        if($debug == "true") {
            print $exec;
        } 
        exec($exec);
    } elseif(trim($_POST['secondSwipePause']) == "1") {
        $Second_Swipe_Pause = "1";
        $exec = 'echo "'.$Second_Swipe_Pause.'" > '.$conf['settings_abs'].'/Second_Swipe_Pause';
        if($debug == "true") {
            print $exec;
        } 
        exec($exec);
    } elseif(trim($_POST['secondSwipePause']) == "2") {
        $Second_Swipe_Pause = "2";
        $exec = 'echo "'.$Second_Swipe_Pause.'" > '.$conf['settings_abs'].'/Second_Swipe_Pause';
        if($debug == "true") {
            print $exec;
        } 
        exec($exec);
    } elseif(trim($_POST['secondSwipePause']) == "3") {
        $Second_Swipe_Pause = "3";
        $exec = 'echo "'.$Second_Swipe_Pause.'" > '.$conf['settings_abs'].'/Second_Swipe_Pause';
        if($debug == "true") {
            print $exec;
        } 
        exec($exec);
    } elseif(trim($_POST['secondSwipePause']) == "4") {
        $Second_Swipe_Pause = "4";
        $exec = 'echo "'.$Second_Swipe_Pause.'" > '.$conf['settings_abs'].'/Second_Swipe_Pause';
        if($debug == "true") {
            print $exec;
        } 
        exec($exec);
    } elseif(trim($_POST['secondSwipePause']) == "5") {
        $Second_Swipe_Pause = "5";
        $exec = 'echo "'.$Second_Swipe_Pause.'" > '.$conf['settings_abs'].'/Second_Swipe_Pause';
        if($debug == "true") {
            print $exec;
        } 
        exec($exec);
    } elseif(trim($_POST['secondSwipePause']) == "6") {
        $Second_Swipe_Pause = "6";
        $exec = 'echo "'.$Second_Swipe_Pause.'" > '.$conf['settings_abs'].'/Second_Swipe_Pause';
        if($debug == "true") {
            print $exec;
        } 
        exec($exec);
    } elseif(trim($_POST['secondSwipePause']) == "7") {
        $Second_Swipe_Pause = "7";
        $exec = 'echo "'.$Second_Swipe_Pause.'" > '.$conf['settings_abs'].'/Second_Swipe_Pause';
        if($debug == "true") {
            print $exec;
        } 
        exec($exec);
    } elseif(trim($_POST['secondSwipePause']) == "8") {
        $Second_Swipe_Pause = "8";
        $exec = 'echo "'.$Second_Swipe_Pause.'" > '.$conf['settings_abs'].'/Second_Swipe_Pause';
        if($debug == "true") {
            print $exec;
        } 
        exec($exec);
    } elseif(trim($_POST['secondSwipePause']) == "9") {
        $Second_Swipe_Pause = "9";
        $exec = 'echo "'.$Second_Swipe_Pause.'" > '.$conf['settings_abs'].'/Second_Swipe_Pause';
        if($debug == "true") {
            print $exec;
        } 
        exec($exec);
    } elseif(trim($_POST['secondSwipePause']) == "10") {
        $Second_Swipe_Pause = "10";
        $exec = 'echo "'.$Second_Swipe_Pause.'" > '.$conf['settings_abs'].'/Second_Swipe_Pause';
        if($debug == "true") {
            print $exec;
        } 
        exec($exec);
    }
    // execute shell to create config file
    exec("sudo ".$conf['scripts_abs']."/inc.writeGlobalConfig.sh");
}
?>
        <!-- input-group -->
            <div class="row" style="margin-bottom:1em;">
              <div class="col-md-6 col-xs-12">
              <h4><?php print $lang['settingsSecondSwipePauseInfo']; ?></h4>
                <form name='secondSwipePause' method='post' action='<?php print $_SERVER['PHP_SELF']; ?>'>
                  <div class="input-group my-group">
                    <select id="secondSwipePause" name="secondSwipePause" class="selectpicker form-control">
                    <?php
                        print "
                        <option value='0'";
                        if($Second_Swipe_Pause == "0") {
                            print " selected";
                        }
                        print ">OFF</option>\n";
                        print "
                        <option value='1'";
                        if($Second_Swipe_Pause == "1") {
                            print " selected";
                        }
                        print ">1 ".$lang['second'];
                        print "</option>\n";
                        print "
                        <option value='2'";
                        if($Second_Swipe_Pause == "2") {
                            print " selected";
                        }
                        print ">2 ".$lang['seconds'];
                        print "</option>\n";
                        print "
                        <option value='3'";
                        if($Second_Swipe_Pause == "3") {
                            print " selected";
                        }
                        print ">3 ".$lang['seconds'];
                        print "</option>\n";
                        print "
                        <option value='4'";
                        if($Second_Swipe_Pause == "4") {
                            print " selected";
                        }
                        print ">4 ".$lang['seconds'];
                        print "</option>\n";
                        print "
                        <option value='5'";
                        if($Second_Swipe_Pause == "5") {
                            print " selected";
                        }
                        print ">5 ".$lang['seconds'];
                        print "</option>\n";
                        print "
                        <option value='6'";
                        if($Second_Swipe_Pause == "6") {
                            print " selected";
                        }
                        print ">6 ".$lang['seconds'];
                        print "</option>\n";
                        print "
                        <option value='7'";
                        if($Second_Swipe_Pause == "7") {
                            print " selected";
                        }
                        print ">7 ".$lang['seconds'];
                        print "</option>\n";
                        print "
                        <option value='8'";
                        if($Second_Swipe_Pause == "8") {
                            print " selected";
                        }
                        print ">8 ".$lang['seconds'];
                        print "</option>\n";
                        print "
                        <option value='9'";
                        if($Second_Swipe_Pause == "9") {
                            print " selected";
                        }
                        print ">9 ".$lang['seconds'];
                        print "</option>\n";
                        print "
                        <option value='10'";
                        if($Second_Swipe_Pause == "10") {
                            print " selected";
                        }
                        print ">10 ".$lang['seconds'];
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
