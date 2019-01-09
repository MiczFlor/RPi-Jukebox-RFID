<?php
/**************************************************
* VARIABLES
* No changes required if you stuck to the
* INSTALL-stretch.md instructions.
* If you want to change the paths, edit config.php
***************************************************/

/*
* DEBUGGING
* for debugging, set following var to true.
* This will only print the executable strings, not execute them
*/
$debug = "false"; // true or false


/*
* load language strings
*/
include("inc.langLoad.php");


/* NO CHANGES BENEATH THIS LINE ***********/
/*
* Configuration file
* Due to an initial commit with the config file 'config.php' and NOT 'config.php.sample'
* we need to check first if the config file exists (it might get erased by 'git pull').
* If it does not exist:
* a) copy sample file to config.php and give warning
* b) if sample file does not exist: throw error and die
*/
if(!file_exists("config.php")) {
    if(!file_exists("config.php.sample")) {
        // no config nor sample config found. die.
        print "<h1>Configuration file not found</h1>
            <p>The files 'config.php' and 'config.php.sample' were not found in the
            directory 'htdocs'. Please download 'htdocs/config.php.sample' from the 
            <a href='https://github.com/MiczFlor/RPi-Jukebox-RFID/'>online repository</a>,
            copy it locally to 'htdocs/config.php' and then adjust it to fit your system.</p>";
        die;
    } else {
        // no config but sample config found: make copy (and give warning)
        if(!(copy("config.php.sample", "config.php"))) {
            // sample config can not be copied. die.
            print "<h1>Configuration file could not be created</h1>
                <p>The file 'config.php' was not found in the
                directory 'htdocs'. Attempting to create this file from 'config.php.sample'
                resulted in an error. </p>
                <p>
                Are the folder settings correct? You could try to run the following commands
                inside the folder 'RPi-Jukebox-RFID' and then reload the page:<br/>
                <pre>
sudo chmod -R 775 htdocs/
sudo chgrp -R www-data htdocs/
                </pre>
                </p>
                Alternatively, download 'htdocs/config.php.sample' from the 
                <a href='https://github.com/MiczFlor/RPi-Jukebox-RFID/'>online repository</a>,
                copy it locally to 'htdocs/config.php' and then adjust it to fit your system.</p>";
            die;
        } else {
            $warning = "<h4>Configuration file created</h4>
                <p>The file 'config.php' was not found in the
                directory 'htdocs'. A copy of the sample file 'config.php.sample' was made automatically.
                If you encounter any errors, edit the newly created 'config.php'.
                </p>
            ";
        }
    }
}
include("config.php");

$conf['url_abs']    = "http://".$_SERVER['HTTP_HOST'].$_SERVER['PHP_SELF']; // URL to PHP_SELF

include("func.php");

// path to script folder from github repo on RPi
$conf['scripts_abs'] = realpath(getcwd().'/../scripts/');
// path to shared folder from github repo on RPi
$conf['shared_abs'] = realpath(getcwd().'/../shared/');
// path to settings folder from github repo on RPi
$conf['settings_abs'] = realpath(getcwd().'/../settings/');

/*
* Vars from the settings folder
*/
$Audio_Folders_Path = trim(file_get_contents($conf['settings_abs'].'/Audio_Folders_Path'));
$Latest_Folder_Played = trim(file_get_contents($conf['settings_abs'].'/Latest_Folder_Played'));
$Second_Swipe = trim(file_get_contents($conf['settings_abs'].'/Second_Swipe'));
if(file_exists($conf['settings_abs'].'/ShowCover')) {
    $ShowCover = trim(file_get_contents($conf['settings_abs'].'/ShowCover'));
} else {
    $ShowCover = "ON";
}
$version = trim(file_get_contents($conf['settings_abs'].'/version'));
if(file_exists(dirname(__FILE__).'/../settings/edition')) {
    $edition = trim(file_get_contents(dirname(__FILE__).'/../settings/edition'));
} else {
    $edition = "classic";
    $edition = "classic";
}

