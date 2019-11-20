<?php

/***
 * Allows to control the player by sending a command via PUT like 'play' or 'pause'.
 * Retrieves information about the player by sending a GET request.
 */
include 'common.php';

if ($_SERVER['REQUEST_METHOD'] === 'PUT') {
    handlePut();
} else if ($_SERVER['REQUEST_METHOD'] === 'GET') {
    handleGet();
} else {
    http_response_code(405);
}

function handlePut() {
    $body = file_get_contents('php://input');
    $json = json_decode(trim($body), TRUE);
    $inputCommand = $json['command'];
    if ($inputCommand != null) {
        $controlsCommand = determineCommand($inputCommand);
        $execCommand = "playout_controls.sh {$controlsCommand}";
        execScript($execCommand);
    } else {
        echo "Body is missing command";
        http_response_code(400);
    }
}

function handleGet() {
    $statusCommand = "echo 'status\ncurrentsong\nclose' | nc -w 1 localhost 6600";
    $execResult = execSuccessfully($statusCommand);
    $result = array();
    forEach($execResult as $value) {
        $exploded = explode(' ', $value);
        if (count($exploded) == 2) {
            $result[substr(trim($exploded[0]), 0, -1)] = $exploded[1];
        }
    }
    header('Content-Type: application/json');
    echo json_encode($result);
}

function determineCommand($body) {
    switch ($body) {
        case 'play':
            return '-c=playerplay';
        case 'next':
            return '-c=playernext';
        case 'prev':
            return '-c=playerprev';
        case 'replay':
            return '-c=playerreplay -v=playlist';
        case 'pause':
            return '-c=playerpause -v=single';
        case 'repeat':
            return '-c=playerprev -c=playerrepeat -v=playlist';
        case 'single':
            return '-c=playerprev -c=playerrepeat -v=single';
        case 'repeatoff':
            return '-c=playerprev -c=playerrepeat -v=off';
        case 'seekBack':
            return '-c=playerprev -c=playerseek -v=-15';
        case 'seekAhead':
            return '-c=playerprev -c=playerseek -v=+15';
        case 'stop':
            return '-c=playerstop';
        case 'mute':
            return'-c=mute';
        case 'volumeup':
            return'-c=volumeup';
        case 'volumedown':
            return'-c=volumedown';
    }
    echo "Unknown command {$body}";
    http_response_code(400);
    exit;
}

?>
