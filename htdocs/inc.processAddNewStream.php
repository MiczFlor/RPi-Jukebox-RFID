<?php
// create folder $post['streamFolderName']
$exec = "mkdir '".$conf['shared_abs']."/audiofolders/".$post['streamFolderName']."'";
exec($exec);
//print "<p>".$exec."</p>";//???
// figure out $filestream depending on $post['streamType']
switch($post['streamType']) {
    case "podcast":
        $filestream = "podcast.txt";
        break;
    case "youtube":
        $filestream = "youtube.txt";
        break;
    case "livestream":
        $filestream = "livestream.txt";
        break;
    default:
        $filestream = "url.txt";
}
$filestream = $conf['shared_abs']."/audiofolders/".$post['streamFolderName']."/".$filestream;
// write $post['streamURL'] to $filestream
$exec = "echo '".$post['streamURL']."' > '".$filestream."'";
exec($exec);
//print "<p>".$exec."</p>";//???
// make this file accessible by user pi as well as webserver            
$exec = "chmod -R 777 '".$conf['shared_abs']."/audiofolders/".$post['streamFolderName']."'";
exec($exec);
//print "<p>".$exec."</p>";//???
// write $post['streamFolderName'] to cardID file in shortcuts
$exec = "rm ".$fileshortcuts."; echo '".$post['streamFolderName']."' > '".$fileshortcuts."'; chmod 777 '".$fileshortcuts."'";
exec($exec);
//print "<p>".$exec."</p>";//???
?>