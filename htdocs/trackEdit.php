<?php

include("inc.header.php");

/**************************************************
* VARIABLES
* No changes required if you stuck to the
* INSTALL-stretch.md instructions.
* If you want to change the paths, edit config.php
***************************************************/

/* NO CHANGES BENEATH THIS LINE ***********/

$trackDat = array();
$trackDat['metaKeys']['mp3'] = array(
    "COMM==XXX",//=comment
    "TALB",//=album
    "TCOM",//=composer
    "TCON",//=genre
    "TDRC",//=2010
    "TIT2",//=title
    "TPE1",//=artist
    "TPE2",//=album artist
    "TPOS",//=Part of set
    "TRCK",//=Track Number
);
/*
    --AENC    Audio encryption. 
    --APIC    Attached (or linked) Picture. 
    --ASPI    Audio seek point index. 
    --COMM    User comment. 
    --COMR    Commercial frame. 
    --ENCR    Encryption method registration. 
    --EQU2    Equalisation (2). 
    --ETCO    Event timing codes. 
    --GEOB    General Encapsulated Object. 
    --GRID    Group identification registration. 
    --IPLS    Involved People List 
    --LINK    Linked information. 
    --MCDI    Binary dump of CD's TOC 
    --MLLT    MPEG location lookup table. 
    --OWNE    Ownership frame. 
    --PCNT    Play counter. 
    --POPM    Popularimeter. 
    --POSS    Position synchronisation frame 
    --PRIV    Private frame. 
    --RBUF    Recommended buffer size. 
    --RVA2    Relative volume adjustment (2). 
    --RVRB    Reverb. 
    --SEEK    Seek frame. 
    --SIGN    Signature frame. 
    --SYLT    Synchronised lyrics/text. 
    --SYTC    Synchronised tempo codes. 
    --TALB    Album 
    --TBPM    Beats per minute 
    --TCMP    iTunes Compilation Flag 
    --TCOM    Composer 
    --TCON    Content type (Genre) 
    --TCOP    Copyright (c) 
    --TDAT    Date of recording (DDMM) 
    --TDEN    Encoding Time 
    --TDES    iTunes Podcast Description 
    --TDLY    Audio Delay (ms) 
    --TDOR    Original Release Time 
    --TDRC    Recording Time 
    --TDRL    Release Time 
    --TDTG    Tagging Time 
    --TENC    Encoder 
    --TEXT    Lyricist 
    --TFLT    File type 
    --TGID    iTunes Podcast Identifier 
    --TIME    Time of recording (HHMM) 
    --TIPL    Involved People List 
    --TIT1    Content group description 
    --TIT2    Title 
    --TIT3    Subtitle/Description refinement 
    --TKEY    Starting Key 
    --TLAN    Audio Languages 
    --TLEN    Audio Length (ms) 
    --TMCL    Musicians Credits List 
    --TMED    Source Media Type 
    --TMOO    Mood 
    --TOAL    Original Album 
    --TOFN    Original Filename 
    --TOLY    Original Lyricist 
    --TOPE    Original Artist/Performer 
    --TORY    Original Release Year 
    --TOWN    Owner/Licensee 
    --TPE1    Lead Artist/Performer/Soloist/Group 
    --TPE2    Band/Orchestra/Accompaniment 
    --TPE3    Conductor 
    --TPE4    Interpreter/Remixer/Modifier 
    --TPOS    Part of set 
    --TPRO    Produced (P) 
    --TPUB    Publisher 
    --TRCK    Track Number 
    --TRDA    Recording Dates 
    --TRSN    Internet Radio Station Name 
    --TRSO    Internet Radio Station Owner 
    --TSIZ    Size of audio data (bytes) 
    --TSO2    iTunes Album Artist Sort 
    --TSOA    Album Sort Order key 
    --TSOC    iTunes Composer Sort 
    --TSOP    Perfomer Sort Order key 
    --TSOT    Title Sort Order key 
    --TSRC    International Standard Recording Code (ISRC) 
    --TSSE    Encoder settings 
    --TSST    Set Subtitle 
    --TXXX    User-defined text data. 
    --TYER    Year of recording 
    --UFID    Unique file identifier. 
    --USER    Terms of use. 
    --USLT    Unsynchronised lyrics/text transcription. 
    --WCOM    Commercial Information 
    --WCOP    Copyright Information 
    --WFED    iTunes Podcast Feed 
    --WOAF    Official File Information 
    --WOAR    Official Artist/Performer Information 
    --WOAS    Official Source Information 
    --WORS    Official Internet Radio Information 
    --WPAY    Payment Information 
    --WPUB    Official Publisher Information 
    --WXXX    User-defined URL data. 

*/

