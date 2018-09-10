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
    $post['folderNew'] = trim($_GET['folderNew']);
} else {
    if(isset($_POST['folderNew']) && trim($_POST['folderNew']) != "") { 
        $post['folderNew'] = trim($_POST['folderNew']);
    }
}
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
if($_POST['ACTION'] == "fileUpload") {
    /*
    * I spent 3 hours trying to find out why when I upload multiples file $_FILES  return empty, 
    * I did noticed it was only when I select files that exceed 3m so I thought it was something 
    * related to the MAX_UPLOAD_SIZE that for my surprice came as default as 20m which was very 
    * confusing. Later I discovery the problem was in the POST_MAX_SIZE been 3m, so it happen 
    * that not only MAX_UPLOAD_SIZE is responsible and that is why I'd like to know there is no 
    * error message that shows the cause.
    */
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
        && file_exists($post['folder'])
        && is_dir($post['folder'])
    ){
        // yes, a folder was selected
        $messageAction .= "Will move files to folder: '".$post['folder']."'";
        $moveFolder = $post['folder'];
    } elseif(
        // if not, see if we have a new folder to create
        isset($post['folderNew'])
        && $post['folderNew'] != ""
        && ! file_exists($Audio_Folders_Path."/".$post['folderNew'])
    ){
        // yes, valid new folder 
        $messageAction .= "Will create new folder and move files to: '".$post['folderNew']."'";
        // create folder
        $exec = 'sudo mkdir "'.$Audio_Folders_Path.'/'.$post['folderNew'].'"; sudo chown -R pi:www-data "'.$Audio_Folders_Path."/".$post['folderNew'].'"; sudo chmod 775 "'.$Audio_Folders_Path."/".$post['folderNew'].'"';
        exec($exec);
        $moveFolder = $Audio_Folders_Path."/".$post['folderNew'];
    } else {
        $messageWarning .= "<p>No folder selected nor a valid new folder specified.</p>";
    }
    // if neither: error message
    if($messageWarning == "") {
        // else: move files to folder
        foreach($uFiles['ufile'] as $key => $values) {
            $targetName = $moveFolder.'/'.$values['name'];
            $exec = 'sudo mv "'.$values['tmp_name'].'" "'.$targetName.'"; sudo chown -R pi:www-data "'.$targetName.'"; sudo chmod 775 "'.$targetName.'"';
            //print $exec;
            exec($exec);
        }
        $messageSuccess = "<p>Files were successfully uploaded.</p>";
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
        <h1><?php print $lang['fileUploadTitle']; ?></h1>
<?php

//phpinfo();
/*
* Do we need to voice a warning here?
*/
if ($messageAction == "") {
    $messageAction = "<p>If the upload does not work, make sure that you adjust these variables in <code>/etc/php/7.0/fpm/php.ini</code>:<br>
    <code>file_uploads = On</code><br>
    <code>upload_max_filesize = 0</code><br>
    <code>max_file_uploads = 20</code><br>
    <code>post_max_size = 0</code><br>
    And restart the webserver.
    </p>";
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
    
    <div class="row">
      <div class="col-lg-12">
      
        <form name='fileUpload'  enctype="multipart/form-data" method="post" action='<?php print $_SERVER['PHP_SELF']; ?>'>
          <input type="hidden" name="folder" value="<?php print $post['folder']; ?>">
          <input type="hidden" name="filename" value="<?php print $post['filename']; ?>">
          <input type="hidden" name="ACTION" value="fileUpload">
        <fieldset> 
        <legend><i class='mdi mdi-upload-multiple'></i> <?php print $lang['fileUploadLegend']; ?></legend>

        <!-- Select Basic -->
        <div class="form-group">
          <label class="col-md-3 control-label" for="folder"><?php print $lang['fileUploadFilesLabel']; ?></label>
           <div class="col-md-7">
                <ol>
                    <li> <input name="ufile[]" type="file" /></li>
                    <li> <input name="ufile[]" type="file" /></li>
                    <li> <input name="ufile[]" type="file" /></li>
                    <li> <input name="ufile[]" type="file" /></li>
                    <li> <input name="ufile[]" type="file" /></li>
                    <li> <input name="ufile[]" type="file" /></li>
                    <li> <input name="ufile[]" type="file" /></li>
                    <li> <input name="ufile[]" type="file" /></li>
                    <li> <input name="ufile[]" type="file" /></li>
                    <li> <input name="ufile[]" type="file" /></li>
                    <li> <input name="ufile[]" type="file" /></li>
                    <li> <input name="ufile[]" type="file" /></li>
                    <li> <input name="ufile[]" type="file" /></li>
                    <li> <input name="ufile[]" type="file" /></li>
                    <li> <input name="ufile[]" type="file" /></li>
                    <li> <input name="ufile[]" type="file" /></li>
                    <li> <input name="ufile[]" type="file" /></li>
                    <li> <input name="ufile[]" type="file" /></li>
                    <li> <input name="ufile[]" type="file" /></li>
                    <li> <input name="ufile[]" type="file" /></li>
                </ol>
          </div>
 
          <label class="col-md-3 control-label" for="folder"><?php print $lang['fileUploadLabel']; ?></label>
           <div class="col-md-7">
            <select id="folder" name="folder" class="form-control">

              <option value="false"><?php print $lang['cardFormYTSelectDefault']; ?></option>
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

// check if we can preselect an audiofolder if NOT a foldername was posted
if(! isset($fpost['folder'])) {
    if(array_key_exists($fpost['cardID'], $shortcuts)) {
        $fpost['folder'] = $shortcuts[$fpost['cardID']];
    }
}
    
// counter for ID of each folder
$idcounter = 0;

// go through all folders
foreach($audiofolders as $keyfolder => $audiofolder) {
    
    print "              <option value='".$keyfolder."'";
    if($keyfolder == $post['folder']) {
        print " selected=selected";
    }
    print ">".$audiofolder."</option>\n";
   
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
          ?>" id="folderNew" name="folderNew" placeholder="<?php print $lang['cardFormYTFolderPlaceholder']; ?>" class="form-control input-md" type="text">
          <span class="help-block"><?php print $lang['fileUploadFolderHelp']; ?></span>  
          </div>
        </div>
        
        </fieldset>
        
        <!-- Button (Double) -->
        <div class="form-group">
          <label class="col-md-3 control-label" for="submit"></label>
          <div class="col-md-9">
            <button id="submit" name="submit" class="btn btn-success" value="trackMove"><?php print $lang['globalUpload']; ?></button>
            <br clear='all'><br>
          </div>
        </div>

        </form>

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

