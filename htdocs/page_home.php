<?php
?>
<body>
  <div class="container">
      
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