/*******************************************
* URLPARAMETERS
*******************************************/
if(isset($_GET['folder']) && $_GET['folder'] != "") { 
    $post['folder'] = $_GET['folder'];
} else {
    if(isset($_POST['folder']) && $_POST['folder'] != "") { 
        $post['folder'] = $_POST['folder'];
    }
}
if(isset($_GET['filename']) && $_GET['filename'] != "") { 
    $post['filename'] = $_GET['filename'];
} else {
    if(isset($_POST['filename']) && $_POST['filename'] != "") { 
        $post['filename'] = $_POST['filename'];
    }
}
/*
* track information 
*/
if(isset($_POST['TIT2']) && trim($_POST['TIT2']) != "") { 
    $post['trackTitle'] = trim($_POST['TIT2']);
}
if(isset($_POST['TPE1']) && trim($_POST['TPE1']) != "") { 
    $post['trackArtist'] = trim($_POST['TPE1']);
}
if(isset($_POST['TALB']) && trim($_POST['TALB']) != "") { 
    $post['trackAlbum'] = trim($_POST['TALB']);
}
if(isset($_POST['TCOM']) && trim($_POST['TCOM']) != "") { 
    $post['trackComposer'] = trim($_POST['TCOM']);
}

/*******************************************
* ACTIONS
*******************************************/
$messageAction = "";
$messageSuccess = "";

/*
* Move file to different dir
*/
if($_POST['ACTION'] == "trackMove") {
    if(
    trim($_POST['folderNew']) != "" 
    && file_exists($Audio_Folders_Path."/".$_POST['folderNew'])
    && is_dir($Audio_Folders_Path."/".$_POST['folderNew'])
    // check if new folder is different from current
    && $_POST['folderNew'] != basename($post['folder'])
    ) {
        // rename($post['folder']."/".$post['filename'], $Audio_Folders_Path."/".$_POST['folderNew']."/".$post['filename']);
        $exec = "mv ".$post['folder']."/".$post['filename']." ".$Audio_Folders_Path."/".$_POST['folderNew']."/";
        exec($exec);
        // set new location for form that is being displayed
        $post['folder'] = $Audio_Folders_Path."/".$_POST['folderNew'];
    }
}

