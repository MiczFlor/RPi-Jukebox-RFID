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
?>
          
          <span class="help-block"><?php print $fdata['streamURL_help']; ?></span>  
          </div>
        </div>
        </fieldset>
        
<!-----------------------------------------
- Folder link
-->
        <fieldset>        
        <!-- Form Name -->
        <legend><?php print $lang['cardFormFolderLegend']; ?></legend>
        
        <!-- Select Basic -->
        <div class="form-group">
          <label class="col-md-4 control-label" for="audiofolder"><?php print $lang['cardFormFolderLabel']; ?></label>
          <div class="col-md-6">
            <select id="audiofolder" name="audiofolder" class="form-control">
              <option value="false"<?php if(!isset($fpost['audiofolder'])) { print " selected=selected"; } ?>><?php print $lang['cardFormFolderSelectDefault']; ?></option>
<?php

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
          <span class="help-block"><?php print $lang['cardFormFolderHelp']; ?></span>  
          </div>          
        </div>
        
        <!-- Text input-->
        <div class="form-group">
          <label class="col-md-4 control-label" for="audiofolderNew"><?php print $lang['cardFormNewFolderLabel']; ?></label>  
          <div class="col-md-6">
          <input value="<?php
          if (isset($fpost['audiofolderNew'])) {
              print $fpost['audiofolderNew'];
          }
          ?>" id="audiofolderNew" name="audiofolderNew" placeholder="<?php print $lang['cardFormNewFolderPlaceholder']; ?>" class="form-control input-md" type="text">
          <span class="help-block"><?php print $lang['cardFormNewFolderHelp']; ?></span>  
          </div>
        </div>
        
<!-----------------------------------------
- Trigger for system function (like volume up, pause, shutdown)
-->
               
        <!-- Select Basic -->
        <div class="form-group">
          <label class="col-md-4 control-label" for="TriggerCommand"><?php print $lang['cardFormTriggerLabel']; ?></label>
           <div class="col-md-6">
            <select id="TriggerCommand" name="TriggerCommand" class="form-control">
              <option value="false"<?php if(!isset($fpost['TriggerCommand'])) { print " selected=selected"; } ?>><?php print $lang['cardFormTriggerSelectDefault']; ?></option>
<?php

// create form fields 
$fn = fopen("../settings/rfid_trigger_play.conf.sample","r");
$counter = 1;

while(! feof($fn))  {
    $result = fgets($fn);
    if(startsWith($result, "#") && trim($result) != "") {
        // group title
        if(startsWith($result, "## ")) {
            print "<option value=\"false\">-- ".trim(substr($result, 3))."</option>";
        }
        // help
        if(startsWith($result, "### ")) {
            //print "<h3>".trim(substr($result, 3))."</h3>";
            // keep help in mind for coming item
            $help = trim(substr($result, 3));
        }
    } elseif(trim($result) != "") {
        // replace values with used or placeholders in sample conf
        $temp = explode("=", $result);
        // leave input empty if no value in active conf
        if(startsWith($fillRfidArrAvailWithUsed[$temp[0]], "%")) {
            $rfidCurrent = "";
        } else {
            $rfidCurrent = $fillRfidArrAvailWithUsed[$temp[0]];
        }
        print "\n<option value=\"".$temp[0]."\"";
        if($temp[0] == $fpost['TriggerCommand']) {
            print " selected=selected";
        }
        print ">".$help." (".$temp[0]." RFID: ";
        if($rfidCurrent != "") {
            print $rfidCurrent;
        } else {
            print "NONE";
        }
        //print " ".$temp[0]." == ".$fpost['TriggerCommand'];
        print ")</option>";
        $help = "";
    }
}
fclose($fn);
?>
            </select>
            <span class="help-block"><?php print $lang['cardFormTriggerHelp']; ?></span>  
          </div>
        </div>  
        </fieldset>
        
<!-----------------------------------------
- Stream (radio, podcast)
-->
        <fieldset>        
        <!-- Form Name -->
        <legend><?php print $lang['cardFormStreamLegend']; ?></legend>
        
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
		  } else { 
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
              <option value="false"<?php if(!isset($fpost['streamType'])) { print " selected=selected"; } ?>><?php print $lang['cardFormStreamTypeSelectDefault']; ?></option>
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
        
        </fieldset>


<!-----------------------------------------
- YouTube
-->
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
        
        
        </fieldset>
              
        
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