/*******************************************
* URLPARAMETERS
*******************************************/

$urlparams = array();
/*
* Firstly, collect via 'GET', later collect 'POST'
*/
if(isset($_GET['play']) && trim($_GET['play']) != "") {
    $urlparams['play'] = trim($_GET['play']);
}
if(isset($_GET['recursive']) && trim($_GET['recursive']) == "true") {
    $urlparams['recursive'] = trim($_GET['recursive']);
}

if(isset($_GET['playpos']) && trim($_GET['playpos']) != "") {
    $urlparams['playpos'] = trim($_GET['playpos']);
}

if(isset($_GET['player']) && trim($_GET['player']) != "") {
    $urlparams['player'] = trim($_GET['player']);
}

if(isset($_GET['stop']) && trim($_GET['stop']) != "") {
    $urlparams['stop'] = trim($_GET['stop']);
}

if(isset($_GET['volume']) && trim($_GET['volume']) != "") {
    $urlparams['volume'] = trim($_GET['volume']);
}

if(isset($_GET['maxvolume']) && trim($_GET['maxvolume']) != "") {
    $urlparams['maxvolume'] = trim($_GET['maxvolume']);
}

if(isset($_GET['volstep']) && trim($_GET['volstep']) != "") {
    $urlparams['volstep'] = trim($_GET['volstep']);
}

if(isset($_GET['mute']) && trim($_GET['mute']) == "true") {
    $urlparams['mute'] = trim($_GET['mute']);
}

if(isset($_GET['volumeup']) && trim($_GET['volumeup']) == "true") {
    $urlparams['volumeup'] = trim($_GET['volumeup']);
}

if(isset($_GET['volumedown']) && trim($_GET['volumedown']) == "true") {
    $urlparams['volumedown'] = trim($_GET['volumedown']);
}

if(isset($_GET['shutdown']) && trim($_GET['shutdown']) != "") {
    $urlparams['shutdown'] = trim($_GET['shutdown']);
}

if(isset($_GET['reboot']) && trim($_GET['reboot']) != "") {
    $urlparams['reboot'] = trim($_GET['reboot']);
}

if(isset($_GET['scan']) && trim($_GET['scan']) != "") {
    $urlparams['scan'] = trim($_GET['scan']);
}

if(isset($_GET['idletime']) && trim($_GET['idletime']) != "") {
    $urlparams['idletime'] = trim($_GET['idletime']);
}

if(isset($_GET['shutdownafter']) && trim($_GET['shutdownafter']) != "") {
    $urlparams['shutdownafter'] = trim($_GET['shutdownafter']);
}

if(isset($_GET['rfidstatus']) && trim($_GET['rfidstatus']) == "turnon") {
    $urlparams['rfidstatus'] = trim($_GET['rfidstatus']);
}

if(isset($_GET['rfidstatus']) && trim($_GET['rfidstatus']) == "turnoff") {
    $urlparams['rfidstatus'] = trim($_GET['rfidstatus']);
}

if(isset($_GET['gpiostatus']) && trim($_GET['gpiostatus']) == "turnon") {
    $urlparams['gpiostatus'] = trim($_GET['gpiostatus']);
}

if(isset($_GET['gpiostatus']) && trim($_GET['gpiostatus']) == "turnoff") {
    $urlparams['gpiostatus'] = trim($_GET['gpiostatus']);
}

if(isset($_GET['enableresume']) && trim($_GET['enableresume']) != "") {
    $urlparams['enableresume'] = trim($_GET['enableresume']);
}

if(isset($_GET['disableresume']) && trim($_GET['disableresume']) != "") {
    $urlparams['disableresume'] = trim($_GET['disableresume']);
}

if(isset($_GET['enableshuffle']) && trim($_GET['enableshuffle']) != "") {
    $urlparams['enableshuffle'] = trim($_GET['enableshuffle']);
}

if(isset($_GET['disableshuffle']) && trim($_GET['disableshuffle']) != "") {
    $urlparams['disableshuffle'] = trim($_GET['disableshuffle']);
}

