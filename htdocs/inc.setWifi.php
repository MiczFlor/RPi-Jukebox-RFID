<?php

$active_essid = trim(exec("iwconfig wlan0 | grep ESSID | cut -d ':' -f 2"),'"');
/*
* Now we need to check if we need to create a new wpa_supplicant.conf
*/
unset($exec);
if(isset($_POST["submitWifi"]) && $_POST["submitWifi"] == "submit") {
    $networks=array(); //clear
    $priorities=array(); //clear

    foreach ( $_POST as $post_key => $post_value ) {
        if ( substr(trim($post_key), 0, 9) == "WIFIssid_" ) {
            $WIFIssid = trim($post_value);
            $post_key = "WIFIpass_".substr(trim($post_key), 9);
            $post_value = $_POST[$post_key];
            $WIFIpass = trim($post_value);
            $post_key = "WIFIprio_".substr(trim($post_key), 9);
            $post_value = $_POST[$post_key];
            $WIFIprio = trim($post_value);

            if ( isset($WIFIssid) && $WIFIssid != "") {
                if(isset($WIFIpass) && strlen($WIFIpass) >= 8) {
                    $networks[$WIFIssid] = $WIFIpass;
                }
                if(isset($WIFIprio) && $WIFIprio != "") {
                    $priorities[$WIFIssid] = $WIFIprio;
                }
            }
        }
    }
    $_POST=array(); //clear

    // make multiline bash
    $exec  = "bash -e <<'END'\n";
    $exec .= "source ".$conf['scripts_abs']."/helperscripts/inc.networkHelper.sh\n";
    $exec .= "clear_wireless_networks\n";
    foreach ( $networks as $WIFIssid => $WIFIpass ) {
        $WIFIprio = $priorities[$WIFIssid];
        $exec .= "add_wireless_network wlan0 ".$WIFIssid." ".$WIFIpass." ".$WIFIprio."\n";
    }
    $exec .= "END\n";
    exec("sudo bash -c '". $exec . "'");
}

$network_confs_shell = shell_exec("sudo bash -c 'source ".$conf['scripts_abs']."/helperscripts/inc.networkHelper.sh && get_all_wireless_networks'");
$network_confs = explode(' ',$network_confs_shell);
/*
* get the lines we need
*/
$networks = array();
$priorities = array();
foreach($network_confs as $line){
    unset($temp_ssid);
    unset($temp_pass);
    unset($temp_prio);

    $network_conf = explode(':',$line);
    $temp_ssid = $network_conf[0];
    $temp_pass = $network_conf[1];
    $temp_prio = $network_conf[2];

    if(isset($temp_ssid) && $temp_ssid != "") {
        if(isset($temp_pass)) {
            $networks[$temp_ssid] = $temp_pass;
        }
        if(isset($temp_prio)) {
            $priorities[$temp_ssid] = $temp_prio;
        }
    }
}
unset($temp_ssid);
unset($temp_pass);
unset($temp_prio);

?>

<form name='volume' method='post' action='<?php print $_SERVER['PHP_SELF']; ?>'>
    <fieldset>
        <!-- Form Name -->
        <legend><?php print $lang['globalWifiNetwork']; ?></legend>
<?php
    if(isset($exec)) {
        print '
        <div class="alert alert-info">
        '.$lang['settingsWifiRestart'].'
        </div>';
    }
    if(isset($active_essid) && $active_essid != "") {
        print '
        <div class="alert alert-info">
        '.$lang['globalSSID'].': '.$active_essid.'
        </div>';
    }
?>
        <ul class="list-group">
