<?php

include("inc.header.php");

/**************************************************
* VARIABLES
* No changes required if you stuck to the
* INSTALL-stretch.md instructions.
* If you want to change the paths, edit config.php
***************************************************/

/* NO CHANGES BENEATH THIS LINE ***********/


/*******************************************
* URLPARAMETERS
*******************************************/
if(isset($_GET['folder']) && trim($_GET['folder']) != "") { 
    $post['folder'] = trim($_GET['folder']);
} else {
    if(isset($_POST['folder']) && trim($_POST['folder']) != "") { 
        $post['folder'] = trim($_POST['folder']);
    }
}
if(isset($_GET['folderNew']) && trim($_GET['folderNew']) != "") { 
    $post['folderNew'] = $_GET['folderNew'];
} else {
    if(isset($_POST['folderNew']) && trim($_POST['folderNew']) != "") { 
        $post['folderNew'] = $_POST['folderNew'];
    }
}

/*
if(isset($_GET['folderNew']) && trim($_GET['folderNew']) != "") { 
    $post['folderNew'] = trim($_GET['folderNew']);
} else {
    if(isset($_POST['folderNew']) && trim($_POST['folderNew']) != "") { 
        $post['folderNew'] = trim($_POST['folderNew']);
    }
}
*/
if(isset($_GET['filename']) && $_GET['filename'] != "") { 
    $post['filename'] = $_GET['filename'];
} else {
    if(isset($_POST['filename']) && $_POST['filename'] != "") { 
        $post['filename'] = $_POST['filename'];
    }
}

/*******************************************
* ACTIONS
*******************************************/
$messageAction = "";
$messageSuccess = "";
// no error to start with
$messageWarning = "";

/*
* Move file to different dir
*/

if($_POST['ACTION'] == "userScript") {

$messageAction .= "Executed 'sudo ".$conf['scripts_abs']."/userscripts/".$post['folder']." ".$post['folderNew']."'";
 // funktionstest // $exec = "sudo mkdir '".$Audio_Folders_Path."/".$post['folderNew']."'; sudo touch '".$Audio_Folders_Path."/".$post['folderNew']."/'".$post['folder'];
 
            $exec = "sudo ".$conf['scripts_abs']."/userscripts/".$post['folder']." ".$post['folderNew'];
            exec($exec);

}

/*

if($_POST['ACTION'] == "fileUpload") {
    /*
    * I spent 3 hours trying to find out why when I upload multiples file $_FILES  return empty, 
    * I did noticed it was only when I select files that exceed 3m so I thought it was something 
    * related to the MAX_UPLOAD_SIZE that for my surprice came as default as 20m which was very 
    * confusing. Later I discovery the problem was in the POST_MAX_SIZE been 3m, so it happen 
    * that not only MAX_UPLOAD_SIZE is responsible and that is why I'd like to know there is no 
    * error message that shows the cause.
    
    $uFiles = getFiles();
    // are there any files?
    foreach($uFiles['ufile'] as $key => $values) {
        if(trim($values['name']) == "") {
            unset($uFiles['ufile'][$key]);
        }
    }
    if(count($uFiles['ufile']) == 0) {
        // if 0 there are no files
        $messageWarning .= "<p>No files were uploaded.</p>";
    } elseif(
        // see if we have a folder selected that exists
        isset($post['folder'])
        && $post['folder'] != ""
        && file_exists($Audio_Folders_Path."/".$post['folder'])
        && is_dir($Audio_Folders_Path."/".$post['folder'])
        ){
            // yes, a folder was selected
            $messageAction .= "Will move files to folder: '".$post['folder']."'";
            $moveFolder = $Audio_Folders_Path."/".$post['folder'];
    } elseif(
        // if not, see if we have a new folder to create
        isset($post['folderNew'])
        && $post['folderNew'] != ""
        && ! file_exists($Audio_Folders_Path."/".$post['folderNew'])
        ){
            // yes, valid new folder 
            $messageAction .= "Will create new folder and move files to: '".$post['folderNew']."'";
            // create folder
            $exec = "sudo mkdir ".$Audio_Folders_Path."/".$post['folderNew']."; sudo chmod 777 ".$Audio_Folders_Path."/".$post['folderNew'];
            exec($exec);
            $moveFolder = $Audio_Folders_Path."/".$post['folderNew'];
    } else {
        $messageWarning .= "<p>No folder selected nor a valid new folder specified.</p>";
    }
    // if neither: error message
    if($messageWarning == "") {
        // else: move files to folder
        foreach($uFiles['ufile'] as $key => $values) {
//            $replafile = str_replace(" ", "_", $values['name']); 
//            $exec = "mv ".$values['tmp_name']." ".$moveFolder."/".$replafile."; chmod 777 ".$moveFolder."/".$replafile;
              $exec = "mv ".$values['tmp_name']." ".$moveFolder."/".$values['name']."; chmod 777 ".$moveFolder."/".$values['name'];

           // $exec = "mv ".$values['tmp_name']." "".$moveFolder."/".$values['name'].""; chmod 777 "".$moveFolder."/".$values['name']";
            exec($exec);
        }
        $messageSuccess = "<p>Files were successfully uploaded.</p>";
    }
    
    
}
*/
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
        <h1>User scripts</h1>