/*
* Update track tags
* WARNING: I spent two days testing with ffmpeg, id3v2, id3 and mid3v2 to make utf-8 work. 
* And failed.
* So there is help needed here. Until then, I am using an ugly solution to avoid '?':
* search and replace for Umlaute (because besides the English speaking users, there are
* mainly German speaking Phoniebox tinkerers.
* The function is inside the file htdocs/func.php and used here to make the metadata
* human readable (yet not searcheable :)
*/
if($_POST['ACTION'] == "trackUpdate") {
    unset($exec);
    /*
    * general metadata that should work for all file types
    */
    // trackArtist
    if(isset($post['trackArtist'])) {
	$exec = 'mid3v2 --artist "'.replaceUmlaute($post['trackArtist']).'" '.$post['folder'].'/'.$post['filename'];
        exec($exec);
    }
    // trackTitle
    if(isset($post['trackTitle'])) {
        $exec = "mid3v2 --song '".replaceUmlaute($post['trackTitle'])."' ".$post['folder']."/".$post['filename'];
        exec($exec);
    }
    // trackAlbum
    if(isset($post['trackAlbum'])) {
        $exec = "mid3v2 --album '".replaceUmlaute($post['trackAlbum'])."' ".$post['folder']."/".$post['filename'];
        exec($exec);
    }
    // what file type are we dealing with?
    if(strtolower(pathinfo($post['filename'], PATHINFO_EXTENSION)) == "mp3") {
        // trackComposer
        if(isset($post['trackComposer'])) {
            $exec = "mid3v2 --TCOM '".replaceUmlaute($post['trackComposer'])."' ".$post['folder']."/".$post['filename'];
            exec($exec);
        }
    }
}
/*
* Delete file
*/
if($_POST['ACTION'] == "trackDelete") {
    if($_POST['deleteTrack'] == "yes") {
        // delte the file
        $exec = 'sudo rm "'.$post['folder'].'/'.$post['filename'].'"';
        exec($exec);
        $messageSuccess = "<p>File '".$post['folder']."/".$post['filename']."' was deleted from your collection.</p>";
        // unset the filename and folder var
        unset($post['filename']);
        unset($post['folder']);
    } else {
        $messageWarning = "<p>File '".$post['folder']."/".$post['filename']."' was NOT deleted. You need to select 'yes' to confirm.</p>";
    }
}

/*
* read metadata
*/
$exec = "mid3v2 -l ".$post['folder']."/".$post['filename'];
$res = shell_exec($exec);
$lines = explode(PHP_EOL, $res);
foreach($lines as $line) {
    $parts = explode("=",$line);
    $key = trim(array_shift($parts)); // take the first
    $val = trim(implode("=",$parts)); // put the rest back together
    if (in_array($key, $trackDat['metaKeys']['mp3'])) {
        $trackDat['existingTags'][$key] = $val;
    }
}

/*******************************************
* START HTML
*******************************************/

html_bootstrap3_createHeader("en","Phoniebox",$conf['base_url']);

?>
<body>
  <div class="container">
      
<?php
include("inc.navigation.php");
?>

    <div class="row playerControls">
      <div class="col-lg-12">
        <h1><?php print $lang['trackEditTitle']; ?></h1>
<?php
/*
* Do we need to voice a warning here?
*/
if ($messageAction == "") {
    $messageAction = "";
}  
if(isset($messageWarning) && $messageWarning != "") {
    print '<div class="alert alert-warning">'.$messageWarning.'</div>';
}
if(isset($messageAction) && $messageAction != "") {
    print '<div class="alert alert-info">'.$messageAction.'</div>';
}
if(isset($messageSuccess) && $messageSuccess != "") {
    print '<div class="alert alert-success">'.$messageSuccess.'</div>';
    //unset($post);
}


?>

       </div>
    </div>