/*
* Now check for $_POST
*/
if(isset($_POST['play']) && trim($_POST['play']) != "") {
    $urlparams['play'] = trim($_POST['play']);
}
if(isset($_POST['recursive']) && trim($_POST['recursive']) == "true") {
    $urlparams['recursive'] = trim($_POST['recursive']);
}

if(isset($_POST['playpos']) && trim($_POST['playpos']) != "") {
    $urlparams['playpos'] = trim($_POST['playpos']);
}

if(isset($_POST['player']) && trim($_POST['player']) != "") {
    $urlparams['player'] = trim($_POST['player']);
}

if(isset($_POST['stop']) && trim($_POST['stop']) != "") {
    $urlparams['stop'] = trim($_POST['stop']);
}

if(isset($_POST['volume']) && trim($_POST['volume']) != "") {
    $urlparams['volume'] = trim($_POST['volume']);
}

if(isset($_POST['maxvolume']) && trim($_POST['maxvolume']) != "") {
    $urlparams['maxvolume'] = trim($_POST['maxvolume']);
}

if(isset($_POST['volstep']) && trim($_POST['volstep']) != "") {
    $urlparams['volstep'] = trim($_POST['volstep']);
}

if(isset($_POST['mute']) && trim($_POST['mute']) == "true") {
    $urlparams['mute'] = trim($_POST['mute']);
}

if(isset($_POST['volumeup']) && trim($_POST['volumeup']) == "true") {
    $urlparams['volumeup'] = trim($_POST['volumeup']);
}

if(isset($_POST['volumedown']) && trim($_POST['volumedown']) == "true") {
    $urlparams['volumedown'] = trim($_POST['volumedown']);
}

if(isset($_POST['shutdown']) && trim($_POST['shutdown']) != "") {
    $urlparams['shutdown'] = trim($_POST['shutdown']);
}

if(isset($_POST['reboot']) && trim($_POST['reboot']) != "") {
    $urlparams['reboot'] = trim($_POST['reboot']);
}

if(isset($_POST['scan']) && trim($_POST['scan']) != "") {
    $urlparams['scan'] = trim($_POST['scan']);
}

if(isset($_POST['idletime']) && trim($_POST['idletime']) != "") {
    $urlparams['idletime'] = trim($_POST['idletime']);
}

if(isset($_POST['shutdownafter']) && trim($_POST['shutdownafter']) != "") {
    $urlparams['shutdownafter'] = trim($_POST['shutdownafter']);
}

if(isset($_POST['rfidstatus']) && trim($_POST['rfidstatus']) == "turnon") {
    $urlparams['rfidstatus'] = trim($_POST['rfidstatus']);
}

if(isset($_POST['rfidstatus']) && trim($_POST['rfidstatus']) == "turnoff") {
    $urlparams['rfidstatus'] = trim($_POST['rfidstatus']);
}

if(isset($_POST['gpiostatus']) && trim($_POST['gpiostatus']) == "turnon") {
    $urlparams['gpiostatus'] = trim($_POST['gpiostatus']);
}

if(isset($_POST['gpiostatus']) && trim($_POST['gpiostatus']) == "turnoff") {
    $urlparams['gpiostatus'] = trim($_POST['gpiostatus']);
}

if(isset($_POST['enableresume']) && trim($_POST['enableresume']) != "") {
    $urlparams['enableresume'] = trim($_POST['enableresume']);
}

if(isset($_POST['disableresume']) && trim($_POST['disableresume']) != "") {
    $urlparams['disableresume'] = trim($_POST['disableresume']);
}

if(isset($_POST['enableshuffle']) && trim($_POST['enableshuffle']) != "") {
    $urlparams['enableshuffle'] = trim($_POST['enableshuffle']);
}

if(isset($_POST['disableshuffle']) && trim($_POST['disableshuffle']) != "") {
    $urlparams['disableshuffle'] = trim($_POST['disableshuffle']);
}

