<?php
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
        <li><a href='index.php' class='mainMenu'><i class='fa fa-refresh'></i> Reload page</a></li>
      </ul>
      
<!-- sub menu -->
      <ul class="nav navbar-nav navbar-right">
        <li><a href='?shutdown=true' class='mainMenu'><i class='fa fa-power-off'></i> Shutdown jukebox</a></li>
        <li><a href='?reboot=true' class='mainMenu'><i class='fa fa-refresh'></i> Reboot jukebox</a></li>
      </ul>
<!-- / sub menu -->
    </div><!-- /.navbar-collapse -->
  </div><!-- /.container-fluid -->
</nav>
    <div class="row">
      <div class="col-lg-12">

        <div class="btn-group" role="group" aria-label="player">
          <a href='?player=prev' class='btn btn-default btn-success'><i class='fa  fa-step-backward'></i></a>
          <a href='?player=pause' class='btn btn-default btn-success'><i class='fa  fa-pause'></i></a>
          <a href='?player=play' class='btn btn-default btn-success'><i class='fa fa-play'></i></a>
          <a href='?player=replay' class='btn btn-default btn-success'><i class='fa fa-refresh'></i></a>
          <a href='?stop=true' class='btn btn-default btn-success'><i class='fa fa-stop'></i></a>
          <a href='?player=next' class='btn btn-default btn-success'><i class='fa  fa-step-forward'></i></a>
         </div>&nbsp;
        <div class="btn-group" role="group" aria-label="volume">
                <a href='?volumedown=true' class='btn btn-default btn-primary'><i class='fa  fa-volume-down'></i></a>
                <a href='?volumeup=true' class='btn btn-default btn-primary'><i class='fa  fa-volume-up'></i></a>
         </div>
       <p>&nbsp;</p>
       </div>
    </div>

    <div class="row">
      <div class="col-lg-6">
              <h4>Volume</h4>
        
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
        <div class="col-lg-6">
              <h4>Manage Files and Chips</h4>
              <!-- Button trigger modal -->
                <button type="button" class="btn btn-primary btn" data-toggle="modal" data-target="#myModal">
                <i class='fa  fa-info'></i> Chip ID
                </button>
        </div>
    </div>

    <div class="row">
      <div class="col-lg-12">
        
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
usort($audiofolders, 'strcasecmp');

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
        print "
            <span data-toggle='collapse' data-target='#folder".$idcounter."' class='btn btn-info'>Folder:
                ".str_replace($conf['base_path'].'/shared/audiofolders/', '', $audiofolder)."
                <i class='fa fa-info-circle'></i>
            </span>
            <div id='folder".$idcounter."' class='collapse'>
            ".$accordion."
            </div>
        ";
        // print ID if any found
        if($ids != "") {
            print "
            <br/>Card ID: ".$ids;
        }
        print "
        </div>
        ";
    }
}

?>
        </div>
    </div>


<!-- Modal -->
<div class="modal fade" id="myModal" tabindex="-1" role="dialog" aria-labelledby="myModalLabel">
  <div class="modal-dialog" role="document">
    <div class="modal-content">
      <div class="modal-header">
        <button type="button" class="close" data-dismiss="modal" aria-label="Close"><span aria-hidden="true">&times;</span></button>
        <h4 class="modal-title" id="myModalLabel">Last used Chip ID</h4>
      </div>
      <div class="modal-body">
<pre>
<?php
print file_get_contents($conf['base_path'].'/shared/latestID.txt', true);
?>
</pre>
      </div>
      <div class="modal-footer">
        <button type="button" class="btn btn-default" data-dismiss="modal">Close</button>
      </div>
    </div>
  </div>
</div>
