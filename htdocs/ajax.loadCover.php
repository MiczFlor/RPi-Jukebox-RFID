<?php
include("config.php");
include("inc.playerStatus.php");
$file = $playerStatus['file'];

$Audio_Folders_Path = trim(file_get_contents('../settings/Audio_Folders_Path'));
$Latest_Folder_Played = trim(file_get_contents('../settings/Latest_Folder_Played'));
$Latest_Played_File = trim(file_get_contents('../settings/Latest_Played_File'));

$pathSettings = realpath('../settings/');
$spover = $Audio_Folders_Path."/../../settings/cover.jpg";
$ocover = $Audio_Folders_Path."/".$Latest_Folder_Played."/cover.jpg";
//$nocover = "https://upload.wikimedia.org/wikipedia/commons/b/b9/No_Cover.jpg";
$nocover = "_assets/img/No_Cover.jpg";

if (file_exists($Audio_Folders_Path.'/'.$Latest_Folder_Played.'/spotify.txt') && $file != $Latest_Played_File) {
	// this is for loading cover!
	$url = "https://open.spotify.com/oembed/?url=".$playerStatus['file']."&format=json";

	$str = file_get_contents($url);

	$json  = json_decode($str, true);

	$cover = $json['thumbnail_url'];
	$title = $json['title'];

	if(is_null($cover) === true) {
		unlink($spover);
		copy($ocover, $spover);
	} else {
		$coverdl = file_get_contents($cover);
		file_put_contents($spover, $coverdl);
	}
	$handle = fopen('../settings/Latest_Played_File', 'w');
	fwrite($handle, $file);
	fclose($handle);
}

if(file_exists($Audio_Folders_Path.'/'.$Latest_Folder_Played.'/cover.jpg') && !file_exists($Audio_Folders_Path.'/'.$Latest_Folder_Played.'/spotify.txt')) { 
    print '<center>';
	print  "<img class='img-responsive img-thumbnail' src='data:image/jpg;base64,".base64_encode(file_get_contents("$ocover"))."' alt=''/>";
    print '</center>';
} elseif (file_exists($Audio_Folders_Path.'/'.$Latest_Folder_Played.'/spotify.txt')) {
    print '<center>';
	print  "<img class='img-responsive img-thumbnail' src='data:image/jpg;base64,".base64_encode(file_get_contents("$spover"))."' alt=''/>";
    print '</center>';	
} else {
    print '<center>';
    print "<img class='img-responsive img-thumbnail' src='data:image/jpg;base64,".base64_encode(file_get_contents("$nocover"))."' alt=''/>";
    print '</center>';
}
?>
