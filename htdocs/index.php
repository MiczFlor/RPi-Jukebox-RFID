<?php

include("inc.header.php");

/*******************************************
* START HTML
*******************************************/

html_bootstrap3_createHeader("en","Phoniebox",$conf['base_url']);

?>
<body>
  <div class="container">

<?php
include("inc.playerStatus.php");
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

?>

      </div><!-- / .col-lg-12 -->
    </div><!-- /.row -->

<?php
// show currently played track

if (isset($playerStatus['file'])) {
    print '
    <div class="row">
        <div class="col-lg-12">';
            include("inc.loadedPlaylist.php");
    print '
        </div><!-- / .col-lg-12 -->
    </div><!-- /.row -->';
}
?>
    <div class="row">
      <div class="col-lg-12">
<?php
include("inc.setVolume.php");
?>      
    </div><!-- ./col-lg-12 -->
    </div><!-- ./row -->

    <div class="row">
      <div class="col-lg-12">
        <h3><?php print $lang['indexAvailAudio']; ?></h3>
      <div class="row">
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
    $accordion = "<h4>".$lang['indexContainsFiles']."</h4><ul>";
    foreach($files as $file) {
	// add file name to list, supress if it's lastplayed.dat
        if(is_file($audiofolder."/".$file) && $file != "lastplayed.dat"){
            $accordion .= "\n<li>".$file;
            $accordion .= " <a href='trackEdit.php?folder=$audiofolder&filename=$file'><i class='mdi mdi-wrench'></i> ".$lang['globalEdit']."</a>";
            $accordion .= "</li>";
        }
    }
    $accordion .= "</ul>";
    
    // get all IDs that match this folder
    $ids = ""; // print later
    $audiofolderbasename = trim(basename($audiofolder));
    if(in_array($audiofolderbasename, $shortcuts)) {
        foreach ($shortcuts as $key => $value) {
            if($value == $audiofolderbasename) {
                $ids .= " <a href='cardEdit.php?cardID=$key'>".$key." <i class='mdi mdi-wrench'></i></a> | ";
            }
        }
        $ids = rtrim($ids, "| "); // get rid of trailing slash
    }
    parse_str($conf['base_path'].'/shared/audiofolders/'.$audiofolder.'/folder.conf', $folderConf);
    $folderConfRaw = file_get_contents($audiofolder.'/folder.conf');
    // if folder not empty, display play button and content
    if ($accordion != "<h4>".$lang['indexContainsFiles']."</h4><ul></ul>") {
        print "
        <div class='col-md-6'>
        <div class='well'>";
        print "
            <h4><i class='mdi mdi-folder'></i>
                ".str_replace($conf['base_path'].'/shared/audiofolders/', '', $audiofolder)."
                </h4>";
        print "
            <a href='?play=".$audiofolder."' class='btn btn-info'><i class='mdi mdi-play'></i> ".$lang['globalPlay']."</a> ";
        // Adds a button to enable/disable resume play. Checks if lastplayed.dat exists and livestream.txt not (no resume for livestreams)

// RESUME BUTTON
// do not show any if there is a live stream in the folder
if (!in_array("livestream.txt", $files) ) {
    $foundResume = "OFF";
    if( file_exists($audiofolder."/folder.conf") && strpos(file_get_contents($audiofolder."/folder.conf"),'RESUME="ON"') !== false) {
        $foundResume = "ON";
    } else {
    }
}
if( $foundResume == "OFF" ) {
        // do stuff
            print "<a href='?enableresume=".$audiofolder."' class='btn btn-warning '>".$lang['globalResume'].": ".$lang['globalOff']." <i class='mdi mdi-toggle-switch-off-outline' aria-hidden='true'></i></a> ";
    } elseif($foundResume == "ON") {
            print "<a href='?disableresume=".$audiofolder."' class='btn btn-success '>".$lang['globalResume'].": ".$lang['globalOn']." <i class='mdi mdi-toggle-switch' aria-hidden='true'></i></a>";
}

// SHUFFLE BUTTON
// do not show any if there is a live stream in the folder
if (!in_array("livestream.txt", $files) ) {
    $foundShuffle = "OFF";
    if( file_exists($audiofolder."/folder.conf") && strpos(file_get_contents($audiofolder."/folder.conf"),'SHUFFLE="ON"') !== false) {
        $foundShuffle = "ON";
    }
}
if( $foundShuffle == "OFF" ) {
        // do stuff
            print "<a href='?enableshuffle=".$audiofolder."' class='btn btn-warning '>".$lang['globalShuffle'].": ".$lang['globalOff']." <i class='mdi mdi-toggle-switch-off-outline' aria-hidden='true'></i></a> ";
    } elseif($foundShuffle == "ON") {
            print "<a href='?disableshuffle=".$audiofolder."' class='btn btn-success '>".$lang['globalShuffle'].": ".$lang['globalOn']." <i class='mdi mdi-toggle-switch' aria-hidden='true'></i></a>";
}


        print "
            <span data-toggle='collapse' data-target='#folder".$idcounter."' class='btn btnFolder'>".$lang['indexShowFiles']." <i class='mdi mdi-folder-open'></i></span> ";
        print "
            <div id='folder".$idcounter."' class='collapse folderContent'>
            ".$accordion."
            </div>
        ";
        // print ID if any found
        if($ids != "") {
            print "
            <br/>".$lang['globalCardId'].": ".$ids;
        } else {
            print "            
            <br/>&nbsp;";
        }
        print "
        </div><!-- ./well -->
        </div><!-- ./row -->
        ";
    }
}

?>

      </div><!-- / .col-lg-12 -->
        <!-- input-group -->          
          <div class="col-md-4 col-sm-6">
            <div class="row" style="margin-bottom:1em;">
              <div class="col-xs-12">
              <h4><?php print $lang['indexManageFilesChips']; ?></h4>
                <a href="cardRegisterNew.php" class="btn btn-primary btn">
                <i class='mdi mdi-cards-outline'></i> <?php print $lang['globalRegisterCard']; ?>
                </a>
              </div>
            </div><!-- ./row -->
        </div><!-- ./col -->
        <!-- /input-group --> 
	      
    </div><!-- /.row -->
    
    <!-- Modal -->
    <div class="modal fade" id="myModal" tabindex="-1" role="dialog" aria-labelledby="myModalLabel">
      <div class="modal-dialog" role="document">
        <div class="modal-content">
          <div class="modal-header">
            <button type="button" class="close" data-dismiss="modal" aria-label="Close"><span aria-hidden="true">&times;</span></button>
            <h4 class="modal-title" id="myModalLabel"><?php print $lang['globalLastUsedCard']; ?></h4>
          </div>
          <div class="modal-body">
<pre>
<?php
print file_get_contents($conf['base_path'].'/shared/latestID.txt', true);
?>
</pre>
          </div>
          <div class="modal-footer">
            <button type="button" class="btn btn-default" data-dismiss="modal"><?php print $lang['globalClose']; ?></button>
          </div>
    
        </div><!-- / .modal-content -->
      </div><!-- /.modal-dialog -->
    </div><!-- /.modal -->


  </div><!-- /.container -->

</body>
</html>
