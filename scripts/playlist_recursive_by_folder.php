#!/usr/bin/php
<?php
/*
* Examples below
* Note: folder in '' to support whitespaces in folder names
* ./playlist_recursive_by_folder.php folder='ZZZ-SubMaster'
* ./playlist_recursive_by_folder.php folder='ZZZ-SubMaster' list=recursive
* ./playlist_recursive_by_folder.php folder='ZZZ SubMaster Whitespaces' list=recursive
* ./playlist_recursive_by_folder.php folder='ZZZ-SubMaster/001-SubSub/bbb-AudioFormatsTest' list=recursive
* ./playlist_recursive_by_folder.php folder='ZZZ-SubMaster/001-SubSub/AAA MP3 Whitespace StartUpSound' list=recursive
*/

// path to audiofolder
$Audio_Folders_Path = trim(file_get_contents('../settings/Audio_Folders_Path'));

/*
* Get vars passed on from command line
*/
parse_str(implode('&', array_slice($argv, 1)), $_GET);
//print_r($_GET);


/*
* Create path to folder we want to get a list from
*/
$Audio_Folders_Path_Playlist = $Audio_Folders_Path."/".$_GET['folder'];

if(file_exists($Audio_Folders_Path_Playlist)) {
    /*
    * now we look recursively only if list=recursive was given when calling this script
    */
    if($_GET['list'] == "recursive") {
        $folders = dir_list_recursively($Audio_Folders_Path_Playlist);
    } else {
        /*
        * not recursively: only the one folder that was passed on in folder=...
        */
        $folders = array($Audio_Folders_Path_Playlist);
    }
    usort($folders, 'strnatcasecmp');
    /*
    * Eliminate folders which contain special formats like a live stream
    */
    foreach($folders as $key => $value) {
        if(file_exists($value."/livestream.txt")) {
            unset($folders[$key]);
        } else {
            /*
            * relative path from the $Audio_Folders_Path_Playlist folder
            * which is also set in the mpd.conf
            * ARRGH, commented out, not needed here, but for the files :)
            */
            //$folders[$key] = substr($value, strlen($Audio_Folders_Path) + 1, strlen($value));
        }
    }
}

$return = "";
foreach($folders as $folder) {
    $return .= $folder."\n";
}
/*
* prints all folders in a neat order:
print trim($return);
*/

/*
* Walk through the folder paths and get the files
*/
$files_playlist = array();
foreach($folders as $folder) {
    /*
    * list all files and folders
    */
    $folder_files = array_diff(scandir($folder), array('..', '.'));
    /*
    * clean the list 
    */
    foreach ($folder_files as $key => $value) {
        // drop directories
        if(is_dir($folder."/".$value)){
            unset($folder_files[$key]);
        }
        // drop config files
        if(file_exists($folder."/folder.conf")){
            unset($folder_files[$key]);
        }
        // podcasts
        // not sure yet how to handle them, drop them for now
        if(file_exists($folder."/podcast.txt")){
            unset($folder_files[$key]);
        }
    }
    /*
    * relative path from the $Audio_Folders_Path_Playlist folder
    * which is also set in the mpd.conf
    */
    foreach ($folder_files as $key => $value) {
        $folder_files[$key] = substr($folder."/".$value, strlen($Audio_Folders_Path) + 1, strlen($folder."/".$value));
    }    
    /* 
    * order the remaining files - if any...
    */
    usort($folder_files, 'strnatcasecmp');
    
    $files_playlist = array_merge($files_playlist, $folder_files);
}

$return = "";
foreach($files_playlist as $file_playlist) {
    $return .= $file_playlist."\n";
}

print trim($return);

//////////////////////////////////////////////////////////////////////

function dir_list_recursively($rootdir = "") {
  /*
  * Get directory tree recursively.
  * The dir path will end without '/'.
  */
  
  $iter = new RecursiveIteratorIterator(
    new RecursiveDirectoryIterator($rootdir, RecursiveDirectoryIterator::SKIP_DOTS),
    RecursiveIteratorIterator::SELF_FIRST,
    RecursiveIteratorIterator::CATCH_GET_CHILD // Ignore "Permission denied"
  );

  $paths = array($rootdir);
  foreach ($iter as $path => $dir) {
      if ($dir->isDir()) {
          $paths[] = $path;
      } 
  }

  return $paths;
}
?>