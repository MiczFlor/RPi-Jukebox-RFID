<?php
include("inc.playerStatus.php");

if ( $playlistOverallTime > 0 && $playlistOverallTime < 3600 ) {
	print '<span class="badge" style="float: right">'.date("i:s",$playlistPlayedTime).' / '.date("i:s",$playlistOverallTime).'</span>';
} elseif ( $playlistOverallTime > 0 ) {
	print '<span class="badge" style="float: right">'.date("H:i:s",$playlistPlayedTime).' / '.date("H:i:s",$playlistOverallTime).'</span>';
}
?>