<?php
/*
* ONLY show the forms if the file and folder are set and known. e.g. not after file was deleted.
*/
if(
    isset($post['filename'])
    && isset($post['folder'])
    && $post['filename'] != ""
    && $post['folder'] != ""
    ) {
?>
<div class="panel-group">
  <div class="panel panel-default">
    <div class="panel-heading">
      <h4 class="panel-title">
         <i class='mdi mdi-information-outline'></i> <?php print $lang['trackEditInformation']; ?>
      </h4>
    </div><!-- /.panel-heading -->

    <div class="panel-body">
  
        <div class="row">	
          <label class="col-md-3 control-label" for=""><?php print $lang['globalFolder']; ?></label> 
          <div class="col-md-9"><?php print $post['folder']; ?></div>
        </div><!-- / row -->
        <div class="row">	
          <label class="col-md-3 control-label" for=""> <?php print $lang['globalFilename']; ?></label> 
          <div class="col-md-9"><?php print $post['filename']; ?></div>
        </div><!-- / row -->
      
	</div><!-- /.panel-body -->
  </div><!-- /.panel panel-default-->
</div><!-- /.panel-group -->

    <div class="row">
      <div class="col-lg-12">

      
        <form name='volume' method='post' action='<?php print $_SERVER['PHP_SELF']; ?>'>
          <input type="hidden" name="folder" value="<?php print $post['folder']; ?>">
          <input type="hidden" name="filename" value="<?php print $post['filename']; ?>">
          <input type="hidden" name="ACTION" value="trackMove">
        <fieldset> 
        <legend><i class='mdi mdi-folder-move'></i> <?php print $lang['trackEditMove']; ?></legend>
        
        
        <!-- Select Basic -->
        <div class="form-group">
          <label class="col-md-3 control-label" for="folderNew"><?php print $lang['trackEditMoveSelectLabel']; ?></label>
          <div class="col-md-7">
            <select id="folderNew" name="folderNew" class="form-control">
              <!-- the first option will contain the name of the original folder. If this is found after posting, it will mean: do not move -->
              <option value="<?php print basename($post['folder']); ?>" selected="selected"><?php print $lang['trackEditMoveSelectDefault']; ?></option>
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

// counter for ID of each folder
$idcounter = 0;
// go through all folders
foreach($audiofolders as $keyfolder => $audiofolder) {
    if($post['folder'] != $keyfolder) {
        print "              <option value='".$keyfolder."'";
        print ">".$audiofolder."</option>\n";
    }   
}
?>
            </select>
            <span class="help-block"></span>  
          </div>
        </div>
        </fieldset>
        
        <!-- Button (Double) -->
        <div class="form-group">
          <label class="col-md-3 control-label" for="submit"></label>
          <div class="col-md-9">
            <button id="submit" name="submit" class="btn btn-success" value="trackMove"><?php print $lang['globalMove']; ?></button>
            <br clear='all'><br>
          </div>
        </div>

        </form>

      </div><!-- / .col-lg-12 -->
    </div><!-- /.row -->

    <div class="row">
      <div class="col-lg-12">

      
        <form name='volume' method='post' action='<?php print $_SERVER['PHP_SELF']; ?>'>
          <input type="hidden" name="folder" value="<?php print $post['folder']; ?>">
          <input type="hidden" name="filename" value="<?php print $post['filename']; ?>">
          <input type="hidden" name="ACTION" value="trackDelete">
        <fieldset> 
        <legend><i class='mdi mdi-folder-move'></i> <?php print $lang['trackEditDelete']; ?></legend>
          
    <!-- Multiple Radios -->
    <div class="form-group">
      <label class="col-md-3 control-label" for="radios"><?php print $lang['trackEditDeleteLabel']; ?></label>
      <div class="col-md-7">
      <div class="radio">
    <label for="radios-0">
      <input name="deleteTrack" id="deleteTrack-0" value="no" checked="checked" type="radio">
      <?php print $lang['trackEditDeleteNo']; ?>
    </label>
	</div>
  <div class="radio">
    <label for="radios-1">
      <input name="deleteTrack" id="deleteTrack-1" value="yes" type="radio">
      <?php print $lang['trackEditDeleteYes']; ?>
    </label>
	</div>
          <span class="help-block"><?php print $lang['trackEditDeleteHelp']; ?></span>  
  </div>
    </div>

        </fieldset>
        
        <!-- Button (Double) -->
        <div class="form-group">
          <label class="col-md-3 control-label" for="submit"></label>
          <div class="col-md-9">
            <button id="submit" name="submit" class="btn btn-warning" value="trackMove"><?php print $lang['globalDelete']; ?></button>
            <br clear='all'><br>
          </div>
        </div>

        </form>

      </div><!-- / .col-lg-12 -->
    </div><!-- /.row -->

    <div class="row">
      <div class="col-lg-12">

      
        <form name='volume' method='post' action='<?php print $_SERVER['PHP_SELF']; ?>'>
          <input type="hidden" name="folder" value="<?php print $post['folder']; ?>">
          <input type="hidden" name="filename" value="<?php print $post['filename']; ?>">
          <input type="hidden" name="ACTION" value="trackUpdate">
        <fieldset> 
        <legend><i class='mdi mdi-information-outline'></i> Edit track information</legend>
        <div class="alert alert-info">Please note that the tag editing only works well for ASCII chars. German Umlaute will be replaced. Other UTF-8 chars turn into '?'. Help needed: please file pull requests :)</div>
        
        <!-- Text input-->
        <div class="form-group">
          <label class="col-md-3 control-label" for="TIT2">Track title</label>  
          <div class="col-md-9">
          <input value="<?php
          if (isset($trackDat['existingTags']['TIT2']) && trim($trackDat['existingTags']['TIT2']) != "") {
              echo trim($trackDat['existingTags']['TIT2']);
          }
          ?>" id="TIT2" name="TIT2" placeholder="" class="form-control input-md" type="text">
          <span class="help-block"></span>  
          </div>
        </div>
        
        <!-- Text input-->
        <div class="form-group">
          <label class="col-md-3 control-label" for="TPE1">Artist</label>  
          <div class="col-md-9">
          <input value="<?php
          if (isset($trackDat['existingTags']['TPE1']) && trim($trackDat['existingTags']['TPE1']) != "") {
              echo trim($trackDat['existingTags']['TPE1']);
          }
          ?>" id="TPE1" name="TPE1" placeholder="" class="form-control input-md" type="text">
          <span class="help-block"></span>  
          </div>
        </div>
        
        <!-- Text input-->
        <div class="form-group">
          <label class="col-md-3 control-label" for="TCOM">Composer</label>  
          <div class="col-md-9">
          <input value="<?php
          if (isset($trackDat['existingTags']['TCOM']) && trim($trackDat['existingTags']['TCOM']) != "") {
              echo trim($trackDat['existingTags']['TCOM']);
          }
          ?>" id="TCOM" name="TCOM" placeholder="" class="form-control input-md" type="text">
          <span class="help-block"></span>  
          </div>
        </div>
        
        <!-- Text input-->
        <div class="form-group">
          <label class="col-md-3 control-label" for="TALB">Album title</label>  
          <div class="col-md-9">
          <input value="<?php
          if (isset($trackDat['existingTags']['TALB']) && trim($trackDat['existingTags']['TALB']) != "") {
              echo trim($trackDat['existingTags']['TALB']);
          }
          ?>" id="TALB" name="TALB" placeholder="" class="form-control input-md" type="text">
          <span class="help-block"></span>  
          </div>
        </div>
        </fieldset>
        
        <!-- Button (Double) -->
        <div class="form-group">
          <label class="col-md-3 control-label" for="submit"></label>
          <div class="col-md-9">
            <button id="submit" name="submit" class="btn btn-success" value="trackUpdate"><?php print $lang['globalUpdate']; ?></button>
            <br clear='all'><br>
          </div>
        </div>

        </form>

      </div><!-- / .col-lg-12 -->
    </div><!-- /.row -->  

<?php
/*
* ONLY show the forms if the file and folder are set and known. e.g. not after file was deleted.
*
if(
    isset($post['filename'])
    && isset($post['folder'])
    && $post['filename'] != ""
    && $post['folder'] != ""
    ) {
*/
}
?>  
    
  </div><!-- /.container -->

<?php
if($debug == "true") {
    print "<pre>";
    print "_POST\n";
    print_r($_POST);
    print "\nconf\n";
    print_r($conf);
    print "\npost\n";
    print_r($post);
    print "\nfile extension: ".strtolower(pathinfo($post['filename'], PATHINFO_EXTENSION))."\n";//.lower(pathinfo($filname, PATHINFO_EXTENSION));
    print_r($trackDat);
    print $res;
    print "</pre>";
    include('inc.debug.php');
}
?>
</body>
</html>