/*******************************************
* URLPARAMETERS cardEdit.php and cardRegisterNew.php
*******************************************/
if(isset($_POST['cardID']) && $_POST['cardID'] != "") { // && file_exists('../shared/shortcuts/'.$_POST['cardID'])) {
    $post['cardID'] = $_POST['cardID'];
} elseif(isset($_GET['cardID']) && $_GET['cardID'] != "") {
    $post['cardID'] = $_GET['cardID'];
}
if(isset($_POST['streamURL']) && $_POST['streamURL'] != "") {
    $post['streamURL'] = $_POST['streamURL'];
}
if(isset($_POST['streamFolderName']) && $_POST['streamFolderName'] != "") {
    $post['streamFolderName'] = $_POST['streamFolderName'];
}
if(isset($_POST['streamType']) && $_POST['streamType'] != "" && $_POST['streamType'] != "false") {
    $post['streamType'] = $_POST['streamType'];
}
if(isset($_POST['audiofolder']) && $_POST['audiofolder'] != "" && $_POST['audiofolder'] != "false" && file_exists($Audio_Folders_Path.'/'.$_POST['audiofolder'])) {
    $post['audiofolder'] = $_POST['audiofolder'];
}
if(isset($_POST['YTstreamURL']) && $_POST['YTstreamURL'] != "") {
    $post['YTstreamURL'] = $_POST['YTstreamURL'];
}
if(isset($_POST['YTstreamFolderName']) && $_POST['YTstreamFolderName'] != "") {
    $post['YTstreamFolderName'] = $_POST['YTstreamFolderName'];
}
if(isset($_POST['YTaudiofolder']) && $_POST['YTaudiofolder'] != "" && $_POST['YTaudiofolder'] != "false" && file_exists($Audio_Folders_Path.'/'.$_POST['YTaudiofolder'])) {
    $post['YTaudiofolder'] = $_POST['YTaudiofolder'];
}
if(isset($_POST['submit']) && $_POST['submit'] == "submit") {
    $post['submit'] = $_POST['submit'];
}
if(isset($_POST['delete']) && $_POST['delete'] == "delete") {
    $post['delete'] = $_POST['delete'];
}
if(isset($_GET['delete']) && $_GET['delete'] == "delete") {
    $post['delete'] = $_GET['delete'];
}


/*******************************************
* ACTIONS
*******************************************/

// change volume
if(isset($urlparams['volume'])) {
    $exec = "/usr/bin/sudo ".$conf['scripts_abs']."/playout_controls.sh -c=setvolume -v=".$urlparams['volume'];
    if($debug == "true") { 
        print "Command: ".$exec; 
    } else { 
        exec($exec);
        /* redirect to drop all the url parameters */
        header("Location: ".$conf['url_abs']);
        exit; 
    }
}

// change max volume
if(isset($urlparams['maxvolume'])) {
    $exec = "/usr/bin/sudo ".$conf['scripts_abs']."/playout_controls.sh -c=setmaxvolume -v=".$urlparams['maxvolume'];
    if($debug == "true") { 
        print "Command: ".$exec; 
    } else { 
        exec($exec);
        /* redirect to drop all the url parameters */
        header("Location: ".$conf['url_abs']);
        exit; 
    }
}

// change volume step
if(isset($urlparams['volstep'])) {
    $exec = "/usr/bin/sudo ".$conf['scripts_abs']."/playout_controls.sh -c=setvolstep -v=".$urlparams['volstep'];
    if($debug == "true") { 
        print "Command: ".$exec; 
    } else { 
        exec($exec);
        /* redirect to drop all the url parameters */
        header("Location: ".$conf['url_abs']);
        exit; 
    }
}


// volume mute (toggle)
if(isset($urlparams['mute'])) {
    $exec = "/usr/bin/sudo ".$conf['scripts_abs']."/playout_controls.sh -c=mute";
    if($debug == "true") { 
        print "Command: ".$exec; 
    } else { 
        exec($exec);
        /* redirect to drop all the url parameters */
        header("Location: ".$conf['url_abs']);
        exit; 
    }
}

