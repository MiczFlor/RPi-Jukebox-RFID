<?php
if(isset($post['audiofolderNew'])) {
    // create new folder
    $exec = "mkdir --parents '".$Audio_Folders_Path."/".$post['audiofolderNew']."'; chmod 777 '".$Audio_Folders_Path."/".$post['audiofolderNew']."'";
    exec($exec);
    $foldername = $Audio_Folders_Path."/".$post['audiofolderNew'];
    // New folder is created so we link a RFID to it. Write $post['audiofolderNew'] to cardID file in shortcuts
    $exec = "rm ".$fileshortcuts."; echo '".$post['audiofolderNew']."' > ".$fileshortcuts."; chmod 777 ".$fileshortcuts;
    exec($exec);
} else {
    // link to existing audiofolder
    $foldername = $Audio_Folders_Path."/".$post['audiofolder'];
}
$exec = "cd '".$foldername."'; youtube-dl -f bestaudio --extract-audio --audio-format mp3 ".$post['YTstreamURL']." > ".$conf['shared_abs']."/youtube-dl.log; chmod 777 ".$foldername."/* 2>&1 &";
exec($exec);
?>
