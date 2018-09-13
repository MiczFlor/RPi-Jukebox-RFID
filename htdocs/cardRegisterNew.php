<?php

include("inc.header.php");

/**************************************************
* VARIABLES
* No changes required if you stuck to the
* INSTALL-stretch.md instructions.
* If you want to change the paths, edit config.php
* If you want to change the paths, edit config.php
***************************************************/

/* NO CHANGES BENEATH THIS LINE ***********/

$conf['url_abs']    = "http://".$_SERVER['HTTP_HOST'].$_SERVER['PHP_SELF']; // URL to PHP_SELF

/*******************************************
* START HTML
*******************************************/

html_bootstrap3_createHeader("en","RPi Jukebox",$conf['base_url']);

?>
<body>
  <div class="container">
      
<?php
include("inc.navigation.php");

// path to script folder from github repo on RPi
$conf['shared_abs'] = realpath(getcwd().'/../shared/');

/*******************************************
* URLPARAMETERS
*******************************************/
if(isset($_POST['cardID']) && $_POST['cardID'] != "") { // && file_exists('../shared/shortcuts/'.$_POST['cardID'])) {
    $post['cardID'] = $_POST['cardID'];
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

/*******************************************
* ACTIONS
*******************************************/
$messageAction = "";
$messageSuccess = "";
if($post['submit'] == "submit") {
    /*
    * error check
    */
    // The dropdown menus for the audiofolders in the section "Audio folders" and "YouTube" are interchangeable.
    // So you may select the folder in any of both.
    // Check if two different audiofolders are selectied in the dropdowns
    if(isset($post['audiofolder']) && isset($post['YTaudiofolder'])) {
        $messageAction .= $lang['cardRegisterErrorTooMuch'];
    } elseif(!isset($post['audiofolder']) && isset($post['YTaudiofolder'])) {
        //set the audiofolder variable (if unset) to the YTaudiofolder variable. This makes the further handling easier.
        $post['audiofolder'] = $post['YTaudiofolder'];
    }
    // Like above: stream folder inputs are interchangeable.
    // Check if two different stream folder names are entered
    if(isset($post['streamFolderName']) && isset($post['YTstreamFolderName']) && $post['streamFolderName'] != $post['YTstreamFolderName']) {
        $messageAction .= $lang['cardRegisterErrorTooMuch'];
    } elseif(!isset($post['streamFolderName']) && isset($post['YTstreamFolderName'])) {
        //set the streamFolderName variable (if unset) to the YTstreamFolderName variable. This makes the further handling easier.
        $post['streamFolderName'] = $post['YTstreamFolderName'];
    }

    // posted too much?
    if(isset($post['streamURL']) && isset($post['audiofolder'])) {
        $messageAction .= $lang['cardRegisterErrorStreamAndAudio'];
    }
    
    // posted too little?
    if(!isset($post['streamURL']) && !isset($post['audiofolder']) && !isset($post['YTstreamURL'])) {
        $messageAction .= $lang['cardRegisterErrorStreamOrAudio'];
    }

    // posted streamFolderName and audiofolder
    if(isset($post['streamFolderName']) && isset($post['audiofolder'])) {
        $messageAction .= $lang['cardRegisterErrorExistingAndNew'];
    }
    
    // streamFolderName already exists
    if(isset($post['streamFolderName']) && file_exists($Audio_Folders_Path.'/'.$post['streamFolderName'])) {
        $messageAction .= $lang['cardRegisterErrorExistingFolder'];
    }
    
    // No streamFolderName entered
    if(isset($post['streamURL']) && !isset($post['streamFolderName'])) {
        $messageAction .= $lang['cardRegisterErrorSuggestFolder'];
        // get rid of strange chars, prefixes and the like
        $post['streamFolderName'] = $link = str_replace(array('http://','https://','/','=','-','.', 'www','?','&'), '', $post['streamURL']);
    }
    
    // streamFolderName not given
    if( ( isset($post['streamURL']) || isset($post['YTstreamURL']) ) && !isset($post['audiofolder']) && !isset($post['streamFolderName'])) {
        $messageAction .= $lang['cardRegisterErrorSuggestFolder'];
        // get rid of strange chars, prefixes and the like
        $post['streamFolderName'] = $link = str_replace(array('http://','https://','/','=','-','.', 'www','?','&'), '', $post['streamURL']);
    }
    
    /*
    * any errors?
    */
    if($messageAction == "") {
        /*
        * do what's asked of us
        */
        $fileshortcuts = $conf['shared_abs']."/shortcuts/".$post['cardID'];
        if(isset($post['streamURL'])) {
            /*
            * Stream URL to be created
            */
            include('inc.processAddNewStream.php');
            // success message
            $messageSuccess = "<p>".$lang['cardRegisterStream2Card']." ".$lang['globalFolder']." '".$post['streamFolderName']."' ".$lang['globalCardId']." '".$post['cardID']."'</p>";
        }
        elseif(isset($post['YTstreamURL'])) {
            /*
            * Stream URL to be created
            */
            include('inc.processAddYT.php');
            // success message
            $messageSuccess = $lang['cardRegisterDownloadingYT'];
        } else {
            /*
            * connect card with existing audio folder
            */
            // write $post['audiofolder'] to cardID file in shortcuts
            $exec = "rm ".$fileshortcuts."; echo '".$post['audiofolder']."' > ".$fileshortcuts."; chmod 777 ".$fileshortcuts;
            exec($exec);
            // success message
            $messageSuccess = "<p>".$lang['cardRegisterFolder2Card']."  ".$lang['globalFolder']." '".$post['audiofolder']."' ".$lang['globalCardId']." '".$post['cardID']."'</p>";
        }
    } else {
        /*
        * Warning given, action can not be taken
        */
    }
}

?>

    <div class="row playerControls">
      <div class="col-lg-12">
        <h1><?php print $lang['cardRegisterTitle']; ?></h1>
<?php
/*
* Do we need to voice a warning here?
*/
if ($messageAction == "") {
    $messageAction = $lang['cardRegisterMessageDefault'].$lang['cardRegisterManualLinks'];
} 
if(isset($messageSuccess) && $messageSuccess != "") {
    print '<div class="alert alert-success">'.$messageSuccess.'<p>'.$lang['cardRegisterMessageSwipeNew'].'</p></div>';
    unset($post);
} else {
    if(isset($warning)) {
        print '<div class="alert alert-warning">'.$warning.'</div>';
    }
    if(isset($messageAction)) {
        print '<div class="alert alert-info">'.$messageAction.'</div>';
    }
}


?>

<?php
if($debug == "true") {
    print "<pre>";
    print_r($_POST);
    print_r($conf);
    print "</pre>";
}
?>

       </div>
    </div>

    <div class="row">
      <div class="col-lg-12">
<?php
/*
* pass on some variables to the form.
* Doing this so I can reuse the form in other places to edit or register cards.
*/
$fdata = array(
    "streamURL_ajax" => "true",
    "streamURL_label" => $lang['globalLastUsedCard'],
    "streamURL_help" => $lang['cardRegisterSwipeUpdates'],
);
$fpost = $post;
include("inc.formCardEdit.php");
?>
      </div><!-- / .col-lg-12 -->
    </div><!-- /.row -->
  </div><!-- /.container -->

<script>
$(document).ready(function() {
    $('#refresh_id').load('ajax.refresh_id.php');
    var refreshId = setInterval(function() {
        $('#refresh_id').load('ajax.refresh_id.php?' + 1*new Date());
    }, 1000);
});

</script>  

</body>
</html>