// volume up
if(isset($urlparams['volumeup'])) {
    $exec = "/usr/bin/sudo ".$conf['scripts_abs']."/playout_controls.sh -c=volumeup";
    if($debug == "true") { 
        print "Command: ".$exec; 
    } else { 
        exec($exec);
        /* redirect to drop all the url parameters */
        header("Location: ".$conf['url_abs']);
        exit; 
    }
}

// volume down
if(isset($urlparams['volumedown'])) {
    $exec = "/usr/bin/sudo ".$conf['scripts_abs']."/playout_controls.sh -c=volumedown";
    if($debug == "true") { 
        print "Command: ".$exec; 
    } else { 
        exec($exec);
        /* redirect to drop all the url parameters */
        header("Location: ".$conf['url_abs']);
        exit; 
    }
}

// reboot the jukebox
if(isset($urlparams['reboot']) && $urlparams['reboot'] == "true") {
    $exec = "/usr/bin/sudo ".$conf['scripts_abs']."/playout_controls.sh -c=reboot > /dev/null 2>&1 &";
    if($debug == "true") { 
        print "Command: ".$exec; 
    } else { 
        exec($exec);
        /* redirect to drop all the url parameters */
        header("Location: ".$conf['url_abs']);
        exit; 
    }
}

// shutdown the jukebox
if(isset($urlparams['shutdown']) && $urlparams['shutdown'] == "true") {
    $exec = "/usr/bin/sudo ".$conf['scripts_abs']."/playout_controls.sh -c=shutdown > /dev/null 2>&1 &";
    if($debug == "true") { 
        print "Command: ".$exec; 
    } else { 
        exec($exec);
        /* redirect to drop all the url parameters */
        header("Location: ".$conf['url_abs']);
        exit; 
    }
}

// set idletime
if(isset($urlparams['idletime'])) {
    $exec = "/usr/bin/sudo ".$conf['scripts_abs']."/playout_controls.sh -c=setidletime -v=".$urlparams['idletime'];
    if($debug == "true") { 
        print "Command: ".$exec; 
    } else { 
        exec($exec);
        /* redirect to drop all the url parameters */
        header("Location: ".$conf['url_abs']);
        exit; 
    }
}

// set shutdownafter time (sleeptimer)
if(isset($urlparams['shutdownafter'])) {
    $exec = "/usr/bin/sudo ".$conf['scripts_abs']."/playout_controls.sh -c=shutdownafter -v=".$urlparams['shutdownafter'];
    if($debug == "true") { 
        print "Command: ".$exec; 
    } else { 
        exec($exec);
        /* redirect to drop all the url parameters */
        header("Location: ".$conf['url_abs']);
        exit; 
    }
}

// start the rfid service
if(isset($urlparams['rfidstatus']) && $urlparams['rfidstatus'] == "turnon") {
    $exec = "/usr/bin/sudo /bin/systemctl start phoniebox-rfid-reader.service";
    if($debug == "true") { 
        print "Command: ".$exec; 
    } else { 
        exec($exec);
        /* redirect to drop all the url parameters */
        header("Location: ".$conf['url_abs']);
        exit; 
    }
}

// stop the rfid service
if(isset($urlparams['rfidstatus']) && $urlparams['rfidstatus'] == "turnoff") {
    $exec = "/usr/bin/sudo /bin/systemctl stop phoniebox-rfid-reader.service";
    if($debug == "true") { 
        print "Command: ".$exec; 
    } else { 
        exec($exec);
        /* redirect to drop all the url parameters */
        header("Location: ".$conf['url_abs']);
        exit; 
    }
}

// start the gpio button service
if(isset($urlparams['gpiostatus']) && $urlparams['gpiostatus'] == "turnon") {
    $exec = "/usr/bin/sudo /bin/systemctl start phoniebox-gpio-buttons.service";
    if($debug == "true") { 
        print "Command: ".$exec; 
    } else { 
        exec($exec);
        /* redirect to drop all the url parameters */
        header("Location: ".$conf['url_abs']);
        exit; 
    }
}

