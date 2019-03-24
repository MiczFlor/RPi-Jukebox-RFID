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

$url_abs = "http://".$_SERVER['HTTP_HOST'].$_SERVER['PHP_SELF']; // URL to PHP_SELF

/**
 * @param $exec
 */
function execAndRedirect($exec)
{
    global $debug;
    global $url_abs;

    if (!isset($exec)) {
        return;
    }

    if ($debug == "true") {
        print "Command: " . $exec;
    } else {
        exec($exec);
        /* redirect to drop all the url parameters */
        header("Location: " . $url_abs);
        exit;
    }
}

function fileGetContentOrDefault($filename, $defaultValue)
{
    return file_exists($filename) ? trim(file_get_contents($filename)) : $defaultValue;
}

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
$ShowCover = fileGetContentOrDefault($conf['settings_abs'].'/ShowCover', "ON");
$version = trim(file_get_contents($conf['settings_abs'].'/version'));
$edition = fileGetContentOrDefault(dirname(__FILE__).'/../settings/edition', "classic");
/*
* load language strings
*/
$conf['settings_lang'] = fileGetContentOrDefault($conf['settings_abs'].'/Lang', "en-UK");
include("inc.langLoad.php");

/*******************************************
* URLPARAMETERS
*******************************************/

$urlparams = array();
/*
* Firstly, collect via 'GET', later collect 'POST'
*/
$nonEmptyCommands = array(
    'play',
    'playpos',
    'player',
    'stop',
    'volume',
    'maxvolume',
    'volstep',
    'shutdown',
    'reboot',
    'scan',
    'idletime',
    'shutdownafter',
    'stopplayoutafter',
    'enableresume',
    'disableresume',
    'enableshuffle',
    'disableshuffle',
    'singleenable',
    'singledisable',
);
foreach ($nonEmptyCommands as $command) {
    if(isset($_GET[$command]) && trim($_GET[$command]) != "") {
        $urlparams[$command] = trim($_GET[$command]);
    }
    if(isset($_POST[$command]) && trim($_POST[$command]) != "") {
        $urlparams[$command] = trim($_POST[$command]);
    }
}

