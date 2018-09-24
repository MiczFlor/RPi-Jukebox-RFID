<?php
if(isset($post['streamFolderName'])) {
    // create new folder
    $exec = "mkdir '".$Audio_Folders_Path."/".$post['streamFolderName']."'; chmod 777 '".$Audio_Folders_Path."/".$post['streamFolderName']."'";
    exec($exec);
    $foldername = $Audio_Folders_Path."/".$post['streamFolderName'];
    // New folder is created so we link a RFID to it. Write $post['streamFolderName'] to cardID file in shortcuts
    $exec = "rm ".$fileshortcuts."; echo '".$post['streamFolderName']."' > ".$fileshortcuts."; chmod 777 ".$fileshortcuts;
    exec($exec);
} else {
    // link to existing audiofolder
    $foldername = $Audio_Folders_Path."/".$post['audiofolder'];
}
$exec = "cd '".$foldername."'; youtube-dl -f bestaudio --extract-audio --audio-format mp3 ".$post['YTstreamURL']." > ".$conf['shared_abs']."/youtube-dl.log; chmod 777 ".$foldername."/* 2>&1 &";
exec($exec);
?>