<?php

//phpinfo();
/*
* Do we need to voice a warning here?
*/
if ($messageAction == "") {
    $messageAction = "These scripts in /scripts/userscripts/ are executed without feedback and should log their own errors";
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
    
     <!-- Form 1 -->
    
     <div class="row">
      <div class="col-lg-12">
      
        <form name='userScript'  enctype="multipart/form-data" method="post" action='<?php print $_SERVER['PHP_SELF']; ?>'>
          <input type="hidden" name="folder" value="<?php print $post['folder']; ?>">
          <input type="hidden" name="filename" value="<?php print $post['filename']; ?>">
          <input type="hidden" name="ACTION" value="userScript">
        <fieldset> 
        <legend><i class='mdi mdi-file-document-box'></i>Start custom scripts</legend>

        <!-- Select Basic -->
        <div class="form-group">
        
 
          <label class="col-md-3 control-label" for="folder">Custom script</label>
           <div class="col-md-7">
            <select id="folder" name="folder" class="form-control">

              <option value="false"><?php print $lang['cardFormYTSelectDefault']; ?></option>
<?php
// read the subfolders of $Audio_Folders_Path
$audiofolders = array_filter(glob($conf['scripts_abs'].'/userscripts/*'), 'is_file');
usort($audiofolders, 'strcasecmp');


// check if we can preselect an audiofolder if NOT a foldername was posted
/* if(! isset($fpost['folder'])) {
    if(array_key_exists($fpost['cardID'], $shortcuts)) {
        $fpost['folder'] = $shortcuts[$fpost['cardID']];
    }
}
*/  
// counter for ID of each folder
$idcounter = 0;

// go through all folders
foreach($audiofolders as $audiofolder) {

    print "              <option value='".basename($audiofolder)."'";
    if(basename($audiofolder) == $post['folder']) {
        print " selected=selected";
    }
    print ">".basename($audiofolder)."</option>\n";
   
}
?>
            </select>
          </div>
        </div>
      
      
        
        <!-- Text input-->
        <div class="form-group">
          <label class="col-md-3 control-label" for="folderNew"></label>  
          
          <div class="col-md-7">
          <input value="<?php
          if (isset($post['folderNew'])) {
              print $post['folderNew'];
          }
          ?>" id="folderNew" name="folderNew" placeholder="add cmdline parameters here (e.g. <newssid ssid passwort> for addhotspot.sh" class="form-control input-md" type="text">
          <span class="help-block">Select the script you want to execute and add parameters (see full script below for parameter order) </span>  
          </div>
        </div>

        
        </fieldset>
        
        <!-- Button (Double) -->
        <div class="form-group">
          <label class="col-md-3 control-label" for="submit"></label>
          <div class="col-md-9">
            <button id="submit" name="submit" class="btn btn-success" value="trackMove">Execute script</button>
            <br clear='all'><br>
          </div>
        </div>

        </form>
<br/><br/>
<label class="col-md-3 control-label" for="scriptfiles"></label>
<?php
// parse all scriptfiles with linebreaks into alterboxes and hide them for later unhiding via selectbox onchange 
foreach($audiofolders as $audiofolder) {
$perms = substr(decoct(fileperms($conf["scripts_abs"]."/userscripts/".basename($audiofolder))), 3);
if(preg_match("([7|5|3|1])",$perms)) {$fcolor =""; }
else {$fcolor ="red"; }
print "<div id='".basename($audiofolder)."' class='col-md-7 alert alert-info source' style='font-family: monospace; font-size: small; display:none'>";
print "Filename:".basename($audiofolder)."(Filerights:<font color=".$fcolor.">".$perms."</font>)<br/>";
print "--------------------------------------------------------<br/>";
print nl2br(file_get_contents($conf['scripts_abs']."/userscripts/".basename($audiofolder)));
print "--------------------------------------------------------<br/>";
print "</div>";
}
?>

<br/><br/>

<script type="text/javascript">
 
   var sel = document.getElementById('folder');
   sel.onchange = function() {
    // hide all scripts
    var elems = document.getElementsByClassName('source');
      for(var i = 0; i < elems.length; i++) {
    elems[i].style.display = "none";
     }
    // display only selected script to see which variables should be entered
    document.getElementById(this.value).style.display = "block";
    }
</script>


      </div><!-- / .col-lg-12 -->

    </div><!-- /.row -->
    
  
        
    
  </div><!-- /.container -->

<?php
if($debug == "true") {
    print "<pre>";
    print "_POST\n";
    print_r($_POST);
    print "uFiles\n";
    print_r($uFiles);
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

