<?php
/*
* eventually, the two pages cardEdit.php and cardRegisterNew.php should be one
* since most of the functionality is the same. This file is an intermediary step
* to unify both, taking some core functionality into one file and then see if it
* works for both.
*/

/******************************************
* read available RFID trigger commands
*/
$rfidAvailArr = rfidAvailArr();

function rfidAvailArr() {
    $rfidAvailRaw = "";
    $conf['conf_abs'] = realpath(getcwd().'/../settings/rfid_trigger_play.conf.sample');
    $fn = fopen($conf['conf_abs'],"r");
    while(! feof($fn))  {
        $result = fgets($fn);
        // ignore commented and empty lines
        if(!startsWith($result, "#") && trim($result) != "") {
            $rfidAvailRaw .= $result."\n";
        }
    }
    fclose($fn);
    $rfidAvailArr = parse_ini_string($rfidAvailRaw); //print "<pre>"; print_r($rfidAvailArr); print "</pre>";
    return $rfidAvailArr;
}
/******************************************/

/******************************************
* read RFID trigger commands already in use
*/
$rfidUsedArr = rfidUsedArr();

function rfidUsedArr() {
    $rfidUsedRaw = "";
    $fn = fopen("../settings/rfid_trigger_play.conf","r");
    while(! feof($fn))  {
        $result = fgets($fn);
        // ignore commented and empty lines
        if(!startsWith($result, "#") && trim($result) != "") {
            $rfidUsedRaw .= $result."\n";
        }
    }
    fclose($fn);
    $rfidUsedArr = parse_ini_string($rfidUsedRaw); //print "<pre>"; print_r($rfidUsedArr); print "</pre>";
    return $rfidUsedArr;
}
/******************************************/

/******************************************
* fill Avail with Used, else empty value
*/
$fillRfidArrAvailWithUsed = fillRfidArrAvailWithUsed($rfidAvailArr, $rfidUsedArr);
//print "<pre>fillRfidArrAvailWithUsed: \n"; print_r($fillRfidArrAvailWithUsed); print "</pre>";

function fillRfidArrAvailWithUsed($rfidAvailArr, $rfidUsedArr=array()) {
    foreach($rfidAvailArr as $key => $val) {
        // check if there is something in the existing conf file already
        if(
            startsWith($rfidUsedArr[$key], "%")
            || endsWith($rfidUsedArr[$key], "%")
        ) {
            $rfidAvailArr[$key] = "";
        } else {
            $rfidAvailArr[$key] = $rfidUsedArr[$key];
        }
    }
    return $rfidAvailArr;
}

/******************************************
* read the shortcuts available
*/
$shortcutstemp = array_filter(glob($conf['base_path'].'/shared/shortcuts/*'), 'is_file');
$shortcuts = array(); // the array with pairs of ID => foldername
// read files' content into array
foreach ($shortcutstemp as $shortcuttemp) {
    $shortcuts[basename($shortcuttemp)] = trim(file_get_contents($shortcuttemp));
}
//print "<pre>"; print_r($shortcuts); print "</pre>"; //???


/******************************************
* read the subfolders of $Audio_Folders_Path
*/
$audiofolders_abs = dir_list_recursively($Audio_Folders_Path);
usort($audiofolders_abs, 'strcasecmp');
/*
* get relative paths for pulldown
*/
$audiofolders = array();
foreach($audiofolders_abs as $audiofolder){
    /*
    * get the relative path as value, set the absolute path as key
    */
    $relpath = substr($audiofolder, strlen($Audio_Folders_Path) + 1, strlen($audiofolder));
    if($relpath != "") {
        $audiofolders[$audiofolder] = substr($audiofolder, strlen($Audio_Folders_Path) + 1, strlen($audiofolder));
    }
}

//print "<pre>"; print_r($audiofolders); print "</pre>"; //???
//print "<pre>\$post: "; print_r($post); print "</pre>"; //???

$messageError = "";
$messageAction = "";
$messageSuccess = "";

