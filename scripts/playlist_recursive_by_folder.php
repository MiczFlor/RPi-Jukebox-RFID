#!/usr/bin/php
<?php
/*
* Examples below
* Note: folder in '' to support whitespaces in folder names
* ./playlist_recursive_by_folder.php folder="ZZZ-SubMaster"
* ./playlist_recursive_by_folder.php folder="ZZZ-SubMaster" list=recursive
* ./playlist_recursive_by_folder.php folder="ZZZ SubMaster Whitespaces" list=recursive
* ./playlist_recursive_by_folder.php folder="ZZZ-SubMaster/fff-threeSubs" list=recursive
*
* ./rfid_trigger_play.sh -d="ZZZ-SubMaster" -v=recursive
* ./rfid_trigger_play.sh -d="ZZZ-SubMaster/fff-threeSubs" -v=recursive
* ./rfid_trigger_play.sh -d="ZZZ SubMaster Whitespaces" -v=recursive
*/

$debug = "false";

// get path of this file
//$PATHDATA = ;
include(dirname(__FILE__).'/../htdocs/func.php');

// path to audiofolder
$Audio_Folders_Path = trim(file_get_contents(dirname(__FILE__).'/../settings/Audio_Folders_Path'));

/*
* Get vars passed on from command line
*/
parse_str(implode('&', array_slice($argv, 1)), $_GET);


/*
* Create path to folder we want to get a list from
*/
$Audio_Folders_Path_Playlist = $Audio_Folders_Path."/".$_GET['folder'];

if(file_exists($Audio_Folders_Path_Playlist)) {
    /*
    * now we look recursively only if list=recursive was given when calling this script
    */
    if(isset($_GET['list']) && $_GET['list'] == "recursive") {
        $folders = dir_list_recursively($Audio_Folders_Path_Playlist);
    } else {
        /*
        * not recursively: only the one folder that was passed on in folder=...
        */
        $folders = array($Audio_Folders_Path_Playlist);
    }
    /*
    * sorting now to make sure we have aaaaallllll the folder in a neat list
    */
    usort($folders, 'strnatcasecmp');
}

// some debugging info
if($debug == "true") {
    print "\$_GET:";
    print_r($_GET);
    print "\$Audio_Folders_Path: ".$Audio_Folders_Path."\n";
    print "\$folders:";
    print_r($folders);
}


/*
* prints all folders in a neat order:
*
$return = "";
foreach($folders as $folder) {
    $return .= $folder."\n";
}
print trim($return);
/**/

/*
* Walk through the folder paths and get the files
*/
$files_playlist = array();
foreach($folders as $folder) {
    //print "\n---------------------\nFOLDER:".$folder."\n";//???
    /*
    * empty the array from what we might have found the last time in this foreach
    */
    $folder_files = array();
    /*
    * totally skip live stream folders
    * a folder with a live stream is dealt with already in rfid_trigger_play.sh
    * and should not be part of a recursive list, because it never stops playing?
    * Actually, let's keep it in, because the listener can always skip forward
    * to get out of the live stream.
    */
    //if(!file_exists($folder."/livestream.txt")){
        /*
        * podcasts, get the files
        * special treatment for podcasts - which are URLs not relative paths!
        */
        if(file_exists($folder."/podcast.txt")){
            /*
            * Read podcast URL and extract audio links from enclosure tag
            */
            $podcast = trim(file_get_contents($folder."/podcast.txt"));
            //wget -q -O - "http://www.kakadu.de/podcast-kakadu.2730.de.podcast.xml" | sed -n 's/.*enclosure.*url="\([^"]*\)".*/\1/p'
            //wget -q -O - "https://www1.wdr.de/mediathek/audio/hoerspiel-speicher/wdr_hoerspielspeicher150.podcast" | sed -n 's/.*enclosure.*url="\([^"]*\)".*/\1/p'
            $exec = 'wget -q -O - \''.$podcast.'\' | sed -n \'s/.*enclosure.*url="\([^"]*\)".*/\1/p\'';
            /*
            * get all the playlist enclosure URLs in a multiline string
            */
            $podcastitems = trim(shell_exec($exec));
            /*
            * Now we replace $folder_files with the podcast playlist URLs
            */
            $folder_files = explode("\n", $podcastitems);     
            /* 
            * NOTE: podcast content is NOT ordered - because they are an ordered playlist already
            */
        } elseif(file_exists($folder."/livestream.txt")) {
            /*
            * Read content of the file and add to the array
            */
            $livestreamURL = file_get_contents($folder."/livestream.txt");
            $folder_files = array($livestreamURL);
        } else {
            /*
            * ordinary, local files
            * list all files and folders
            * ignore . and ..
            */
            $folder_files = array_diff(scandir($folder), array('..', '.'));
            // some debugging info
            if($debug == "true") {
                print "\$folder:".$folder."\n";
                print "\$folder_files all:";
                print_r($folder_files);
            }
            /*
            * clean up what we found in the folder
            */
            foreach ($folder_files as $key => $value) {
                // drop directories
                if(is_dir($folder."/".$value)){
                    unset($folder_files[$key]);
                }
                // drop config files
                if($folder."/".$value == $folder."/folder.conf"){
                    unset($folder_files[$key]);
                } 
            }  
            // some debugging info
            if($debug == "true") {
                print "\$folder_files cleaned:";
                print_r($folder_files);
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
            * NOTE: podcast content is NOT ordered - because they are an ordered playlist already
            */
            usort($folder_files, 'strnatcasecmp');
        }
        /*
        * push files to playlist
        */
        $files_playlist = array_merge($files_playlist, $folder_files);
    //}
}

$return = "";
foreach($files_playlist as $file_playlist) {
    if($file_playlist != "") {
        $return .= $file_playlist."\n";
    }
}

print trim($return);

?>