<?php
    $network_index = 0;
    foreach ( $networks as $WIFIssid => $WIFIpass ) {
        $WIFIprio = $priorities[$WIFIssid];
?>
            <li class="list-group-item">
                <div class="row">

                    <!-- Text input-->
                    <div class="form-group">
                        <label class="col-md-4 control-label" for="WIFIssid_<?php print $network_index; ?>"><?php
                            if(isset($WIFIssid) && isset($active_essid) && $WIFIssid == $active_essid) {
                                print $lang['globalSSID']."*";
                            } else {
                                print $lang['globalSSID'];
                            }
                        ?></label>
                        <div class="col-md-6">
                            <input value="<?php
                                if(isset($WIFIssid) && $WIFIssid != "") {
                                    print $WIFIssid;
                                }
                            ?>" id="WIFIssid_<?php print $network_index; ?>" name="WIFIssid_<?php print $network_index; ?>" placeholder="<?php print $lang['settingsWifiSsidPlaceholder']; ?>" class="form-control input-md" type="text">
                            <span class="help-block"></span>
                        </div>
                    </div>

                    <!-- Text input-->
                    <div class="form-group">
                        <label class="col-md-4 control-label" for="WIFIpass_<?php print $network_index; ?>"><?php print $lang['globalPassword']; ?></label>
                        <div class="col-md-6">
                            <input value="<?php
                                if(isset($WIFIpass) && $WIFIpass != "") {
                                    print $WIFIpass;
                                }
                            ?>" id="WIFIpass_<?php print $network_index; ?>" name="WIFIpass_<?php print $network_index; ?>" placeholder="" class="form-control input-md" type="password" minlength="8" maxlength="63">
                            <span class="help-block"></span>
                        </div>
                    </div>

                    <!-- Text input-->
                    <div class="form-group">
                      <label class="col-md-4 control-label" for="WIFIprio_<?php print $network_index; ?>"><?php print $lang['globalPriority']; ?></label>
                      <div class="col-md-6">
                          <input value="<?php
                              if(isset($WIFIprio) && $WIFIprio != "") {
                                  print $WIFIprio;
                              } else {
                                  print 0;
                              }
                          ?>" id="WIFIprio_<?php print $network_index; ?>" name="WIFIprio_<?php print $network_index; ?>" placeholder="" class="form-control input-md" type="number" min="0" max="100">
                          <span class="help-block"></span>
                      </div>
                    </div>
                </div>
            </li>
<?php
        $network_index++;
    }
?>
            <li class="list-group-item">
                <div class="row">
                    <!-- Text input-->
                    <div class="form-group">
                      <label class="col-md-4 control-label" for="WIFIssid_<?php print $network_index; ?>"><?php print $lang['globalSSID']; ?></label>
                      <div class="col-md-6">
                          <input value="" id="WIFIssid_<?php print $network_index; ?>" name="WIFIssid_<?php print $network_index; ?>" placeholder="<?php print $lang['settingsWifiSsidPlaceholder']; ?>" class="form-control input-md" type="text">
                          <span class="help-block"><?php print $lang['settingsWifiSsidHelp']; ?></span>
                      </div>
                    </div>

                    <!-- Text input-->
                    <div class="form-group">
                      <label class="col-md-4 control-label" for="WIFIpass_<?php print $network_index; ?>"><?php print $lang['globalPassword']; ?></label>
                      <div class="col-md-6">
                          <input value="" id="WIFIpass_<?php print $network_index; ?>" name="WIFIpass_<?php print $network_index; ?>" placeholder="" class="form-control input-md" type="password" minlength="8" maxlength="63">
                          <span class="help-block"><?php print $lang['settingsWifiPassHelp']; ?></span>
                      </div>
                    </div>

                    <!-- Text input-->
                    <div class="form-group">
                      <label class="col-md-4 control-label" for="WIFIprio_<?php print $network_index; ?>"><?php print $lang['globalPriority']; ?></label>
                      <div class="col-md-6">
                          <input value="0" id="WIFIprio_<?php print $network_index; ?>" name="WIFIprio_<?php print $network_index; ?>" placeholder="" class="form-control input-md" type="number" min="0" max="100">
                          <span class="help-block"><?php print $lang['settingsWifiPrioHelp']; ?></span>
                      </div>
                    </div>
                </div>
            </li>
        </ul>
    </fieldset>

    <!-- Button (Double) -->
    <div class="form-group">
        <label class="col-md-4 control-label" for="submit"></label>
        <div class="col-md-8">
            <button id="submitWifi" name="submitWifi" class="btn btn-success" value="submit"><?php print $lang['globalSubmit']; ?></button>
            <br clear='all'><br>
        </div>
    </div>

</form>
