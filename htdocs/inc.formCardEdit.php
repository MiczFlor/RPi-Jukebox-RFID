<?php

?>
        <form name='volume' method='post' action='<?php print $_SERVER['PHP_SELF']; ?>'>
        
        <fieldset> 
        <legend><?php print $lang['globalCardId']; ?></legend>
        <!-- Text input-->
        <div class="form-group">
          <label class="col-md-4 control-label" for="streamURL"><?php print $fdata['streamURL_label']; ?></label>  
          <div class="col-md-6">
          
<?php
if($fdata['streamURL_ajax'] == "true") {
    print "<span id=\"refresh_id\"></span>";
} else {
    print "<input value=\"";
    if (isset($fpost['cardID'])) {
        print $fpost['cardID'];
    }
    print "\" id=\"cardID\" name=\"cardID\" placeholder=\"".$fdata['streamURL_placeholder']."\" class=\"form-control input-md\" type=\"text\">";

}

// read the shortcuts available
$shortcutstemp = array_filter(glob($conf['base_path'].'/shared/shortcuts/*'), 'is_file');
$shortcuts = array(); // the array with pairs of ID => foldername
// read files' content into array
foreach ($shortcutstemp as $shortcuttemp) {
    $shortcuts[basename($shortcuttemp)] = trim(file_get_contents($shortcuttemp));
}
//print "<pre>"; print_r($shortcuts); print "</pre>"; //???
?>
          
          <span class="help-block"><?php print $fdata['streamURL_help']; ?></span>  
          </div>
        </div>
        </fieldset>
        
        <fieldset>        
        <!-- Form Name -->
        <legend><?php print $lang['cardFormFolderLegend']; ?></legend>
        
        <!-- Select Basic -->
        <div class="form-group">
          <label class="col-md-4 control-label" for="audiofolder"><?php print $lang['cardFormFolderLabel']; ?></label>
          <div class="col-md-6">
            <select id="audiofolder" name="audiofolder" class="form-control">
              <option value="false"><?php print $lang['cardFormFolderSelectDefault']; ?></option>
<?php
/*
* read the subfolders of $Audio_Folders_Path
*/
$audiofolders_abs = dir_list_recursively($Audio_Folders_Path);
usort($audiofolders_abs, 'strcasecmp');
/*
* get relative paths for pulldown
*/
$audiofolders = array();
foreach($audiofolders_abs as $audiofolder){
    /*
    * get the relative path as value, set the absolute path as key
    */
    $relpath = substr($audiofolder, strlen($Audio_Folders_Path) + 1, strlen($audiofolder));
    if($relpath != "") {
        $audiofolders[$audiofolder] = substr($audiofolder, strlen($Audio_Folders_Path) + 1, strlen($audiofolder));
    }
}
//print "<pre>"; print_r($audiofolders); print "</pre>"; //???

    
/*
// counter for ID of each folder
$idcounter = 0;
// go through all folders
foreach($audiofolders as $keyfolder => $audiofolder) {
    if($post['folder'] != $keyfolder) {
        print "              <option value='".$keyfolder."'";
        print ">".$audiofolder."</option>\n";
    }   
}
*/


// counter for ID of each folder
$idcounter = 0;

// check if we can preselect an audiofolder if NOT a foldername was posted
if(! isset($fpost['audiofolder']) OR trim($fpost['audiofolder']) == "") {
    if(array_key_exists($fpost['cardID'], $shortcuts)) {
        $fpost['audiofolder'] = $shortcuts[$fpost['cardID']];
    }
}

