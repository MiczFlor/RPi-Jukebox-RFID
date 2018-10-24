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

html_bootstrap3_createHeader("en","Phoniebox",$conf['base_url']);

?>
<body>
  <div class="container">
      
<?php
include("inc.navigation.php");

// path to script folder from github repo on RPi
$conf['shared_abs'] = realpath(getcwd().'/../shared/');

/*******************************************
* ACTIONS
*******************************************/
include("inc.processCheckCardEditRegister.php");

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
    print_r($post);
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
