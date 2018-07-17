<?php
$playerStatus = [];
$playerStatus['status'] = trim( shell_exec("echo 'status\nclose' | nc.openbsd -w 1 localhost 6600 | grep -o -P '(?<=state: ).*'") );

if ( $playerStatus['status'] == "play" || $playerStatus['status'] == "pause" ) {

      $playerStatus['track'] = shell_exec("echo 'currentsong\nclose' | nc.openbsd -w 1 localhost 6600 | grep -o -P '(?<=file: ).*'");
}
?>