// go through all folders
foreach($audiofolders as $keyfolder => $audiofolder) {
    print "              <option value='".$audiofolder."'";
    if($audiofolder == $fpost['audiofolder']) {
        print " selected=selected";
    }
    print ">".$audiofolder."</option>\n";
}
?>
            </select>
          </div>
        </div>
        </fieldset>
        
        <fieldset>        
        <!-- Form Name -->
        <legend><?php print $lang['globalStream']; ?></legend>
        
        <!-- Text input-->
        <div class="form-group">
          <label class="col-md-4 control-label" for="streamURL"><?php print $lang['cardFormStreamLabel']; ?></label>  
          <div class="col-md-6">
          <input value="<?php
          if (isset($fpost['streamURL'])) {
              print $fpost['streamURL'];
          }
          ?>" id="streamURL" name="streamURL" placeholder="<?php 
		  if ($edition == "plusSpotify") { 
		  print $lang['cardFormStreamPlaceholderPlusSpotify']; 
		  } elseif ($edition == "classic") { 
		  print $lang['cardFormStreamPlaceholderClassic']; 
		  } 
		  ?>" class="form-control input-md" type="text">
          <span class="help-block"><?php print $lang['cardFormStreamHelp']; ?></span>  
          </div>
        </div>
        
        <!-- Select Basic -->
        <div class="form-group">
          <label class="col-md-4 control-label" for="streamType"></label>
          <div class="col-md-6">
            <select id="streamType" name="streamType" class="form-control">
              <option value="false"><?php print $lang['cardFormStreamTypeSelectDefault']; ?></option>
			  <?php
			  if ($edition == "plusSpotify") {
				print "<option value='spotify'";
				if($fpost['streamType'] == "spotify") { print " selected=selected"; }
				print ">Spotify</option>";
			  }
			  ?>
              <option value='podcast'<?php if($fpost['streamType'] == "podcast") { print " selected=selected"; } ?>>Podcast</option>
              <!--option value='youtube'<?php if($fpost['streamType'] == "youtube") { print " selected=selected"; } ?>>YouTube</option-->
              <option value='livestream'<?php if($fpost['streamType'] == "livestream") { print " selected=selected"; } ?>>Web radio / live stream</option>
              <option value='other'<?php if($fpost['streamType'] == "other") { print " selected=selected"; } ?>>Other</option>
            </select>
            <span class="help-block"><?php print $lang['cardFormStreamTypeHelp']; ?></span>  
          </div>
        </div>
        
        <!-- Text input-->
        <div class="form-group">
          <label class="col-md-4 control-label" for="streamFolderName"></label>  
          <div class="col-md-6">
          <input value="<?php
          if (isset($fpost['streamFolderName'])) {
              print $fpost['streamFolderName'];
          }
          ?>" id="streamFolderName" name="streamFolderName" placeholder="<?php print $lang['cardFormStreamFolderPlaceholder']; ?>" class="form-control input-md" type="text">
          <span class="help-block"><?php print $lang['cardFormStreamFolderHelp']; ?></span>  
          </div>
        </div>
        
        </fieldset>

        <fieldset>        
        <!-- Form Name -->
        <legend><?php print $lang['cardFormYTLegend']; ?></legend>
        
        <!-- Text input-->
        <div class="form-group">
          <label class="col-md-4 control-label" for="YTstreamURL"><?php print $lang['cardFormYTLabel']; ?></label>  
          <div class="col-md-6">
          <input value="<?php
          if (isset($fpost['YTstreamURL'])) {
              print $fpost['YTstreamURL'];
          }
          ?>" id="YTstreamURL" name="YTstreamURL" placeholder="<?php print $lang['cardFormYTPlaceholder']; ?>" class="form-control input-md" type="text">
          <span class="help-block"><?php print $lang['cardFormYTHelp']; ?></span>  
          </div>
        </div>
        
        <!-- Select Basic -->
        <div class="form-group">
          <label class="col-md-4 control-label" for="YTaudiofolder"></label>
           <div class="col-md-6">
            <select id="YTaudiofolder" name="YTaudiofolder" class="form-control">
              <option value="false"><?php print $lang['cardFormYTSelectDefault']; ?></option>
<?php

// check if we can preselect an audiofolder if NOT a foldername was posted
if(! isset($fpost['audiofolder'])) {
    if(array_key_exists($fpost['cardID'], $shortcuts)) {
        $fpost['audiofolder'] = $shortcuts[$fpost['cardID']];
    }
}
    
// counter for ID of each folder
$idcounter = 0;

// go through all folders
foreach($audiofolders as $keyfolder => $audiofolder) {
    print "              <option value='".$audiofolder."'";
    if($audiofolder == $fpost['audiofolder']) {
        print " selected=selected";
    }
    print ">".$audiofolder."</option>\n";
   
}
?>
            </select>
            <span class="help-block"></span>  
          </div>
        </div>
        
        <!-- Text input-->
        <div class="form-group">
          <label class="col-md-4 control-label" for="YTstreamFolderName"></label>  
          <div class="col-md-6">
          <input value="<?php
          if (isset($fpost['YTstreamFolderName'])) {
              print $fpost['YTstreamFolderName'];
          }
          ?>" id="YTstreamFolderName" name="YTstreamFolderName" placeholder="<?php print $lang['cardFormYTFolderPlaceholder']; ?>" class="form-control input-md" type="text">
          <span class="help-block"><?php print $lang['cardFormYTFolderHelp']; ?></span>  
          </div>
        </div>
        
        </fieldset>
        
        <!-- Button (Double) -->
        <div class="form-group">
          <label class="col-md-4 control-label" for="submit"></label>
          <div class="col-md-8">
            <button id="submit" name="submit" class="btn btn-success" value="submit"><?php print $lang['globalSubmit']; ?></button>
<?php
if($fdata['streamURL_ajax'] != "true") {
    print '<button id="delete" name="delete" class="btn btn-warning" value="delete">'.$lang['cardFormRemoveCard'].'</button>';
}
?>
            <a href="index.php" id="cancel" name="cancel" class="btn btn-danger"><?php print $lang['globalCancel']; ?></a>
            <br clear='all'><br>
          </div>
        </div>

        </form>
