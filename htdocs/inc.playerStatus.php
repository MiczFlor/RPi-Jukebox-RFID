<?php
$playerStatus = [];
$playerStatus['status'] = trim( shell_exec("echo 'status\nclose' | nc -w 1 localhost 6600 | grep -o -P '(?<=state: ).*'") );
$playerStatus['repeat'] = trim( shell_exec("echo 'status\nclose' | nc -w 1 localhost 6600 | grep -o -P '(?<=repeat: ).*'") );
$playerStatus['single'] = trim( shell_exec("echo 'status\nclose' | nc -w 1 localhost 6600 | grep -o -P '(?<=single: ).*'") );
if ( $playerStatus['status'] == "play" || $playerStatus['status'] == "pause" ) {

      $playerStatus['track'] = shell_exec("echo 'currentsong\nclose' | nc -w 1 localhost 6600 | grep -o -P '(?<=file: ).*'");
}
?>
