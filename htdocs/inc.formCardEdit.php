      
        <form name='volume' method='post' action='<?php print $_SERVER['PHP_SELF']; ?>'>
        
        <fieldset> 
        <legend>Card ID</legend>
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
?>
          
          <span class="help-block"><?php print $fdata['streamURL_help']; ?></span>  
          </div>
        </div>
        </fieldset>
        
        <fieldset>        
        <!-- Form Name -->
        <legend>Audio folder</legend>
        
        <!-- Select Basic -->
        <div class="form-group">
          <label class="col-md-4 control-label" for="audiofolder">a) Link card to audio folder</label>
          <div class="col-md-6">
            <select id="audiofolder" name="audiofolder" class="form-control">
              <option value="false">None (pulldown to select a folder)</option>
<?php
// read the subfolders of shared/audiofolders
$audiofolders = array_filter(glob($conf['base_path'].'/shared/audiofolders/*'), 'is_dir');
usort($audiofolders, 'strcasecmp');

// check if we can preselect an audiofolder if NOT a foldername was posted
if(! isset($fpost['audiofolder'])) {
    if(array_key_exists($fpost['cardID'], $shortcuts)) {
        print "got one!!!";    
        $fpost['audiofolder'] = $shortcuts[$fpost['cardID']];
    }
}
    
// counter for ID of each folder
$idcounter = 0;

// go through all folders
foreach($audiofolders as $audiofolder) {
    
    print "              <option value='".basename($audiofolder)."'";
    if(basename($audiofolder) == $fpost['audiofolder']) {
        print " selected=selected";
    }
    print ">".basename($audiofolder)."</option>\n";
   
}
?>
            </select>
          </div>
        </div>
        </fieldset>
        
        <fieldset>        
        <!-- Form Name -->
        <legend>Stream</legend>
        
        <!-- Text input-->
        <div class="form-group">
          <label class="col-md-4 control-label" for="streamURL">b) ... or connect with Stream URL</label>  
          <div class="col-md-6">
          <input value="<?php
          if (isset($fpost['streamURL'])) {
              print $fpost['streamURL'];
          }
          ?>" id="streamURL" name="streamURL" placeholder="http(...).mp3 / .m3u / .ogg / ..." class="form-control input-md" type="text">
          <span class="help-block">Add the URL for a podcast, web radio, stream or other online media</span>  
          </div>
        </div>
        
        <!-- Select Basic -->
        <div class="form-group">
          <label class="col-md-4 control-label" for="streamType"></label>
          <div class="col-md-6">
            <select id="streamType" name="streamType" class="form-control">
              <option value="false">Select type of stream</option>
              <option value='podcast'<?php if($fpost['streamType'] == "podcast") { print " selected=selected"; } ?>>Podcast</option>
              <option value='youtube'<?php if($fpost['streamType'] == "youtube") { print " selected=selected"; } ?>>YouTube</option>
              <option value='livestream'<?php if($fpost['streamType'] == "livestream") { print " selected=selected"; } ?>>Web radio / live stream</option>
              <option value='other'<?php if($fpost['streamType'] == "other") { print " selected=selected"; } ?>>Other</option>
            </select>
            <span class="help-block">Select the type of URL / stream you are adding</span>  
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
          ?>" id="streamFolderName" name="streamFolderName" placeholder="e.g. 'Station Name'" class="form-control input-md" type="text">
          <span class="help-block">Name for the audio folder that will contain the stream URL.</span>  
          </div>
        </div>
        
        </fieldset>
        
        <!-- Button (Double) -->
        <div class="form-group">
          <label class="col-md-4 control-label" for="submit"></label>
          <div class="col-md-8"><br/>
            <button id="submit" name="submit" class="btn btn-success" value="submit">Submit</button>
            <a href="index.php" id="cancel" name="cancel" class="btn btn-danger">Cancel</a>
          </div>
        </div>

        </form>