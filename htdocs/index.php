<?php

/**************************************************
* VARIABLES
* No changes required if you stuck to the
* INSTALL.md instructions.
* If you want to change the paths, edit config.php
***************************************************/

/*
* DEBUGGING
* for debugging, set following var to true.
* This will only print the executable strings, not execute them
*/
$debug = "false"; // true or false

/* NO CHANGES BENEATH THIS LINE ***********/

include("config.php");

$conf['url_abs']    = "http://".$_SERVER['HTTP_HOST'].$_SERVER['PHP_SELF']; // URL to PHP_SELF

include("func.php");

// path to script folder from github repo on RPi
$conf['scripts_abs'] = realpath(getcwd().'/../scripts/');

/*******************************************
* URLPARAMETERS
*******************************************/

$urlparams = array();

if(isset($_GET['play']) && trim($_GET['play']) != "") {
    $urlparams['play'] = trim($_GET['play']);
}

if(isset($_GET['player']) && trim($_GET['player']) != "") {
    $urlparams['player'] = trim($_GET['player']);
}

if(isset($_GET['stop']) && trim($_GET['stop']) != "") {
    $urlparams['stop'] = trim($_GET['stop']);
}

if(isset($_POST['volume']) && trim($_POST['volume']) != "") {
    $urlparams['volume'] = trim($_POST['volume']);
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
    $exec = "/usr/bin/sudo ".$conf['scripts_abs']."/playout_controls.sh -c=reboot";
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
    $exec = "/usr/bin/sudo ".$conf['scripts_abs']."/playout_controls.sh -c=shutdown";
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

// play folder with VLC
if(isset($urlparams['play']) && $urlparams['play'] != "" && is_dir(urldecode($urlparams['play']))) {
    // kill vlc if running
    // NOTE: this is being done as sudo, because the webserver does not have the rights to kill VLC
    $exec = "/usr/bin/sudo pkill vlc > /dev/null 2>/dev/null";
    exec($exec);

    // pipe playlist into VLC
    // NOTE: this is being done as sudo, because the webserver does not have the rights to start VLC
    $exec = "/usr/bin/sudo /usr/bin/cvlc --no-video -I rc --rc-host localhost:4212 '".urldecode($urlparams['play'])."' > /dev/null 2>/dev/null &";
    exec($exec);
    /* redirect to drop all the url parameters */
    header("Location: ".$conf['url_abs']);
    exit; 
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
}

/*******************************************
* START HTML
*******************************************/

html_bootstrap3_createHeader("en","RPi Jukebox",$conf['base_url']);

include("page_home.php");

?>



      </div><!-- / .col-lg-12 -->
    </div><!-- /.row -->
  </div><!-- /.container -->

</body>
</html>
