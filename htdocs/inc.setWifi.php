<?php
/*
* read ssid and password from /etc/wpa_supplicant/wpa_supplicant.conf
*/
$wpaconf = file_get_contents("/etc/wpa_supplicant/wpa_supplicant.conf");
/*
* get the lines we need (in a rough way...)
*/
foreach(preg_split("/((\r?\n)|(\r\n?))/", $wpaconf) as $line){
    unset($temp);
    $temp = explode("=", $line);
    if(trim($temp[0]) == "ssid") {
        $CONFssid = trim(trim($temp[1]), '"');
    }
    if(trim($temp[0]) == "psk") {
        $CONFWIFIpass = trim(trim($temp[1]), '"');
    }   
} 
/*
* see if we got some values from the form
*/
if(trim($_POST['WIFIssid']) != "") {
    $WIFIssid = trim($_POST['WIFIssid']);
} else {
    $WIFIssid = $CONFssid;
}
if(trim($_POST['WIFIpass']) != "") {
    $WIFIpass = trim($_POST['WIFIpass']);
} else {
    $WIFIpass = $CONFWIFIpass;
}
/*
* Now we need to check if we need to create a new wpa_supplicant.conf
* This is the case if either value coming from the form is different from
* the current conf file
*/
unset($exec);
if($WIFIssid != $CONFssid || $WIFIpass != $CONFWIFIpass) {
    // make multiline bash
    $exec = "bash <<'END'
sudo cp /home/pi/RPi-Jukebox-RFID/misc/sampleconfigs/wpa_supplicant.conf.stretch-default2.sample /etc/wpa_supplicant/wpa_supplicant.conf
sudo sed -i 's/%WIFIssid%/'".$WIFIssid."'/' /etc/wpa_supplicant/wpa_supplicant.conf
sudo sed -i 's/%WIFIpass%/'".$WIFIpass."'/' /etc/wpa_supplicant/wpa_supplicant.conf
sudo chown root:netdev /etc/wpa_supplicant/wpa_supplicant.conf
sudo chmod 664 /etc/wpa_supplicant/wpa_supplicant.conf
# restart wlan0
# dunno how to do this on the command line. The following doesn't disconnect the WiFi:
# sudo ip link set wlan0 down && sudo ip link set wlan0 up
END";
    passthru($exec);
}
    
if($debug == "true") {
    print "<pre>";
    print "\$wpaconf:\n";
    print $wpaconf;
    print "\$WIFIssid: ".$WIFIssid."\n";
    print "\$WIFIpass: ".$WIFIpass."\n";
    print "\$_POST:\n";
    print_r($_POST);
    print "</pre>";
}
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
?>        
        <!-- Text input-->
        <div class="form-group">
          <label class="col-md-4 control-label" for="WIFIssid"><?php print $lang['globalSSID']; ?></label>
          <div class="col-md-6">
          <input value="<?php
            if(isset($WIFIssid) && $WIFIssid != "") {
                print $WIFIssid;
            }
          ?>" id="WIFIssid" name="WIFIssid" placeholder="<?php print $lang['settingsWifiSsidPlaceholder']; ?>" class="form-control input-md" type="text" required="required">
          <span class="help-block"><?php print $lang['settingsWifiSsidHelp']; ?></span>  
          </div>
        </div>
        
        <!-- Text input-->
        <div class="form-group">
          <label class="col-md-4 control-label" for="WIFIpass"><?php print $lang['globalPassword']; ?></label>
          <div class="col-md-6">
          <input value="<?php
            if(isset($WIFIpass) && $WIFIpass != "") {
                print $WIFIpass;
            }
          ?>" id="WIFIpass" name="WIFIpass" placeholder="" class="form-control input-md" type="password" required="required">
          <span class="help-block"></span>  
          </div>
        </div>
        
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