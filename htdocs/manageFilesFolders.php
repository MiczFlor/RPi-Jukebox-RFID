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
if (isset($_GET['folder']) && trim($_GET['folder']) != "") {
    $post['folder'] = trim($_GET['folder']);
} else {
    if (isset($_POST['folder']) && trim($_POST['folder']) != "") {
        $post['folder'] = trim($_POST['folder']);
    }
}
if (isset($_GET['folderNew']) && trim($_GET['folderNew']) != "") {
    $post['folderNew'] = trim($_GET['folderNew']);
} else {
    if (isset($_POST['folderNew']) && trim($_POST['folderNew']) != "") {
        $post['folderNew'] = trim($_POST['folderNew']);
    }
}
if (isset($_GET['filename']) && $_GET['filename'] != "") {
    $post['filename'] = $_GET['filename'];
} else {
    if (isset($_POST['filename']) && $_POST['filename'] != "") {
        $post['filename'] = $_POST['filename'];
    }
}
if (isset($_GET['folderCreateNew']) && trim($_GET['folderCreateNew']) != "") {
    $post['folderCreateNew'] = trim($_GET['folderCreateNew']);
} else {
    if (isset($_POST['folderCreateNew']) && trim($_POST['folderCreateNew']) != "") {
        $post['folderCreateNew'] = trim($_POST['folderCreateNew']);
    }
}
if (isset($_GET['folderParent']) && trim($_GET['folderParent']) != "") {
    $post['folderParent'] = trim($_GET['folderParent']);
} else {
    if (isset($_POST['folderParent']) && trim($_POST['folderParent']) != "") {
        $post['folderParent'] = trim($_POST['folderParent']);
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
* Move uploaded file to different dir
*/
if ($_POST['ACTION'] == "fileUpload") {
    /*
    * I spent 3 hours trying to find out why when I upload multiples file $_FILES  return empty, 
    * I did noticed it was only when I select files that exceed 3m so I thought it was something 
    * related to the MAX_UPLOAD_SIZE that for my surprice came as default as 20m which was very 
    * confusing. Later I discovery the problem was in the POST_MAX_SIZE been 3m, so it happen 
    * that not only MAX_UPLOAD_SIZE is responsible and that is why I'd like to know there is no 
    * error message that shows the cause.
    */    
    
    $uFiles = getFiles();
    //print "<pre>"; print_r($uFiles); print "</pre>"; //???
    // are there any files?
    foreach ($uFiles['ufile'] as $key => $values) {
        if (trim($values['name']) == "") {
            unset($uFiles['ufile'][$key]);
        }
    }
    if (count($uFiles['ufile']) == 0) {
        // if 0 there are no files
        $messageWarning .= "<p>No files were uploaded.</p>";
    } 
    /*
    * let's start building the path to move the files to
    * as a relative path.
    */
    if(
        isset($post['folder'])
        && $post['folder'] != ""
        && file_exists($post['folder'])
        && is_dir($post['folder'])
    ) {
        // add the existing folder to the path
        $moveFolder = $post['folder'];
    } else {
        $moveFolder = $Audio_Folders_Path;
    }
    /*
    * see if we need to create a new folder
    */
    if (
        // did we get a new folder to create?
        isset($post['folderNew'])
        && $post['folderNew'] != ""
    ) {
        // add the new folder to the relative folder path
        $moveFolder = $moveFolder . "/" . $post['folderNew'];
        // hang on, does that folder exist already?
        if(!file_exists($Audio_Folders_Path . "/" . $moveFolder)) {
            // no, so create the folder
            $exec = 'mkdir "' . $moveFolder . '"; chown -R pi:www-data "' . $moveFolder . '"; chmod 777 "' . $moveFolder . '"';
            exec($exec);   
            $messageAction .= "Will create new folder and move files to: '" . $moveFolder . "'";
        } else {
            // folder exists already :(
            $messageWarning .= $lang['manageFilesFoldersErrorNewFolderExists'] . "(".$moveFolder.")";
        }
    }
    /*
    * see if any valid folder has been chosen
    */
    //print "if(".realpath($moveFolder)." == ".realpath($Audio_Folders_Path).") {";
    if(realpath($moveFolder) == realpath($Audio_Folders_Path)) {
        $messageWarning .= $lang['manageFilesFoldersErrorNoNewFolder'];
    }
    
    // if no error message
    if ($messageWarning == "") {
        // move files to folder
        foreach ($uFiles['ufile'] as $key => $values) {
            $targetName = $moveFolder . '/' . $values['name'];
            $exec = 'mv "' . $values['tmp_name'] . '" "' . $targetName . '"; chown -R pi:www-data "' . $targetName . '"; chmod 777 "' . $targetName . '"';
            exec($exec);
        }
        $messageSuccess = "<p>Files were successfully uploaded.</p>";
    }
}
// create new folder
if ($_POST['ACTION'] == "folderCreateNew") {
    if($post['folderParent'] != "") {
        $newDirPathRel = $post['folderParent']."/".$post['folderCreateNew'];
    } else {
        $newDirPathRel = $post['folderCreateNew'];
    }
    if($post['folderCreateNew'] == "") {
        $messageWarning .= $lang['manageFilesFoldersErrorNewFolderName'];
    } else {
        if(file_exists($Audio_Folders_Path."/".$newDirPathRel)) {
            $messageWarning .= $lang['manageFilesFoldersErrorNewFolderExists'];
        }
        if($post['folderParent'] != "" && !file_exists($Audio_Folders_Path."/".$post['folderParent'])) {
            $messageWarning .= $lang['manageFilesFoldersErrorNewFolderNotParent'];
        }
    }
    /*
    * have we come here without warning?
    */
    if($messageWarning == "") {
        /*
        * create folder
        */        
        $exec = 'mkdir "'.$Audio_Folders_Path.'/'.$newDirPathRel.'"; chmod 777 "'.$Audio_Folders_Path.'/'.$newDirPathRel.'"; chown -R pi:www-data "' . $Audio_Folders_Path.'/'.$newDirPathRel . '"';
        exec($exec);
        $messageSuccess = "<p>".$lang['manageFilesFoldersSuccessNewFolder']." '".$newDirPathRel."'</p>";
        
        
    }
}

/*******************************************
 * START HTML
 *******************************************/

html_bootstrap3_createHeader("en", "Phoniebox", $conf['base_url']);

?>
<body>
<div class="container">

    <?php
    include("inc.navigation.php");
    ?>

    <div class="row playerControls">
        <div class="col-lg-12">
            <h1><?php print $lang['manageFilesFoldersTitle']; ?></h1>
            <?php

            //phpinfo();
            /*
            * Do we need to voice a warning here?
            */
            if ($messageAction == "") {
                $messageAction = '
<div class="wrap-collabsible">
  <input id="collapsible" class="toggle" type="checkbox">
  <label for="collapsible" class="lbl-toggle">Are you having trouble with uploading files?</label>
  <div class="collapsible-content">
    <div class="content-inner">
    <p>If the upload does not work, make sure that you adjust these variables in <code>/etc/php/7.0/fpm/php.ini</code>:<br>
        <code>file_uploads = On</code><br>
        <code>upload_max_filesize = 0</code><br>
        <code>max_file_uploads = 20</code><br>
        <code>post_max_size = 0</code><br>
        And restart the webserver.
        </p>
    </div>
  </div>
</div>';


            }
            if (isset($messageWarning) && $messageWarning != "") {
                print '<div class="alert alert-warning">' . $messageWarning . '</div>';
            }
            if (isset($messageAction) && $messageAction != "") {
                print '<div class="alert alert-info">' . $messageAction . '</div>';
            }
            if (isset($messageSuccess) && $messageSuccess != "") {
                print '<div class="alert alert-success">' . $messageSuccess . '</div>';
                //unset($post);
            }


            ?>

        </div>
    </div>

    <div class="row">
        <div class="col-lg-12">

            <form class="form-horizontal" name='fileUpload' enctype="multipart/form-data" method="post"
                  action='<?php print $_SERVER['PHP_SELF']; ?>'>
                <input type="hidden" name="folder" value="<?php print $post['folder']; ?>">
                <input type="hidden" name="filename" value="<?php print $post['filename']; ?>">
                <input type="hidden" name="ACTION" value="fileUpload">
                <fieldset>
                    <legend><i class='mdi mdi-upload-multiple'></i> <?php print $lang['manageFilesFoldersUploadLegend']; ?></legend>

                    <!-- Select Basic -->
                    <div class="form-group">
                        <label class="col-md-3 control-label"
                               for="folder"><?php print $lang['manageFilesFoldersUploadFilesLabel']; ?></label>
                        <div class="col-md-7">
                            <input class="form-control" name="ufile[]" type="file" multiple accept="audio/*" required />
                        </div>
                    </div>

                    <div class="form-group">

                        <label class="col-md-3 control-label"
                               for="folder"><?php print $lang['manageFilesFoldersUploadLabel']; ?></label>
                        <div class="col-md-7">
                            <select id="folder" name="folder" class="form-control">

                                <option value="false"><?php print $lang['manageFilesFoldersSelectDefault']; ?></option>
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
                                foreach ($audiofolders_abs as $audiofolder) {
                                    /*
                                    * get the relative path as value, set the absolute path as key
                                    */
                                    $relpath = substr($audiofolder, strlen($Audio_Folders_Path) + 1, strlen($audiofolder));
                                    if ($relpath != "") {
                                        $audiofolders[$audiofolder] = substr($audiofolder, strlen($Audio_Folders_Path) + 1, strlen($audiofolder));
                                    }
                                }

                                // check if we can preselect an audiofolder if NOT a foldername was posted
                                if (!isset($fpost['folder'])) {
                                    if (array_key_exists($fpost['cardID'], $shortcuts)) {
                                        $fpost['folder'] = $shortcuts[$fpost['cardID']];
                                    }
                                }

                                // go through all folders
                                foreach ($audiofolders as $keyfolder => $audiofolder) {

                                    print "              <option value='" . $keyfolder . "'";
                                    if ($keyfolder == $post['folder']) {
                                        print " selected=selected";
                                    }
                                    print ">" . $audiofolder . "</option>\n";

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
                            ?>" id="folderNew" name="folderNew"
                                   placeholder="<?php print $lang['cardFormYTFolderPlaceholder']; ?>"
                                   class="form-control input-md" type="text">
                            <span class="help-block"><?php print $lang['manageFilesFoldersUploadFolderHelp']; ?></span>
                        </div>
                    </div>

                </fieldset>

                <!-- Button (Double) -->
                <div class="form-group">
                    <label class="col-md-3 control-label" for="submit"></label>
                    <div class="col-md-9">
                        <button id="submit" name="submit" class="btn btn-success" value="fileUpload"><?php print $lang['globalUpload']; ?></button>
                        <a href="index.php" id="cancel" name="cancel" class="btn btn-danger"><?php print $lang['globalCancel']; ?></a>
                        <br clear='all'><br>
                    </div>
                </div>

            </form>

        </div><!-- / .col-lg-12 -->
    </div><!-- /.row -->

    <div class="row">
        <div class="col-lg-12">
            <form class="form-horizontal" name='fileUpload' enctype="multipart/form-data" method="post"
                  action='<?php print $_SERVER['PHP_SELF']; ?>'>
                <input type="hidden" name="folder" value="<?php print $post['folder']; ?>">
                <!--input type="hidden" name="filename" value="<?php print $post['filename']; ?>"-->
                <input type="hidden" name="ACTION" value="folderCreateNew">

        <fieldset>        
        <!-- Form Name -->
        <legend><i class='mdi mdi-folder-plus'></i> <?php print $lang['manageFilesFoldersNewFolderTitle']; ?></legend>
        
        <!-- Text input-->
        <div class="form-group">
          <label class="col-md-3 control-label" for="folderCreateNew"><?php print $lang['globalFolderName']; ?></label>  
          <div class="col-md-7">
          <input value="" id="folderCreateNew" name="folderCreateNew" placeholder="<?php print $lang['cardFormYTFolderPlaceholder']; ?>" class="form-control input-md" type="text">
          <span class="help-block"><?php print $lang['folderCreateNew']; ?></span>  
          </div>
        </div>
        
        <!-- Select Basic -->
        <div class="form-group">
          <label class="col-md-3 control-label" for="folderParent"><?php print $lang['manageFilesFoldersNewFolderPositionLegend']; ?></label>
           <div class="col-md-7">
            <select id="folderParent" name="folderParent" class="form-control">
              <option value=""><?php print $lang['manageFilesFoldersNewFolderPositionDefault']; ?></option>
<?php

// go through all folders
foreach($audiofolders as $keyfolder => $audiofolder) {
    print "              <option value='".$audiofolder."'";
    if($audiofolder == $post['folderParent']) {
        print " selected=selected";
    }
    print ">".$audiofolder."</option>\n";
   
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
          <div class="col-md-7">
            <button id="submit" name="submit" class="btn btn-success" value="folderCreateNew"><?php print $lang['globalCreate']; ?></button>
            <a href="index.php" id="cancel" name="cancel" class="btn btn-danger"><?php print $lang['globalCancel']; ?></a>
            <br clear='all'><br>
          </div>
        </div>

        </form>
		<?php
		if ($edition == "plusSpotify") {
		print "
		<legend><i class='mdi mdi-autorenew'></i> ".$lang['manageFilesFoldersRenewDB']."</legend>
		<h4>".$lang['manageFilesFoldersRenewDBinfo']."</h4>
		<a href='".$_SERVER['PHP_SELF']."?scan=true' class='btn btn-success'> ".$lang['manageFilesFoldersLocalScan']."</a>";
		}
		?>

        </div><!-- / .col-lg-12 -->
    </div><!-- /.row -->



</div><!-- /.container -->

<?php
if ($debug == "true") {
    print "<pre>";
    print "_POST\n";
    print_r($_POST);
    print "uFiles\n";
    print_r($uFiles);
    print "\nconf\n";
    print_r($conf);
    print "\npost\n";
    print_r($post);
    print "\nfile extension: " . strtolower(pathinfo($post['filename'], PATHINFO_EXTENSION)) . "\n";//.lower(pathinfo($filname, PATHINFO_EXTENSION));
    print_r($trackDat);
    print $res;
    print "</pre>";
    //include('inc.debug.php');
}
?>
</body>
</html>