$commandsWithAllowedValues = array(
    'recursive' => array('true'),
    'mute' => array('true'),
    'volumeup' => array('true'),
    'volumedown' => array('true'),
    'rfidstatus' => array('turnon', 'turnoff'),
    'gpiostatus' => array('turnon', 'turnoff'),
);
foreach ($commandsWithAllowedValues as $command => $allowedValues) {
    if(isset($_GET[$command]) && in_array(trim($_GET[$command]), $allowedValues)) {
        $urlparams[$command] = trim($_GET[$command]);
    }
    if(isset($_POST[$command]) && in_array(trim($_POST[$command]), $allowedValues)) {
        $urlparams[$command] = trim($_POST[$command]);
    }
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

$commandToAction = array(
    'volume' => "/usr/bin/sudo ".$conf['scripts_abs']."/playout_controls.sh -c=setvolume -v=%s",            // change volume
    'maxvolume' => "/usr/bin/sudo ".$conf['scripts_abs']."/playout_controls.sh -c=setmaxvolume -v=%s",      // change max volume
    'volstep' => "/usr/bin/sudo ".$conf['scripts_abs']."/playout_controls.sh -c=setvolstep -v=%s",          // change volume step
    'mute' => "/usr/bin/sudo ".$conf['scripts_abs']."/playout_controls.sh -c=mute",                         // volume mute (toggle)
    'volumeup' => "/usr/bin/sudo ".$conf['scripts_abs']."/playout_controls.sh -c=volumeup",                 // volume up
    'volumedown' => "/usr/bin/sudo ".$conf['scripts_abs']."/playout_controls.sh -c=volumedown",             // volume down
    'idletime' => "/usr/bin/sudo ".$conf['scripts_abs']."/playout_controls.sh -c=setidletime -v=%s",        // set idletime
    'shutdownafter' => "/usr/bin/sudo ".$conf['scripts_abs']."/playout_controls.sh -c=shutdownafter -v=%s", // set shutdownafter time (sleeptimer)
    'stopplayoutafter' => "/usr/bin/sudo ".$conf['scripts_abs']."/playout_controls.sh -c=playerstopafter -v=%s",// set playerstopafter time (auto stop timer)
    'playpos' => "/usr/bin/sudo ".$conf['scripts_abs']."/playout_controls.sh -c=playerplay -v=%s",          // play from playlist position,
    'scan' => array(
        'true' => "/usr/bin/sudo ".$conf['scripts_abs']."/playout_controls.sh -c=scan > /dev/null 2>&1 &"   // scan the library
    ),
    'stop' => array(
        'true' => "/usr/bin/sudo ".$conf['scripts_abs']."/playout_controls.sh -c=playerstop"                // stop playing
    ),
    'reboot' => array(
        'true' => "/usr/bin/sudo ".$conf['scripts_abs']."/playout_controls.sh -c=reboot > /dev/null 2>&1 &" // reboot the jukebox
    ),
    'shutdown' => array(
        'true' => "/usr/bin/sudo ".$conf['scripts_abs']."/playout_controls.sh -c=shutdown > /dev/null 2>&1 &"// shutdown the jukebox
    ),
    'rfidstatus' => array(
        'turnon' => "/usr/bin/sudo /bin/systemctl start phoniebox-rfid-reader.service",                     // start the rfid service
        'turnoff' => "/usr/bin/sudo /bin/systemctl stop phoniebox-rfid-reader.service"                      // stop the rfid service
    ),
    'gpiostatus' => array(
        'turnon' => "/usr/bin/sudo /bin/systemctl start phoniebox-gpio-buttons.service",                    // start the gpio button service
        'turnoff' => "/usr/bin/sudo /bin/systemctl stop phoniebox-gpio-buttons.service"                     // stop the gpio button service
    ),
    // control player through web interface
    'player' => array(
        "next" => "/usr/bin/sudo " . $conf['scripts_abs'] . "/playout_controls.sh -c=playernext",
        "prev" => "/usr/bin/sudo " . $conf['scripts_abs'] . "/playout_controls.sh -c=playerprev",
        "play" => "/usr/bin/sudo " . $conf['scripts_abs'] . "/playout_controls.sh -c=playerplay",
        "replay" => "/usr/bin/sudo " . $conf['scripts_abs'] . "/playout_controls.sh -c=playerreplay",
        "pause" => "/usr/bin/sudo " . $conf['scripts_abs'] . "/playout_controls.sh -c=playerpause",
        "repeat" => "/usr/bin/sudo " . $conf['scripts_abs'] . "/playout_controls.sh -c=playerrepeat -v=playlist",
        "single" => "/usr/bin/sudo " . $conf['scripts_abs'] . "/playout_controls.sh -c=playerrepeat -v=single",
        "repeatoff" => "/usr/bin/sudo " . $conf['scripts_abs'] . "/playout_controls.sh -c=playerrepeat -v=off",
        "seekBack" => "/usr/bin/sudo " . $conf['scripts_abs'] . "/playout_controls.sh -c=playerseek -v=-15",
        "seekAhead" => "/usr/bin/sudo " . $conf['scripts_abs'] . "/playout_controls.sh -c=playerseek -v=+15",
    ),
);
foreach ($urlparams as $paramKey => $paramValue) {
    if(isset($commandToAction[$paramKey]) && !is_array($commandToAction[$paramKey])) {
        $exec = sprintf($commandToAction[$paramKey], $paramValue);
        execAndRedirect($exec);
    } elseif (isset($commandToAction[$paramKey]) && isset($commandToAction[$paramKey][$paramValue])) {
        $exec = sprintf($commandToAction[$paramKey][$paramValue], $paramValue);
        execAndRedirect($exec);
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
    header("Location: ".$url_abs);
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
    execAndRedirect($exec);
}

// enable shuffle
if(isset($urlparams['enableshuffle']) && $urlparams['enableshuffle'] != "" && is_dir(urldecode($Audio_Folders_Path."/".$urlparams['enableshuffle']))) {
    // pass folder to resume script
    // escape whitespaces with backslashes
    $exec = "/usr/bin/sudo ".$conf['scripts_abs']."/shuffle_play.sh -c=enableshuffle -d=".preg_replace('/\s+/', '\ ',$urlparams['enableshuffle']);

    execAndRedirect($exec);
}

// disable shuffle
if(isset($urlparams['disableshuffle']) && $urlparams['disableshuffle'] != "" && is_dir(urldecode($Audio_Folders_Path."/".$urlparams['disableshuffle']))) {
    // pass folder to resume script
    // escape whitespaces with backslashes
    $exec = "/usr/bin/sudo ".$conf['scripts_abs']."/shuffle_play.sh -c=disableshuffle -d=".preg_replace('/\s+/', '\ ',$urlparams['disableshuffle']);
    execAndRedirect($exec);
}

// enable single track play
if(isset($urlparams['singleenable']) && $urlparams['singleenable'] != "" && is_dir(urldecode($Audio_Folders_Path."/".$urlparams['singleenable']))) {
    // pass folder to single_play script
    // escape whitespaces with backslashes
    $exec = "/usr/bin/sudo ".$conf['scripts_abs']."/single_play.sh -c=singleenable -d=".preg_replace('/\s+/', '\ ',$urlparams['singleenable']);
    execAndRedirect($exec);
}

// disable single track play
if(isset($urlparams['singledisable']) && $urlparams['singledisable'] != "" && is_dir(urldecode($Audio_Folders_Path."/".$urlparams['singledisable']))) {
    // pass folder to single_play script
    // escape whitespaces with backslashes
    $exec = "/usr/bin/sudo ".$conf['scripts_abs']."/single_play.sh -c=singledisable -d=".preg_replace('/\s+/', '\ ',$urlparams['singledisable']);
    execAndRedirect($exec);
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
    execAndRedirect($exec);
}
?>