// stop the gpio button service
if(isset($urlparams['gpiostatus']) && $urlparams['gpiostatus'] == "turnoff") {
    $exec = "/usr/bin/sudo /bin/systemctl stop phoniebox-gpio-buttons.service";
    if($debug == "true") { 
        print "Command: ".$exec; 
    } else { 
        exec($exec);
        /* redirect to drop all the url parameters */
        header("Location: ".$conf['url_abs']);
        exit; 
    }
}

// enable resume
if(isset($urlparams['enableresume']) && $urlparams['enableresume'] != "" && is_dir(urldecode($Audio_Folders_Path."/".$urlparams['enableresume']))) {
    if($debug == "true") { 
        print "Command: ".$exec; 
    } else { 
    // pass folder to resume script
    // escape whitespaces with backslashes
    // SC added the following lines to make resume work again, changes affect the folder_string $urlparams['enableresume']
    // Note: This will allow normal function of the resume button in the webinterface for folder s with brackets in their name.
    // Brackets of type "(", ")", "[", "]" are supported as album names often apear in form of "albumname - (year) - albumtitle"
    if($debug == "true") { 
        print "original_enableresume=".$urlparams['enableresume'] . PHP_EOL;
    }
    $modified_enableresume = preg_replace('/\s+/', '\ ',$urlparams['enableresume']); // replace whitespaces with " "
    $modified_enableresume = preg_replace('/\(/', '\(',$modified_enableresume); // replace "(" with with "\("
    $modified_enableresume = preg_replace('/\)/', '\)',$modified_enableresume); // replace "(" with with "\)"
    $modified_enableresume = preg_replace('/\[/', '\[',$modified_enableresume); // replace "(" with with "\["
    $modified_enableresume = preg_replace('/\]/', '\]',$modified_enableresume); // replace "(" with with "\]"
    if($debug == "true") { 
        print "modified_enableresume=".$modified_enableresume . PHP_EOL; 
    }
    $exec = "/usr/bin/sudo ".$conf['scripts_abs']."/resume_play.sh -c=enableresume -d=".$modified_enableresume; // new and modified call of resume_play.sh
    //$exec = "/usr/bin/sudo ".$conf['scripts_abs']."/resume_play.sh -c=enableresume -d=".preg_replace('/\s+/', '\ ',$urlparams['enableresume']); // original call of resume_play.sh
    exec($exec);

    /* redirect to drop all the url parameters */
    header("Location: ".$conf['url_abs']);
    exit; 
    }
}

// disable resume
if(isset($urlparams['disableresume']) && $urlparams['disableresume'] != "" && is_dir($Audio_Folders_Path."/".urldecode($urlparams['disableresume']))) {
    // pass folder to resume script
    // escape whitespaces with backslashes
    // SC added the following lines to make resume work again, changes affect the folder_string $urlparams['enableresume']
    // Note: This will allow normal function of the resume button in the webinterface for folder s with brackets in their name.
    // Brackets of type "(", ")", "[", "]" are supported as album names often apear in form of "albumname - (year) - albumtitle"
    $modified_disableresume = preg_replace('/\s+/', '\ ',$urlparams['disableresume']); // replace whitespaces with " "
    $modified_disableresume = preg_replace('/\(/', '\(',$modified_disableresume); // replace "(" with with "\("
    $modified_disableresume = preg_replace('/\)/', '\)',$modified_disableresume); // replace "(" with with "\)"
    $modified_disableresume = preg_replace('/\[/', '\[',$modified_disableresume); // replace "(" with with "\["
    $modified_disableresume = preg_replace('/\]/', '\]',$modified_disableresume); // replace "(" with with "\]"
    $exec = "/usr/bin/sudo ".$conf['scripts_abs']."/resume_play.sh -c=disableresume -d=".$modified_disableresume; // new and modified call of resume_play.sh
    //$exec = "/usr/bin/sudo ".$conf['scripts_abs']."/resume_play.sh -c=disableresume -d=".preg_replace('/\s+/', '\ ',$urlparams['disableresume']); // original call of resume_play.sh
    if($debug == "true") { 
        print "Command: ".$exec; 
    } else { 
        exec($exec);
        /* redirect to drop all the url parameters */
        header("Location: ".$conf['url_abs']);
        exit; 
    }
}

