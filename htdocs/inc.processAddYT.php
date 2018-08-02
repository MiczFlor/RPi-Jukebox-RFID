<?php
if(isset($post['streamFolderName'])) {
    // create new folder
    $exec = "mkdir '".$conf['shared_abs']."/audiofolders/".$post['streamFolderName']."'";
    exec($exec);
    $foldername = $post['streamFolderName'];
    // New folder is created so we link a RFID to it. Write $post['streamFolderName'] to cardID file in shortcuts
    $exec = "rm ".$fileshortcuts."; echo '".$post['streamFolderName']."' > ".$fileshortcuts."; chmod 777 ".$fileshortcuts;
    exec($exec);
} else {
    // link to existing audiofolder
    $foldername = $post['audiofolder'];
}
$exec = "cd '".$conf['shared_abs']."/audiofolders/".$foldername."' && youtube-dl -f bestaudio --extract-audio --audio-format mp3 ".$post['YTstreamURL']." > ".$conf['shared_abs']."/youtube-dl.log 2>&1 &";
exec($exec);
?>
