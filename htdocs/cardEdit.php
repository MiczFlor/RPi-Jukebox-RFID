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

$conf['url_abs']    = "http://".$_SERVER['HTTP_HOST'].$_SERVER['PHP_SELF']; // URL to PHP_SELF

include("func.php");

// path to script folder from github repo on RPi
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
if(isset($_POST['audiofolder']) && $_POST['audiofolder'] != "" && $_POST['audiofolder'] != "false" && file_exists('../shared/audiofolders/'.$_POST['audiofolder'])) {
    $post['audiofolder'] = $_POST['audiofolder'];
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
    
    // posted too much?
    if(isset($post['streamURL']) && isset($post['audiofolder'])) {
        $messageAction .= "<p>This is too much! Either a stream or an audio folder. Make up your mind.</p>";
    }
    
    // posted too little?
    if(!isset($post['streamURL']) && !isset($post['audiofolder'])) {
        $messageAction .= "<p>This is not enough! Add a stream or select an audio folder. Or 'Cancel' to go back to the home page.</p>";
    }
    
    // streamFolderName already exists
    if(isset($post['streamFolderName']) && file_exists('../shared/audiofolders/'.$post['streamFolderName'])) {
        $messageAction .= "<p>A folder named '".$post['streamFolderName']."' already exists! Chose a different one.</p>";
    }
    
    // streamFolderName already exists
    if(isset($post['streamURL']) && !isset($post['streamFolderName'])) {
        $messageAction .= "A folder name for the stream needs to be created. Below in the form I made a suggestion.";
        // get rid of strange chars, prefixes and the like
        $post['streamFolderName'] = $link = str_replace(array('http://','https://','/','=','-','.', 'www','?','&'), '', $post['streamURL']);
    }
    
    // streamFolderName not given
    if(isset($post['streamURL']) && !isset($post['audiofolder']) && !isset($post['streamFolderName'])) {
        $messageAction .= "<p>A folder name for the stream needs to be created. I'll make a suggestion.</p>";
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
            $messageSuccess = "<p>Stream inside folder '".$post['streamFolderName']."' is now linked to card ID '".$post['cardID']."'</p>";
        } else {
            /*
            * connect card with existing audio folder
            */
            // write $post['audiofolder'] to cardID file in shortcuts
            $exec = "rm ".$fileshortcuts."; echo '".$post['audiofolder']."' > ".$fileshortcuts."; chmod 777 ".$fileshortcuts;
            exec($exec);
            // success message
            $messageSuccess = "<p>Audio folder '".$post['audiofolder']."' is now linked to card ID '".$post['cardID']."'</p>";
        }
    } else {
        /*
        * Warning given, action can not be taken
        */
    }
}

/*******************************************
* START HTML
*******************************************/

html_bootstrap3_createHeader("en","RPi Jukebox",$conf['base_url']);

?>
<body>
  <div class="container">
      
<?php
include("inc.navigation.php");
?>

    <div class="row playerControls">
      <div class="col-lg-12">
        <h1>Edit or add card</h1>
<?php
/*
* Do we need to voice a warning here?
*/
if ($messageAction == "") {
    $messageAction = "The card IDs used in this system are listed on the <a href='index.php' class='mainMenu'><i class='fa fa-home'></i> home page</a>.";
} 
if(isset($messageSuccess) && $messageSuccess != "") {
    print '<div class="alert alert-success">'.$messageSuccess.'<p>Type another card ID pick one from the list on the <a href="index.php" class="mainMenu"><i class="fa fa-home"></i> home page</a>.</p></div>';
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
    "streamURL_ajax" => "false",
    "streamURL_label" => "Card ID",
    "streamURL_placeholder" => "e.g. '1234567890'",
    "streamURL_help" => "The ID is usually printed on the card or fob. A list of used IDs can be found on the home page.",
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