// enable shuffle
if(isset($urlparams['enableshuffle']) && $urlparams['enableshuffle'] != "" && is_dir(urldecode($Audio_Folders_Path."/".$urlparams['enableshuffle']))) {
    // pass folder to resume script
    // escape whitespaces with backslashes
    $exec = "/usr/bin/sudo ".$conf['scripts_abs']."/shuffle_play.sh -c=enableshuffle -d=".preg_replace('/\s+/', '\ ',$urlparams['enableshuffle']);

    if($debug == "true") { 
        print "Command: ".$exec; 
    } else { 
        exec($exec);
        /* redirect to drop all the url parameters */
        header("Location: ".$conf['url_abs']);
        exit; 
    }
}

// disable shuffle
if(isset($urlparams['disableshuffle']) && $urlparams['disableshuffle'] != "" && is_dir(urldecode($Audio_Folders_Path."/".$urlparams['disableshuffle']))) {
    // pass folder to resume script
    // escape whitespaces with backslashes
    $exec = "/usr/bin/sudo ".$conf['scripts_abs']."/shuffle_play.sh -c=disableshuffle -d=".preg_replace('/\s+/', '\ ',$urlparams['disableshuffle']);
    if($debug == "true") { 
        print "Command: ".$exec; 
    } else { 
    exec($exec);

    /* redirect to drop all the url parameters */
    header("Location: ".$conf['url_abs']);
    exit; 
    }
}

// scan the library
if(isset($urlparams['scan']) && $urlparams['scan'] == "true") {
    $exec = "/usr/bin/sudo ".$conf['scripts_abs']."/playout_controls.sh -c=scan > /dev/null 2>&1 &";
    if($debug == "true") { 
        print "Command: ".$exec; 
    } else { 
        exec($exec);
        /* redirect to drop all the url parameters */
        header("Location: ".$conf['url_abs']);
        exit; 
    }
}


// stop playing
if(isset($urlparams['stop']) && $urlparams['stop'] == "true") {
    $exec = "/usr/bin/sudo ".$conf['scripts_abs']."/playout_controls.sh -c=playerstop";
    if($debug == "true") { 
        print "Command: ".$exec; 
    } else { 
        exec($exec);
        /* redirect to drop all the url parameters */
        header("Location: ".$conf['url_abs']);
        exit; 
    }
}

// play folder audio files
if(isset($urlparams['play']) && $urlparams['play'] != "" && is_dir(urldecode($Audio_Folders_Path."/".$urlparams['play']))) {
    // pass folder to playout script
    // escape whitespaces with backslashes
    #$exec = '/usr/bin/sudo '.$conf['scripts_abs'].'/rfid_trigger_play.sh -d="'.preg_replace('/\s+/', '\ ',$urlparams['play']).'"';
    $exec = '/usr/bin/sudo '.$conf['scripts_abs'].'/rfid_trigger_play.sh -d="'.$urlparams['play'].'"';
    if($urlparams['recursive'] == "true") {
        $exec .= ' -v="recursive"';
    }
    if($debug == "true") { 
        print "Command: ".$exec; 
    } else { 
        exec($exec);
        /* redirect to drop all the url parameters */
        header("Location: ".$conf['url_abs']);
        exit; 
    }
}

// play from playlist position
if(isset($urlparams['playpos'])) {
    $exec = "/usr/bin/sudo ".$conf['scripts_abs']."/playout_controls.sh -c=playerplay -v=".$urlparams['playpos'];
    if($debug == "true") { 
        print "Command: ".$exec; 
    } else { 
        exec($exec);
        /* redirect to drop all the url parameters */
        header("Location: ".$conf['url_abs']);
        exit; 
    }
}


