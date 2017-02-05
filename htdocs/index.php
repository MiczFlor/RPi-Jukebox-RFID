<?php

/*******************************************
* VARIABLES
* No changes required if you stuck to the
* INSTALL.md instructions.
*******************************************/
$conf = array();
$conf['base_url'] = "http://192.168.178.199/";
$conf['base_path'] = "/home/pi/RPi-Jukebox-RFID";
/*
$conf['base_url'] = "http://localhost/RPi-Jukebox-RFID/";
$conf['base_path'] = "/home/micz/Documents/github/RPi-Jukebox-RFID";
*/
/* NO CHANGES BENEATH THIS LINE ***********/

/*******************************************
* URLPARAMETERS
*******************************************/

$urlparams = array();

if(isset($_GET['play']) && trim($_GET['play']) != "") {
    $urlparams['play'] = trim($_GET['play']);
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

//print "<pre>"; print_r($urlparams); print "</pre>"; //???

/*******************************************
* ACTIONS
*******************************************/

// change volume
if(isset($urlparams['volume'])) {
    exec("/usr/bin/sudo amixer sset 'PCM' ".$urlparams['volume']."%");
}

// shutdown the jukebox
if(isset($urlparams['shutdown']) && $urlparams['shutdown'] == "true") {
    // NOTE: this is being done as sudo, because the webserver does not have the rights to kill VLC
    $exec = "/usr/bin/sudo halt";
    exec($exec);
}

// stop playing
if(isset($urlparams['stop']) && $urlparams['stop'] == "true") {
    // NOTE: this is being done as sudo, because the webserver does not have the rights to kill VLC
    $exec = "/usr/bin/sudo pkill vlc > /dev/null 2>/dev/null &";
    exec($exec);
}

// play folder with VLC
if(isset($urlparams['play']) && $urlparams['play'] != "" && is_dir($urlparams['play'])) {
    // kill vlc if running
    // NOTE: this is being done as sudo, because the webserver does not have the rights to kill VLC
    $exec = "/usr/bin/sudo pkill vlc > /dev/null 2>/dev/null &";
    exec($exec);

    // pipe playlist into VLC
    // NOTE: this is being done as sudo, because the webserver does not have the rights to start VLC
    $exec = "/usr/bin/sudo /usr/bin/cvlc ".$urlparams['play']." > /dev/null 2>/dev/null &";
    exec($exec);
}

/*******************************************
* START HTML
*******************************************/

html_bootstrap3_createHeader("en","RPi Jukebox",$conf['base_url']);

?>

<body>

  <div class="container">
      

<nav class="navbar navbar-default">
  <div class="container-fluid">
    <!-- Brand and toggle get grouped for better mobile display -->
    <div class="navbar-header">
      <button type="button" class="navbar-toggle collapsed" data-toggle="collapse" data-target="#bs-example-navbar-collapse-1" aria-expanded="false">
        <span class="sr-only">Toggle navigation</span>
        <span class="icon-bar"></span>
        <span class="icon-bar"></span>
        <span class="icon-bar"></span>
      </button>
      <a class="navbar-brand" href="index.php">Jukebox</a>
    </div>

    <!-- Collect the nav links, forms, and other content for toggling -->
    <div class="collapse navbar-collapse" id="bs-example-navbar-collapse-1">
      <ul class="nav navbar-nav">
        <li><a href='?stop=true' class='mainMenu'><i class='fa fa-stop'></i> Stop Player</a></li>
      </ul>
      
<!-- sub menu -->
      <ul class="nav navbar-nav navbar-right">
        <li><a href='?shutdown=true' class='mainMenu'><i class='fa fa-power-off'></i> Shutdown jukebox</a></li>
      </ul>
<!-- / sub menu -->
    </div><!-- /.navbar-collapse -->
  </div><!-- /.container-fluid -->
</nav>

    <div class="row">
      <div class="col-lg-12">
  <?php
  $volume = system("/usr/bin/sudo amixer get Master | awk '$0~/%/{print $4}' | tr -d '[]'");
  print $volume;
  ?>
  <div class="well">
      <h4>Volume</h4>

<form name='volume' method='post' action='<?php print $_SERVER['PHP_SELF']; ?>'>
Select volume: <select name='volume'>
     <option value='0'>Mute (0%)</option>
     <option value='30'>30%</option>
     <option value='50'>50%</option>
     <option value='75'>75%</option>
     <option value='85'>85%</option>
     <option value='90'>90%</option>
     <option value='95'>95%</option>
     <option value='100'>100%</option>
     </select>
<input type='submit' name='submit' value='Set volume'/>
</form>

  </div>
        
  <h2>Available audio</h2>
<?php

// read the subfolders of shared/audiofolders

$audiofolders = array_filter(glob($conf['base_path'].'/shared/audiofolders/*'), 'is_dir');
//print "<pre>"; print_r($audiofolders); print "</pre>"; // ???
// counter for ID of each folder
$idcounter = 0;

// go through all folders
foreach($audiofolders as $audiofolder) {
    
    // increase ID counter
    $idcounter++;
    
    // get list of content for each folder
    $files = scandir($audiofolder); 
    $accordion = "<h4>Contains the following file(s):</h4><ul>";
    foreach($files as $file) {
        if(is_file($audiofolder."/".$file)){
            $accordion .= "\n<li>".$file."</li>";
        }
    }
    $accordion .= "</ul>";
    // if folder not empty, display play button and content
    if ($accordion != "<h4>Contains the following file(s):</h4><ul></ul>") {
        print "
        <div class='well'>";
        // check if the file is playing => show 'stop'
        if($urlparams['play'] == $audiofolder) {
            print "
            <a href='?stop=true' class='btn btn-danger'><i class='fa fa-stop'></i> Stop</a>";
        } else {
            print "
            <a href='?play=".$audiofolder."' class='btn btn-success'><i class='fa fa-play'></i> Play</a>";
        }
        print "
            <span data-toggle='collapse' data-target='#folder".$idcounter."' class='btn btn-info'>Folder:
                ".str_replace($conf['base_path'].'/shared/audiofolders/', '', $audiofolder)."
                <i class='fa fa-info-circle'></i>
            </span>
            <div id='folder".$idcounter."' class='collapse'>
            ".$accordion."
            </div>
        </div>
        ";
    }
}





?>

      </div><!-- / .col-lg-12 -->
    </div><!-- /.row -->
  </div><!-- /.container -->

</body>
</html>
<?php

/*******************************************
* FUNCTIONS
*******************************************/

function html_bootstrap3_createHeader($lang="en",$title="Welcome",$url_absolute="") {
    /*
    * HTML for the header and body tag
    */
    print "<!DOCTYPE html>
<html lang=\"".$lang."\">
    <head>
        <meta charset=\"utf-8\">
        <meta http-equiv=\"X-UA-Compatible\" content=\"IE=edge\">
        <meta name=\"viewport\" content=\"width=device-width, initial-scale=1\">
        <!-- The above 3 meta tags *must* come first in the head; any other head content must come *after* these tags -->
        
        <title>".$title."</title>
        
        <!-- Latest compiled and minified CSS -->
        <link rel=\"stylesheet\" href=\"".$url_absolute."_assets/bootstrap-3/css/bootstrap.min.css\">
        
        <!-- Latest compiled and minified JavaScript -->
        <script src=\"".$url_absolute."_assets/js/jquery.1.12.4.min.js\"></script>
        <script src=\"".$url_absolute."_assets/bootstrap-3/js/bootstrap.min.js\"></script>

        <link rel='stylesheet' href='".$url_absolute."_assets/font-awesome/css/font-awesome.min.css'>
        
        <!-- HTML5 shim and Respond.js for IE8 support of HTML5 elements and media queries -->
        <!--[if lt IE 9]>
            <script src=\"".$url_absolute."_assets/bootstrap-3/js/html5shiv3.7.2.min.js\"></script>
            <script src=\"".$url_absolute."_assets/bootstrap-3/js/respond1.4.2.min.js\"></script>
        <![endif]-->
    </head>\n";
}

?>
