<?php

include("inc.header.php");

/**************************************************
* VARIABLES
* No changes required if you stuck to the
* INSTALL-stretch.md instructions.
* If you want to change the paths, edit config.php
***************************************************/

/* NO CHANGES BENEATH THIS LINE ***********/

$conf['url_abs']    = "http://".$_SERVER['HTTP_HOST'].$_SERVER['PHP_SELF']; // URL to PHP_SELF


/*******************************************
* START HTML
*******************************************/

html_bootstrap3_createHeader("en","Phoniebox",$conf['base_url']);

?>
<body>
  <div class="container">
      
<?php
include("inc.navigation.php");

// path to shared folder from github repo on RPi
$conf['shared_abs'] = realpath(getcwd().'/../shared/');

/*******************************************
* URLPARAMETERS
*******************************************/
if(isset($_GET['cardID']) && $_GET['cardID'] != "") { // && file_exists('../shared/shortcuts/'.$_POST['cardID'])) {
    $post['cardID'] = $_GET['cardID'];
} else {
    if(isset($_POST['cardID']) && $_POST['cardID'] != "") { // && file_exists('../shared/shortcuts/'.$_POST['cardID'])) {
        $post['cardID'] = $_POST['cardID'];
    }
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
if(isset($_POST['submit']) && $_POST['submit'] == "submit") {
    $post['submit'] = $_POST['submit'];
}
if(isset($_POST['delete']) && $_POST['delete'] == "delete") {
    $post['delete'] = $_POST['delete'];
}
$fileshortcuts = $conf['shared_abs']."/shortcuts/".$post['cardID'];

/*******************************************
* ACTIONS
*******************************************/
$messageAction = "";
$messageSuccess = "";

if($post['delete'] == "delete") {
    $messageAction .= "<p>The card with the ID '".$post['cardID']." has been deleted. 
        If you made a mistake, this is your chance to press 'Submit' to restore the card settings. 
        Else: Go <a href='index.php' class='mainMenu'><i class='mdi mdi-home'></i> Home</a>.</p>";
    // remove $fileshortcuts to cardID file in shortcuts
    $exec = "rm ".$fileshortcuts;
    exec($exec);
} elseif($post['submit'] == "submit") {
    /*
    * error check
    */
    
    // posted too much?
    if(isset($post['streamURL']) && isset($post['audiofolder'])) {
        $messageAction .= $lang['cardRegisterErrorStreamAndAudio'];
    }
    
    // posted too little?
    if(!isset($post['streamURL']) && !isset($post['audiofolder'])) {
        $messageAction .= $lang['cardRegisterErrorStreamOrAudio'];
    }
    
    // streamFolderName already exists
    if(isset($post['streamFolderName']) && file_exists($Audio_Folders_Path.'/'.$post['streamFolderName'])) {
        $messageAction .= $lang['cardRegisterErrorExistingFolder'];
    }
    
    // streamFolderName already exists
    if(isset($post['streamURL']) && !isset($post['streamFolderName'])) {
        $messageAction .= $lang['cardRegisterErrorSuggestFolder'];
        // get rid of strange chars, prefixes and the like
        $post['streamFolderName'] = $link = str_replace(array('http://','https://','/','=','-','.', 'www','?','&'), '', $post['streamURL']);
    }
    
    // streamFolderName not given
    if(isset($post['streamURL']) && !isset($post['audiofolder']) && !isset($post['streamFolderName'])) {
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
        if(isset($post['streamURL'])) {
            /*
            * Stream URL to be created
            */
            include('inc.processAddNewStream.php');
            // success message
            $messageSuccess = "<p>".$lang['cardRegisterStream2Card']." ".$lang['globalFolder']." '".$post['streamFolderName']."' ".$lang['globalCardId']." '".$post['cardID']."'</p>";
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
        <h1><?php print $lang['cardEditTitle']; ?></h1>
<?php
/*
* Do we need to voice a warning here?
*/
if ($messageAction == "") {
    $messageAction = $lang['cardEditMessageDefault'];
} 
if(isset($messageSuccess) && $messageSuccess != "") {
    print '<div class="alert alert-success">'.$messageSuccess.'<p>'.$lang['cardEditMessageInputNew'].'</p></div>';
    //unset($post);
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
    "streamURL_ajax" => "false",
    "streamURL_label" => $lang['globalCardId'],
    "streamURL_placeholder" => $lang['globalCardIdPlaceholder'],
    "streamURL_help" => $lang['globalCardIdHelp'],
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
