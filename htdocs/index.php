<?php

/*******************************************
* VARIABLES
* No changes required if you stuck to the
* INSTALL.md instructions.
*******************************************/
$conf               = array();
$conf['base_url']   = "/"; // if root => "/", generally: try to end with trailing slash
$conf['base_path']  = "/home/pi/RPi-Jukebox-RFID"; // absolute path to folder
$conf['base_path']  = "/home/micz/Documents/github/RPi-Jukebox-RFID"; // absolute path to folder

/* NO CHANGES BENEATH THIS LINE ***********/

$conf['url_abs']    = "http://".$_SERVER['HTTP_HOST'].$_SERVER['PHP_SELF']; // URL to PHP_SELF

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
    exec("/usr/bin/sudo amixer sset 'PCM' ".$urlparams['volume']."%");
    /* redirect to drop all the url parameters */
    header("Location: ".$conf['url_abs']);
    exit; 
}

// reboot the jukebox
if(isset($urlparams['reboot']) && $urlparams['reboot'] == "true") {
    // NOTE: this is being done as sudo, because the webserver does not have the rights to kill VLC
    $exec = "/usr/bin/reboot";
    exec($exec);
    /* redirect to drop all the url parameters */
    header("Location: ".$conf['url_abs']);
    exit; 
}

// shutdown the jukebox
if(isset($urlparams['shutdown']) && $urlparams['shutdown'] == "true") {
    // NOTE: this is being done as sudo, because the webserver does not have the rights to kill VLC
    $exec = "/usr/bin/sudo halt";
    exec($exec);
    /* redirect to drop all the url parameters */
    header("Location: ".$conf['url_abs']);
    exit; 
}

// stop playing
if(isset($urlparams['stop']) && $urlparams['stop'] == "true") {
    // NOTE: this is being done as sudo, because the webserver does not have the rights to kill VLC
    $exec = "/usr/bin/sudo pkill vlc > /dev/null 2>/dev/null &";
    exec($exec);
    /* redirect to drop all the url parameters */
    header("Location: ".$conf['url_abs']);
    exit; 
}

// play folder with VLC
if(isset($urlparams['play']) && $urlparams['play'] != "" && is_dir($urlparams['play'])) {
    // kill vlc if running
    // NOTE: this is being done as sudo, because the webserver does not have the rights to kill VLC
    $exec = "/usr/bin/sudo pkill vlc > /dev/null 2>/dev/null &";
    exec($exec);

    // pipe playlist into VLC
    // NOTE: this is being done as sudo, because the webserver does not have the rights to start VLC
    $exec = "/usr/bin/sudo /usr/bin/cvlc -I rc --rc-host localhost:4212 ".$urlparams['play']." > /dev/null 2>/dev/null &";
    exec($exec);
    /* redirect to drop all the url parameters */
    header("Location: ".$conf['url_abs']);
    exit; 
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
        <li><a href='?restart=true' class='mainMenu'><i class='fa fa-refresh'></i> Reboot jukebox</a></li>
      </ul>
<!-- / sub menu -->
    </div><!-- /.navbar-collapse -->
  </div><!-- /.container-fluid -->
</nav>

    <div class="row">
      <div class="col-lg-12">
          <div class="well">
              <h4>Select Volume</h4>
        
                <form name='volume' method='post' action='<?php print $_SERVER['PHP_SELF']; ?>'>
                  <select name='volume'>
                     <option value='0'>Mute (0%)</option>
                     <option value='30'>30%</option>
                     <option value='50'>50%</option>
                     <option value='75'>75%</option>
                     <option value='80'>80%</option>
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

// read the shortcuts used
$shortcutstemp = array_filter(glob($conf['base_path'].'/shared/shortcuts/*'), 'is_file');
$shortcuts = array(); // the array with pairs of ID => foldername
// read files' content into array
foreach ($shortcutstemp as $shortcuttemp) {
    $shortcuts[basename($shortcuttemp)] = trim(file_get_contents($shortcuttemp));
}
//print "<pre>"; print_r($shortcutstemp); print "</pre>"; //???
//print "<pre>"; print_r($shortcuts); print "</pre>"; //???

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
    
    // get all IDs that match this folder
    $ids = ""; // print later
    $audiofolderbasename = trim(basename($audiofolder));
    if(in_array($audiofolderbasename, $shortcuts)) {
        foreach ($shortcuts as $key => $value) {
            if($value == $audiofolderbasename) {
                $ids .= $key.", ";
            }
        }
        $ids = rtrim($ids, ", "); // get rid of trailing slash
    }
    // if folder not empty, display play button and content
    if ($accordion != "<h4>Contains the following file(s):</h4><ul></ul>") {
        print "
        <div class='well'>
            <a href='?play=".$audiofolder."' class='btn btn-success'><i class='fa fa-play'></i> Play</a>";
        // print ID if any found
        if($ids != "") {
            print "
            (ID: ".$ids.")";
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
        
        <link rel=\"apple-touch-icon\" sizes=\"57x57\" href=\"".$url_absolute."_assets/icons/apple-icon-57x57.png\">
        <link rel=\"apple-touch-icon\" sizes=\"60x60\" href=\"".$url_absolute."_assets/icons/apple-icon-60x60.png\">
        <link rel=\"apple-touch-icon\" sizes=\"72x72\" href=\"".$url_absolute."_assets/icons/apple-icon-72x72.png\">
        <link rel=\"apple-touch-icon\" sizes=\"76x76\" href=\"".$url_absolute."_assets/icons/apple-icon-76x76.png\">
        <link rel=\"apple-touch-icon\" sizes=\"114x114\" href=\"".$url_absolute."_assets/icons/apple-icon-114x114.png\">
        <link rel=\"apple-touch-icon\" sizes=\"120x120\" href=\"".$url_absolute."_assets/icons/apple-icon-120x120.png\">
        <link rel=\"apple-touch-icon\" sizes=\"144x144\" href=\"".$url_absolute."_assets/icons/apple-icon-144x144.png\">
        <link rel=\"apple-touch-icon\" sizes=\"152x152\" href=\"".$url_absolute."_assets/icons/apple-icon-152x152.png\">
        <link rel=\"apple-touch-icon\" sizes=\"180x180\" href=\"".$url_absolute."_assets/icons/apple-icon-180x180.png\">
        <link rel=\"icon\" type=\"image/png\" sizes=\"192x192\"  href=\"".$url_absolute."_assets/icons/android-icon-192x192.png\">
        <link rel=\"icon\" type=\"image/png\" sizes=\"32x32\" href=\"".$url_absolute."_assets/icons/favicon-32x32.png\">
        <link rel=\"icon\" type=\"image/png\" sizes=\"96x96\" href=\"".$url_absolute."_assets/icons/favicon-96x96.png\">
        <link rel=\"icon\" type=\"image/png\" sizes=\"16x16\" href=\"".$url_absolute."_assets/icons/favicon-16x16.png\">
        <link rel=\"manifest\" href=\"".$url_absolute."_assets/icons/manifest.json\">
        <meta name=\"msapplication-TileColor\" content=\"#ffffff\">
        <meta name=\"msapplication-TileImage\" content=\"".$url_absolute."_assets/icons/ms-icon-144x144.png\">
        <meta name=\"theme-color\" content=\"#ffffff\">

    </head>\n";
}

?>
