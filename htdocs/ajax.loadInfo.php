<?php
include("inc.playerStatus.php");
$title = $playerStatus['title'];
$album = $playerStatus['album'];
$artist = $playerStatus['artist'];
$date = $playerStatus['date'];
$file = $playerStatus['file'];


if(trim($title) != "") {
	print "<strong>".$title."</strong>";
	print "<br><i>".str_replace(";", " and ", $artist)."</i>";
	if (empty($album) != true) {
		print "<br>".$album;
		if (empty($date) != true) {
			print " (".$date.")";
		}
	}
} else {
	print "<strong>".basename($file)."</strong>";
}

?>