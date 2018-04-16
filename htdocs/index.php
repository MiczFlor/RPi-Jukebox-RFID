<?php

/**************************************************
* VARIABLES
* No changes required if you stuck to the
* INSTALL.md instructions.
* If you want to change the paths, edit config.php
***************************************************/

/* NO CHANGES BENEATH THIS LINE ***********/

include("config.php");

$conf['url_abs']    = "http://".$_SERVER['HTTP_HOST'].$_SERVER['PHP_SELF']; // URL to PHP_SELF

include("func.php");

/*******************************************
* URLPARAMETERS
*******************************************/
$scripts = getcwd().'../scripts/';

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

if(isset($_GET['shutdown']) && trim($_GET['shutdown']) != "") {
    $urlparams['shutdown'] = trim($_GET['shutdown']);
}

if(isset($_GET['reboot']) && trim($_GET['reboot']) != "") {
    $urlparams['reboot'] = trim($_GET['reboot']);
}

/*
print "<pre>"; print_r($urlparams); print "</pre>"; //???
print "<pre>"; print_r($_SERVER); print "</pre>"; //???
print "<pre><a href='".$conf['url_abs']."'>".$conf['url_abs']."</a></pre>"; //???
*/

/*******************************************
* ACTIONS
*******************************************/

// change volume
if(isset($urlparams['volume'])) {
    exec($scripts."volume_set.sh ".$urlparams['volume']);
    /* redirect to drop all the url parameters */
    header("Location: ".$conf['url_abs']);
    exit;
}

// reboot the jukebox
if(isset($urlparams['reboot']) && $urlparams['reboot'] == "true") {
    // NOTE: this is being done as sudo, because the webserver does not have the rights to kill VLC
    $exec = $scripts."reboot.sh";
    exec($exec);
    /* redirect to drop all the url parameters */
    header("Location: ".$conf['url_abs']);
    exit;
}

// shutdown the jukebox
if(isset($urlparams['shutdown']) && $urlparams['shutdown'] == "true") {
    // NOTE: this is being done as sudo, because the webserver does not have the rights to kill VLC
    $exec = $scripts."shutdown.sh";
    exec($exec);
    /* redirect to drop all the url parameters */
    header("Location: ".$conf['url_abs']);
    exit;
}

// stop playing
if(isset($urlparams['stop']) && $urlparams['stop'] == "true") {
    // NOTE: this is being done as sudo, because the webserver does not have the rights to kill VLC
    $exec = "/usr/bin/sudo pkill vlc > /dev/null 2>/dev/null";
    exec($exec);
    /* redirect to drop all the url parameters */
    header("Location: ".$conf['url_abs']);
    exit;
}

// play folder
if(isset($urlparams['play']) && $urlparams['play'] != "" && is_dir(getcwd()."/../shared/audiofolders/".urldecode($urlparams['play']))) {
    $exec = $scripts."stop.sh";
    exec($exec);

    $exec = $scripts."play.sh '".urldecode($urlparams['play'])."'";
    exec($exec);
    /* redirect to drop all the url parameters */
    header("Location: ".$conf['url_abs']);
    exit;
}u
// control player through web interface
if(isset($urlparams['player'])) {
    if($urlparams['player'] == "next") {
        $exec = $scripts."next.sh";
        exec($exec);
        /* redirect to drop all the url parameters */
        header("Location: ".$conf['url_abs']);
        exit;
    }
    if($urlparams['player'] == "prev") {
        $exec = $scripts."prev.sh";
        exec($exec);
        /* redirect to drop all the url parameters */
        header("Location: ".$conf['url_abs']);
        exit;
    }
    if($urlparams['player'] == "play") {
        $exec = $scripts."play.sh";
        exec($exec);
        /* redirect to drop all the url parameters */
        header("Location: ".$conf['url_abs']);
        exit;
    }
    if($urlparams['player'] == "pause") {
        $exec = $scripts."pause.sh";
        exec($exec);
        /* redirect to drop all the url parameters */
        header("Location: ".$conf['url_abs']);
        exit;
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