if($post['delete'] == "delete") {
    $messageAction .= "<p>The card with the ID '".$post['cardID']." has been deleted. 
        If you made a mistake, this is your chance to press 'Submit' to restore the card settings. 
        Else: Go <a href='index.php' class='mainMenu'><i class='mdi mdi-home'></i> Home</a>.</p>";
    // remove $fileshortcuts to cardID file in shortcuts
    $exec = "rm ".$fileshortcuts;
    if($debug == "true") {
        print "<pre>deleting shortcut:\n";
        print $exec;
        print "</pre>";
    } 
    exec($exec);
} elseif($post['submit'] == "submit") {
    /*
    * error check
    */
   
    // posted too little?
    if(
        (!isset($post['streamURL']) || !isset($post['streamType'])) 
        && !isset($post['audiofolder']) 
        && !isset($post['YTstreamURL']) 
        && !isset($post['TriggerCommand'])
    ) {
        $messageError .= $lang['cardRegisterErrorStreamOrAudio']." (error 002)";
    }
    // posted too much?
    $countActions = 0;
    if(isset($post['audiofolder'])) { $countActions++; }
    if(isset($post['audiofolderNew'])) { $countActions++; }
    if(isset($post['TriggerCommand'])) { $countActions++; }
    if($countActions > 1) {
        $messageError .= $lang['cardRegisterErrorStreamAndAudio']." (error 001)";
    }

    // posted streamFolderName and audiofolder
    if(isset($post['audiofolderNew']) && isset($post['audiofolder'])) {
        $messageError .= $lang['cardRegisterErrorExistingAndNew']." (error 003)";
    }

    // audiofolder already exists
    if(isset($post['audiofolderNew']) && file_exists($Audio_Folders_Path.'/'.$post['audiofolderNew'])) {
        $messageError .= $lang['cardRegisterErrorExistingFolder']." (error 004)";
    }

    // No streamFolderName entered
    if(isset($post['streamURL']) && !isset($post['audiofolderNew'])) {
        $messageError .= $lang['cardRegisterErrorSuggestFolder']." (error 005)";
        // suggest folder name: get rid of strange chars, prefixes and the like
        $post['audiofolderNew'] = $link = str_replace(array('http://','https://','/','=','-','.', 'www','?','&'), '', $post['streamURL']);
    }

    // streamFolderName not given
    if( 
        (isset($post['streamURL']) || isset($post['YTstreamURL'])) 
        && !isset($post['audiofolder']) 
        && !isset($post['audiofolderNew'])
    ) {
        $messageError .= $lang['cardRegisterErrorSuggestFolder']." (error 006)";
        // suggest folder name: get rid of strange chars, prefixes and the like
        $post['audiofolderNew'] = $link = str_replace(array('http://','https://','/','=','-','.', 'www','?','&'), '', $post['streamURL']);
    }

    //wrong spotify url, convert to mopidy format
    if((isset($post['streamURL']) && $post['streamType'] == "spotify") && (strpos($post['streamURL'], "https://open.spotify.com/") !== false)){        
        $patterns = array();
        $patterns[0] = '/https\:\/\/open.spotify.com/';
        $patterns[1] = '/\/(playlist|album|track|artist)\//';
        $patterns[2] = '/(\w+)\?(.*)/';
        $replacements = array();
        $replacements[0] = 'spotify:';
        $replacements[1] = '$1:';
        $replacements[2] = '$1';
        $newSpotifyURL = preg_replace($patterns, $replacements, $post['streamURL']);
        $messageError .= $lang['cardRegisterErrorConvertSpotifyURL']." (error 007)<br />".$post['streamURL']." ➔ ".$newSpotifyURL;
        $post['streamURL'] = $newSpotifyURL;
    }


    /*
    * any errors?
    */
    if($messageAction == "" && $messageError == "") {
        /*
        * do what's asked of us
        */
        $fileshortcuts = $conf['shared_abs']."/shortcuts/".$post['cardID'];
        if(isset($post['streamURL'])) {
            /*******************************************************
            * Stream URL to be created
            */
            // 20200512 included code from removed the old include('inc.processAddNewStream.php');
            
            // create new folder
            $streamfolder = $Audio_Folders_Path."/".$post['audiofolderNew']."/";
            $exec = "mkdir -p '".$streamfolder."'";
            exec($exec);
            // New folder is created so we link a RFID to it. Write $post['audiofolderNew'] to cardID file in shortcuts
            $exec = "rm ".$fileshortcuts."; echo '".$post['audiofolderNew']."' > ".$fileshortcuts."; chmod 777 ".$fileshortcuts;
            exec($exec);
            
            // figure out $streamfile depending on $post['streamType']
            switch($post['streamType']) {
            	case "spotify":
                    $streamfile = "spotify.txt";
                    break;
                case "podcast":
                    $streamfile = "podcast.txt";
                    break;
                case "livestream":
                    $streamfile = "livestream.txt";
                    break;
                default:
                    $streamfile = "url.txt";
            }
            
            // write $post['streamURL'] to $streamfile and make accessible to anyone
            $exec = "echo '".$post['streamURL']."' > '".$streamfolder."/".$streamfile."'; sudo chmod -R 777 '".$streamfolder."'";
            exec($exec);
            // success message
            $messageSuccess = "<p>".$lang['cardRegisterStream2Card']." ".$lang['globalFolder']." '".$post['audiofolderNew']."' ".$lang['globalCardId']." '".$post['cardID']."'</p>";
        }
        elseif(isset($post['TriggerCommand']) && trim($post['TriggerCommand']) != "false") {
            /*******************************************************
            * RFID triggers system commands
            */
            // 20200512 included code from removed the old include('inc.processAddTriggerCommand.php');
            
            // Replace the potential existing RFID value with the posted one
            //print $post['cardID']."->".$post['TriggerCommand'];
            $fillRfidArrAvailWithUsed[$post['TriggerCommand']] = $post['cardID'];
            
            /******************************************
            * Create new conf file based on posted values
            */
            
            // copy sample file to conf file
            exec("cp ../settings/rfid_trigger_play.conf.sample ../settings/rfid_trigger_play.conf; chmod 777 ../settings/rfid_trigger_play.conf");
            // replace posted values in new conf file
            foreach($fillRfidArrAvailWithUsed as $key => $val) {
                // only change those with values in the form (not empty)
                if($val != "") {
                    exec("sed -i 's/%".$key."%/".$val."/' '../settings/rfid_trigger_play.conf'");
                }
            }
            // success message
            $messageSuccess = $lang['cardRegisterTriggerSuccess']." ".$post['TriggerCommand'];
        }        
        elseif(isset($post['YTstreamURL'])) {
            /*******************************************************
            * YouTube Download
            */
            // 20200512 included code from removed the old include('inc.processAddYT.php');
            
            if(isset($post['audiofolderNew'])) {
                // create new folder
                $exec = "mkdir --parents '".$Audio_Folders_Path."/".$post['audiofolderNew']."'; chmod 777 '".$Audio_Folders_Path."/".$post['audiofolderNew']."'";
                exec($exec);
                $foldername = $Audio_Folders_Path."/".$post['audiofolderNew'];
                // New folder is created so we link a RFID to it. Write $post['audiofolderNew'] to cardID file in shortcuts
                $exec = "rm ".$fileshortcuts."; echo '".$post['audiofolderNew']."' > ".$fileshortcuts."; chmod 777 ".$fileshortcuts;
                exec($exec);
				// write $streamfile and make accessible to anyone
				$ytfile = "youtube.txt";
				$exec = "echo '' > '".$foldername."/".$ytfile."'; sudo chmod -R 777 '".$foldername."'";
				exec($exec);
            } else {
                // link to existing audiofolder
                $foldername = $Audio_Folders_Path."/".$post['audiofolder'];
            }
            $exec = "cd '".$foldername."'; youtube-dl -f bestaudio --extract-audio --audio-format mp3 ".$post['YTstreamURL']." > ".$conf['shared_abs']."/youtube-dl.log; chmod 777 ".$foldername."/* 2>&1 &";
            exec($exec);
            // success message
            $messageSuccess = $lang['cardRegisterDownloadingYT'];
        } 
        elseif(isset($post['audiofolder']) && trim($post['audiofolder']) != "false") {
            /*******************************************************
            * connect card with existing audio folder
            */
            // write $post['audiofolder'] to cardID file in shortcuts
            $exec = "rm ".$fileshortcuts."; echo '".$post['audiofolder']."' > ".$fileshortcuts."; chmod 777 ".$fileshortcuts;
            exec($exec);
            // success message
            $messageSuccess = "<p>".$lang['cardRegisterFolder2Card']."  ".$lang['globalFolder']." '".$post['audiofolder']."' ".$lang['globalCardId']." '".$post['cardID']."'</p>";
        }
        elseif(isset($post['audiofolderNew']) && trim($post['audiofolderNew']) != "") {
            /*
            * connect card with new audio folder
            */
            // create new folder
            $exec = "mkdir --parents '".$Audio_Folders_Path."/".$post['audiofolderNew']."'; chmod 777 '".$Audio_Folders_Path."/".$post['audiofolderNew']."'";
            exec($exec);
            $foldername = $Audio_Folders_Path."/".$post['audiofolderNew'];
            // New folder is created so we link a RFID to it. Write $post['audiofolderNew'] to cardID file in shortcuts
            $exec = "rm ".$fileshortcuts."; echo '".$post['audiofolderNew']."' > ".$fileshortcuts."; chmod 777 ".$fileshortcuts;
            exec($exec);
            // success message
            $messageSuccess = "<p>".$lang['cardRegisterFolder2Card']."  ".$lang['globalFolder']." '".$post['audiofolderNew']."' ".$lang['globalCardId']." '".$post['cardID']."'</p>";
        }
    } else {
        /*
        * Warning given, action can not be taken
        */
    }
}
?>
