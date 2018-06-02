<?php
$vlcStatus = [];

$socket = fsockopen("localhost", 4212, $errno, $errstr);

if ($socket) {
    fwrite($socket, "status\n");

    $lines = [];
    foreach ( range(0, 4) as $i) {
        $lines[$i] = fgets($socket, 4096);
    }

    preg_match('/\( new input: (.*\/shared\/audiofolders\/)?(.*) \)/', $lines[2], $matches);
    $vlcStatus['track'] = $matches[2];
    preg_match('/\( state (\w+) \)/', $lines[4],$matches);
    $vlcStatus['status'] = $matches[1];

    fclose($socket);
}
