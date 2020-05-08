<?php
// create new folder
$streamfolder = $Audio_Folders_Path."/".$post['audifolderNew']."/";
$exec = "sudo mkdir -p '".$streamfolder."'";
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

// write $post['streamURL'] to $filestream and make accessible to anyone
$exec = "echo '".$post['streamURL']."' > '".$streamfolder."/".$streamfile."'; sudo chmod -R 777 '".$streamfolder."'";
exec($exec);
