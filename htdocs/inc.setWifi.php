<?php

$active_essid = trim(exec("iwconfig wlan0 | grep ESSID | cut -d ':' -f 2"),'"');
/*
* Reconfigure all entries from UI
*/
unset($exec);
if(isset($_POST["submitWifi"]) && $_POST["submitWifi"] == "submit") {
    // make multiline bash
    $exec  = "bash -e <<'END'\n";
    $exec .= "source ".$conf['scripts_abs']."/helperscripts/inc.networkHelper.sh\n";
    $exec .= "clear_wireless_networks\n";

    $tempPOST = $_POST;
    $_POST=array(); //clear
    foreach ( $tempPOST as $post_key => $post_value ) {
        unset($temp_ssid);
        unset($temp_pass);
        unset($temp_prio);
        if ( substr(trim($post_key), 0, 9) == "WIFIssid_" ) {
            $temp_ssid = trim($post_value);
            $post_key = "WIFIpass_".substr(trim($post_key), 9);
            $post_value = $tempPOST[$post_key];
            $temp_pass = trim($post_value);
            $post_key = "WIFIprio_".substr(trim($post_key), 9);
            $post_value = $tempPOST[$post_key];
            $temp_prio = trim($post_value);

            if (isset($temp_ssid) && $temp_ssid != "" && isset($temp_pass) && strlen($temp_pass) >= 8) {
                if(!isset($temp_prio) || !is_numeric($temp_prio)) {
                    $temp_prio = 0;
                }
                $exec .= "add_wireless_network wlan0 ".$temp_ssid." ".$temp_pass." ".$temp_prio."\n";
            }
        }
    }

    $exec .= "END\n";
    exec("sudo bash -c '". $exec . "'");
}

/*
* get all configured wifis
*/
$network_confs_shell = shell_exec("sudo bash -c 'source ".$conf['scripts_abs']."/helperscripts/inc.networkHelper.sh && get_wireless_networks'");
$network_confs = explode(' ',$network_confs_shell);

$networks = array();
foreach($network_confs as $line){
    unset($temp_ssid);
    unset($temp_pass);
    unset($temp_prio);
	unset($temp_active);

    $network_conf = explode(':',$line);
    $temp_ssid = trim($network_conf[0]);
    $temp_pass = trim($network_conf[1]);
    $temp_prio = trim($network_conf[2]);
	$temp_active = isset($active_essid) && $temp_ssid == $active_essid;

    if(isset($temp_ssid) && $temp_ssid != "" && isset($temp_pass) && $temp_pass != "") {
		if(!isset($temp_prio) || !is_numeric($temp_prio)) {
			$temp_prio = 0;
		}
        $temp_entry = array($temp_ssid => [ $temp_pass, $temp_prio, $temp_active ]);
        # use different methods to have the same behavior: the data of the first appearance are kept, following will be ignored
        if($temp_active) {
            $networks = array_merge($temp_entry, $networks);
        } else {
            $networks = $networks + $temp_entry;
        }
    }
}
unset($temp_ssid);
unset($temp_pass);
unset($temp_prio);

?>

<form name='wifi' method='post' action='<?php print $_SERVER['PHP_SELF']; ?>'>
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
    foreach ( $networks as $WIFIssid => $WIFIconf ) {
        $WIFIpass = $WIFIconf[0];
        $WIFIprio = $WIFIconf[1];
		$WIFIactive = $WIFIconf[2];
        $WIFIindex = $network_index++;
?>
            <li class="list-group-item">
                <div class="row">

                    <!-- Text input-->
                    <div class="form-group">
                        <label class="col-md-4 control-label" for="WIFIssid_<?php print $WIFIindex; ?>"><?php
                            if($WIFIactive) {
                                print $lang['globalSSID']."*";
                            } else {
                                print $lang['globalSSID'];
                            }
                        ?></label>
                        <div class="col-md-6">
                            <input value="<?php
								print $WIFIssid;
                            ?>" id="WIFIssid_<?php print $WIFIindex; ?>" name="WIFIssid_<?php print $WIFIindex; ?>" placeholder="<?php print $lang['settingsWifiSsidPlaceholder']; ?>" class="form-control input-md" type="text" <?php print $WIFIactive ? "readonly" : ""; ?>>
                            <span class="help-block"></span>
                        </div>
                    </div>

                    <!-- Text input-->
                    <div class="form-group">
                        <label class="col-md-4 control-label" for="WIFIpass_<?php print $WIFIindex; ?>"><?php print $lang['globalPassword']; ?></label>
                        <div class="col-md-6">
                            <input value="<?php
								print $WIFIpass;
                            ?>" id="WIFIpass_<?php print $WIFIindex; ?>" name="WIFIpass_<?php print $WIFIindex; ?>" placeholder="" class="form-control input-md" type="password" minlength="8" maxlength="63" <?php print $WIFIactive ? "readonly" : ""; ?>>
                            <span class="help-block"></span>
                        </div>
                    </div>

                    <!-- Text input-->
                    <div class="form-group">
                      <label class="col-md-4 control-label" for="WIFIprio_<?php print $WIFIindex; ?>"><?php print $lang['globalPriority']; ?></label>
                      <div class="col-md-6">
                          <input value="<?php
							  print $WIFIprio;
                          ?>" id="WIFIprio_<?php print $WIFIindex; ?>" name="WIFIprio_<?php print $WIFIindex; ?>" placeholder="" class="form-control input-md" type="number" min="0" max="100" <?php print $WIFIactive ? "readonly" : ""; ?>>
                          <span class="help-block"></span>
                      </div>
                    </div>
                </div>
            </li>
<?php
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
