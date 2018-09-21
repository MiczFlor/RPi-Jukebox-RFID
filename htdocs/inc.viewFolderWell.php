<?php

// get list of content for each folder
$files = scandir($audiofolder);
$accordion = "<h4>".$lang['indexContainsFiles']."</h4><ul>";
foreach($files as $file) {
// add file name to list, supress if it's lastplayed.dat
    if(is_file($audiofolder."/".$file) && $file != "folder.conf"){
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
parse_str($Audio_Folders_Path.'/'.$audiofolder.'/folder.conf', $folderConf);
$folderConfRaw = file_get_contents($audiofolder.'/folder.conf');
// if folder not empty, display play button and content
if ($accordion != "<h4>".$lang['indexContainsFiles']."</h4><ul></ul>") {
    print "
    <div class='col-md-6'>
    <div class='well'>";
    print "
        <h4><i class='mdi mdi-folder'></i>
            ".str_replace($Audio_Folders_Path.'/', '', $audiofolder)."
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
        <span data-toggle='collapse' data-target='#folder".$idcounter."' class='btn btnFolder hoverGrey'>".$lang['indexShowFiles']." <i class='mdi mdi-folder-open'></i></span> ";
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
?>