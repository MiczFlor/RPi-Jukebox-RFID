<?php

/*
* this file will be included by 'index.php' for each root folder
* in the directory containing all audiofiles.
* Each root folder will be listed as a panel that can be expanded to see
* containing files and potential subfolders (which in turn expand)
*
* the function 'index_folders_print' in func.php extends the functionality
* and displays the HTML for each folder in the UI
*/

// get all containing folders and subfolders
$subfolders = dir_list_recursively($audiofolder);

/*
* oder subfolders
*/
usort($subfolders, 'strnatcasecmp');
//print "<pre>"; print_r($subfolders); print "</pre>"; //???

$contentTree = array(); // this will be the tree we need for display

/*
* now we need to collect some extra info such as: subfolders? files in folder?
* And create the final array with all this information to display the tree
*/
foreach($subfolders as $key => $subfolder) {
    /*
    * collect containing files and folders
    */
    $containingfolders = array();
    $containingfiles = array();
    /*
    * Get all the folders 
    */
    $subfolderfolders = array_filter(glob($subfolder.'/*'), 'is_dir');
    foreach($subfolderfolders as $subfolderfolder) {
        if(count($subfolderfolders) > 0){
            // YES, we found at least one subfolder
            // take the relative path only
            $containingfolders[$subfolderfolder] = substr($subfolderfolder, strlen($Audio_Folders_Path) + 1, strlen($subfolderfolder));
        }
    }
    /*
    * Get all the files 
    */
    $subfolderfiles = array_filter(glob($subfolder.'/*'), 'is_file');
    //print "<pre>".$subfolder." subfolderfiles"; print_r($subfolderfiles); print "</pre>"; //???        
    foreach($subfolderfiles as $subfolderfile) {
        if(
            is_file($subfolderfile) 
            && basename($subfolderfile) != "folder.conf"
            && basename($subfolderfile) != "cover.jpg"
            && basename($subfolderfile) != "lastplayed.dat" // this is legacy from june 2018
        ){
            // YES, we found a file
            $containingfiles[$subfolderfile] = $subfolderfile;
            //$containingfiles[$subfolderfile] = substr($subfolderfile, strlen($Audio_Folders_Path) + 1, strlen($subfolderfile));
        }
    }
    /*
    * Now we know if the folder is empty or not
    * if not, keep it
    * if empty, drop it
    */
    //if(count($containingfolders) + count($containingfiles) == 0) {
        // empty, do nothing, not even display
    //} else {
        $temp = array();
        // save the absolute path
        $temp['path_abs'] = $subfolder;
        $temp['path_rel'] = substr($subfolderfile, strlen($Audio_Folders_Path) + 1, strlen($subfolderfile));
        $temp['basename'] = basename($subfolder);
        // save the "type" of content 
        if(file_exists($subfolder."/podcast.txt")){
            $temp['type'] = "podcast";
        } elseif(file_exists($subfolder."/livestream.txt")){
            $temp['type'] = "livestream";
        } else {
            $temp['type'] = "generic";
        }
        // chop off the $Audio_Folders_Path in the beginning
        //$temp['path_rel'] = substr($folder."/".$value, strlen($Audio_Folders_Path) + 1, strlen($folder."/".$value));
        $temp['path_rel'] = substr($subfolder, strlen($Audio_Folders_Path) + 1, strlen($subfolder));
        // some special version with no slashes or whitespaces for IDs on the panel collapse
        $temp['id'] = preg_replace('/\//', '---', $temp['path_rel']);
        $temp['id'] = "ID".preg_replace('/\ /', '-_-', $temp['id']);
        // count the level depth in the tree by counting the slashes in the path
        $temp['level'] = substr_count($temp['path_rel'], '/');
        // information about the content
        $temp['count_subdirs'] = count($containingfolders);
        $temp['count_files'] = count($containingfiles);
        usort($containingfolders);
        $temp['subdirs'] = $containingfolders;
        usort($containingfiles, 'strnatcasecmp');
        $temp['files'] = $containingfiles;
        // now make entry in $contentTree
        $contentTree[$temp['path_abs']] = $temp;
        /*
        * Check if folder.conf file exists. If not create it
        */
        if(!file_exists($subfolder."/folder.conf")) {
            $exec = $conf['scripts_abs'].'/inc.writeFolderConfig.sh -c="createDefaultFolderConf" -d="'.preg_replace('/\ /', ' ', $temp['path_rel']).'"';
            //print $exec;
            exec($exec);
        }
        /*
        print "<hr>
        ".$contentTree[$temp['path_abs']]['path_abs']." |
        ".$contentTree[$temp['path_abs']]['path_rel']." |
        #".$contentTree[$temp['path_abs']]['id']."<br>";
        */
    //}
}

if(count($contentTree) > 0) {   
    print "
    <div class='col-md-12'>";

    $rootBranch = current($contentTree);
    
        $getSubDirectories = array();
        /*
        * get the recursive folder structure
        */  
        $getSubDirectories[$rootBranch['path_abs']] = getSubDirectories($audiofolder);

        /*
        * print the panel structure with header
        */
        array_walk($getSubDirectories, 'index_folders_print');

    print "
    </div><!-- ./ class='col-md-12' -->";
}

?>
