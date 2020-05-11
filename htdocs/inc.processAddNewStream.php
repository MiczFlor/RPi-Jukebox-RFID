<?php
// create new folder
$streamfolder = $Audio_Folders_Path."/".$post['audiofolderNew']."/";
$exec = "mkdir -p '".$streamfolder."'";
exec($exec);
// New folder is created so we link a RFID to it. Write $post['audiofolderNew'] to cardID file in shortcuts
$exec = "rm ".$fileshortcuts."; echo '".$post['audiofolderNew']."' > ".$fileshortcuts."; chmod 777 ".$fileshortcuts;
exec($exec);

// figure out $streamfile depending on $post['streamType']
switch($post['streamType']) {
	case "spotify":
        $streamfile = "spotify.txt";
        break;
    case "podcast":
        $streamfile = "podcast.txt";
        break;
    case "livestream":
        $streamfile = "livestream.txt";
        break;
    default:
        $streamfile = "url.txt";
}

// write $post['streamURL'] to $streamfile and make accessible to anyone
$exec = "echo '".$post['streamURL']."' > '".$streamfolder."/".$streamfile."'; sudo chmod -R 777 '".$streamfolder."'";
exec($exec);