// control player through web interface
if(isset($urlparams['player'])) {
    if($urlparams['player'] == "next") {
        $exec = "/usr/bin/sudo ".$conf['scripts_abs']."/playout_controls.sh -c=playernext";
        if($debug == "true") { 
            print "Command: ".$exec; 
        } else { 
            exec($exec);
            /* redirect to drop all the url parameters */
            header("Location: ".$conf['url_abs']);
            exit; 
        }
    }
    if($urlparams['player'] == "prev") {
        $exec = "/usr/bin/sudo ".$conf['scripts_abs']."/playout_controls.sh -c=playerprev";
        if($debug == "true") { 
            print "Command: ".$exec; 
        } else { 
            exec($exec);
            /* redirect to drop all the url parameters */
            header("Location: ".$conf['url_abs']);
            exit; 
        }
    }
    if($urlparams['player'] == "play") {
        $exec = "/usr/bin/sudo ".$conf['scripts_abs']."/playout_controls.sh -c=playerplay";
        if($debug == "true") { 
            print "Command: ".$exec; 
        } else { 
            exec($exec);
            /* redirect to drop all the url parameters */
            header("Location: ".$conf['url_abs']);
            exit; 
        }
    }
    if($urlparams['player'] == "replay") {
        $exec = "/usr/bin/sudo ".$conf['scripts_abs']."/playout_controls.sh -c=playerreplay";
        if($debug == "true") { 
            print "Command: ".$exec; 
        } else { 
            exec($exec);
            /* redirect to drop all the url parameters */
            header("Location: ".$conf['url_abs']);
            exit; 
        }
    }
    if($urlparams['player'] == "pause") {
        $exec = "/usr/bin/sudo ".$conf['scripts_abs']."/playout_controls.sh -c=playerpause";
        if($debug == "true") { 
            print "Command: ".$exec; 
        } else { 
            exec($exec);
            /* redirect to drop all the url parameters */
            header("Location: ".$conf['url_abs']);
            exit; 
        }
    }
    if($urlparams['player'] == "repeat") {
        $exec = "/usr/bin/sudo ".$conf['scripts_abs']."/playout_controls.sh -c=playerrepeat -v=playlist";
        if($debug == "true") { 
            print "Command: ".$exec; 
        } else { 
            exec($exec);
            /* redirect to drop all the url parameters */
            header("Location: ".$conf['url_abs']);
            exit; 
        }
    }
    if($urlparams['player'] == "single") {
        $exec = "/usr/bin/sudo ".$conf['scripts_abs']."/playout_controls.sh -c=playerrepeat -v=single";
        if($debug == "true") { 
            print "Command: ".$exec; 
        } else { 
            exec($exec);
            /* redirect to drop all the url parameters */
            header("Location: ".$conf['url_abs']);
            exit; 
        }
    }
    if($urlparams['player'] == "repeatoff") {
        $exec = "/usr/bin/sudo ".$conf['scripts_abs']."/playout_controls.sh -c=playerrepeat -v=off";
        if($debug == "true") { 
            print "Command: ".$exec; 
        } else { 
            exec($exec);
            /* redirect to drop all the url parameters */
            header("Location: ".$conf['url_abs']);
            exit; 
        }
    }
    if($urlparams['player'] == "seekBack") {
        $exec = "/usr/bin/sudo ".$conf['scripts_abs']."/playout_controls.sh -c=playerseek -v=-15";
        if($debug == "true") { 
            print "Command: ".$exec; 
        } else { 
            exec($exec);
            /* redirect to drop all the url parameters */
            header("Location: ".$conf['url_abs']);
            exit; 
        }
    }
    if($urlparams['player'] == "seekAhead") {
        $exec = "/usr/bin/sudo ".$conf['scripts_abs']."/playout_controls.sh -c=playerseek -v=+15";
        if($debug == "true") { 
            print "Command: ".$exec; 
        } else { 
            exec($exec);
            /* redirect to drop all the url parameters */
            header("Location: ".$conf['url_abs']);
            exit; 
        }
    }
}
?>
