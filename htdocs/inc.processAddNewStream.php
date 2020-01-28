<?php
// create folder $post['streamFolderName']
$streamfolder = $Audio_Folders_Path."/".$post['streamFolderName']."/";
#print "<p>streamfolder:".$streamfolder."</p>";
#print "<p>shared_abs: ".$conf['shared_abs']."</p>";
$exec = "sudo mkdir -p '".$streamfolder."'; sudo chmod 777 '".$streamfolder."'";
exec($exec);
$exec2 = "sudo chown www-data:pi '".$streamfolder."'; sudo chmod 777 '".$streamfolder."'";
exec($exec2);
$username = posix_getpwuid(posix_geteuid())['name'];
#print "<p>".$exec."</p>";//???
#print "<p>".$exec2."</p>";//???
#print "<p>Username:".$username."</p>";
// figure out $filestream depending on $post['streamType']
switch($post['streamType']) {
	case "spotify":
        $filestream = "spotify.txt";
        break;
    case "podcast":
        $filestream = "podcast.txt";
        break;
/*
    case "youtube":
        $filestream = "youtube.txt";
        break;
*/
    case "livestream":
        $filestream = "livestream.txt";
        break;
    default:
        $filestream = "url.txt";
}

$filestreamfolder = $conf['shared_abs']."/audiofolders/".$post['streamFolderName']."/";
#print "<p>filestreamfolder: ".$filestreamfolder."</p>";
$filestreamfolder = $streamfolder;
#print "<p>filestreamfolder: ".$filestreamfolder."</p>";
$filestream = $filestreamfolder."/".$filestream;
#print "<p>filestream:".$filestream."</p>";
// write $post['streamURL'] to $filestream
$exec = "echo '".$post['streamURL']."' > '".$filestream."'";
exec($exec);
#print "<p>exec:".$exec."</p>";
//#print "<p>".$exec."</p>";//???
// make this file accessible by user pi as well as webserver            
#$exec = "sudo chmod -R 777 '".$conf['shared_abs']."/audiofolders/".$post['streamFolderName']."'";
$exec = "sudo chmod -R 777 '".$filestream."'";
exec($exec);
#print "<p>exec:".$exec."</p>";
//#print "<p>".$exec."</p>";//???
// write $post['streamFolderName'] to cardID file in shortcuts
#print "<p>exec:".$fileshortcuts."</p>";

$exec = "rm ".$fileshortcuts."; echo '".$post['streamFolderName']."' > '".$fileshortcuts."'; sudo chmod 777 '".$fileshortcuts."'";
exec($exec);
#print "<p>exec:".$exec."</p>";
