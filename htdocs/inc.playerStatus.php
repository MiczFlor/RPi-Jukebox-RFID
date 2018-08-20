<?php
$playerStatus = [];
$output = [];
// Get status and current track details. Note: a more PHPish version with fsockopen etc.
// fails if mpd is busy e.g. loading a playlist.
$status = trim( shell_exec("echo 'status\ncurrentsong\nclose' | nc -w 1 localhost 6600 ") );
/**
if($debug == "true") {
    print "<pre>"; print $status; print "</pre>";
}
/**/
// Playout status
preg_match('/\nstate: (.*)\n/', $status, $output);
$playerStatus['state'] = $output[1];
// Playlist repeat
preg_match('/\nrepeat: (.*)\n/', $status, $output);
$playerStatus['repeat'] = $output[1];
// Single repeat
preg_match('/\nsingle: (.*)\n/', $status, $output);
$playerStatus['single'] = $output[1];
// Current track name (file name)
preg_match('/\nfile: (.*)\n/', $status, $output);
$playerStatus['file'] = $output[1];
// Current track playlist position
preg_match('/\nPos: (.*)\n/', $status, $output);
$playerStatus['pos'] = $output[1];
// Current track elapsed time
preg_match('/\nelapsed: (.*)\n/', $status, $output);
$playerStatus['elapsed'] = $output[1];

$plFile=[];
$plTime=[];

$playlist = trim( shell_exec("echo 'playlistinfo\nclose' | nc -w 1 localhost 6600 ") );
// File names of all tracks in the loaded playlist
preg_match_all('/\nfile: (.*)\n/', $playlist, $plFile);
// Time length of all tracks in the loaded playlist
preg_match_all('/\nTime: (.*)\n/', $playlist, $plTime);

// Overall length of playlist
$playlistOverallTime = array_sum($plTime[1]);

// Determine how much of the playlist is already played
$playlistPlayedTime = $playerStatus['elapsed'];
for ($i = 0; $i < $playerStatus['pos']; $i++) {
    $playlistPlayedTime = $playlistPlayedTime + $plTime[1][$i];
}
?>
