<?php

include("inc.header.php");

/*******************************************
* START HTML
*******************************************/

html_bootstrap3_createHeader("en","RPi Jukebox",$conf['base_url']);

?>
<body>
  <div class="container">

<?php
include("inc.vlcStatus.php");
?>

<?php
include("inc.navigation.php");
?>

    <div class="row playerControls">
      <div class="col-lg-12">
<?php
/*
* Do we need to voice a warning here?
*/
if(isset($warning)) {
    print '<div class="alert alert-warning">'.$warning.'</div>';
}

include("inc.controlPlayer.php");

include("inc.controlVolumeUpDown.php");
?>

      </div><!-- / .col-lg-12 -->
    </div><!-- /.row -->

<?php
      // show currently played track
      if (array_key_exists('track', $playerStatus)) {
          $icon_class = ($playerStatus['status'] === 'play') ? 'play' : 'pause';
          print '
              <div class="well well-sm">
                  <div class="row">
                      <div class="col-lg-1 col-md-1 col-sm-1 col-xs-1">
                          <i class="fa fa-'. $icon_class .'"></i>
                      </div>
                      <div class="col-lg-11 col-md-11 col-sm-11 col-xs-11">
                          '.$playerStatus['track'].'
                      </div>
                  </div>
              </div>
          ';
      }
?>
<div class="row">
	<div class="col-xs-12">
		<h3>Volume</h3>
	</div>
</div>
<?php
include("inc.volumeSelect.php");
?>              
    <div class="row">
      <div class="col-lg-12">
        <h3>Manage Files and Chips</h3>
              <!-- Button trigger modal -->
                <a href="cardRegisterNew.php" class="btn btn-primary btn">
                <i class='fa  fa-plus-circle'></i> Register new card ID
                </a>
	</div><!-- / .col-lg-12 -->
    </div><!-- /.row -->

    <div class="row">
      <div class="col-lg-12">
        
  <h3>Available audio</h3>
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
	// add file name to list, supress if it's lastplayed.dat
        if(is_file($audiofolder."/".$file) && $file != "lastplayed.dat"){
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
                $ids .= " <a href='cardEdit.php?cardID=$key'>".$key." <i class='fa fa-wrench'></i></a> | ";
            }
        }
        $ids = rtrim($ids, "| "); // get rid of trailing slash
    }
    // if folder not empty, display play button and content
    if ($accordion != "<h4>Contains the following file(s):</h4><ul></ul>") {
        print "
        <div class='well'>";
        print "
            <h4><i class='fa fa-folder-o'></i>
                ".str_replace($conf['base_path'].'/shared/audiofolders/', '', $audiofolder)."
                </h4>";
        print "
            <a href='?play=".$audiofolder."' class='btn btn-info'><i class='fa fa-play'></i> Play</a> ";
        // Adds a button to enable/disable resume play. Checks if lastplayed.dat exists and livestream.txt not (no resume for livestreams)
        if (in_array("lastplayed.dat", $files) && ! in_array("livestream.txt", $files) ) {
            print "<a href='?disableresume=".$audiofolder."' class='btn btn-success '>Resume: ON <i class='fa fa-toggle-on' aria-hidden='true'></i></a>";
            //print "<span class='label label-success'>Resume play <i class='fa fa-toggle-on' aria-hidden='true'></i></span>";
            //$accordion .= "<a href='?disableresume=".$audiofolder."' class='btn btn-danger'><i class='fa fa-power-off'></i> Disable Resume</a>";
        }
        elseif ( ! in_array("livestream.txt", $files) ) {
            print "<a href='?enableresume=".$audiofolder."' class='btn btn-warning '>Resume: OFF <i class='fa fa-toggle-off' aria-hidden='true'></i></a> ";
            //$accordion .= "<a href='?enableresume=".$audiofolder."' class='btn btn-success'><i class='fa fa-play'></i> Enable Resume</a>";
        }
        print "
            <span data-toggle='collapse' data-target='#folder".$idcounter."' class='btn btnFolder'>Show files <i class='fa fa-folder-open-o'></i></span> ";
        print "
            <div id='folder".$idcounter."' class='collapse folderContent'>
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

      </div><!-- / .col-lg-12 -->
    </div><!-- /.row -->
    
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
    
        </div><!-- / .modal-content -->
      </div><!-- /.modal-dialog -->
    </div><!-- /.modal -->


  </div><!-- /.container -->

</body>
</html>
