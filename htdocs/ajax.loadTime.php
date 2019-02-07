<?php
include("inc.playerStatus.php");
print '<span class="badge" style="float: right">';
if ( $plTime['1'][$playerStatus['pos']] < 3600 ) {
	print date("i:s",$playerStatus['elapsed']);
	// Livestream and podcasts have no time length, show only elapsed time
	if ( $plTime['1'][$playerStatus['pos']] > 0 ) {
		print ' / '.date("i:s",$plTime['1'][$playerStatus['pos']]);
	}
} else {
	print date("H:i:s",$playerStatus['elapsed']);
	// Livestream and podcasts have no time length, show only elapsed time
	if ( $plTime['1'][$playerStatus['pos']] > 0 ) {
		print ' / '.date("H:i:s",$plTime['1'][$playerStatus['pos']]);
	}
}
print '</span>';
?>