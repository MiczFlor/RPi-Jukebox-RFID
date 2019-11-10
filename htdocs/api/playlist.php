<?php

/***
 * Starts to play a playlist for a put request.
 * Retrieves information about a playlist for a GET request.
 */
include 'common.php';

if ($_SERVER['REQUEST_METHOD'] === 'GET') {
    handleGet();
} else if ($_SERVER['REQUEST_METHOD'] === 'PUT') {
    handlePut();
} else {
    http_response_code(405);
}

function handleGet() {
    $statusCommand = "echo 'playlist\nclose' | nc -w 1 localhost 6600";
    $execResult = execSuccessfully($statusCommand);
    $result = array();
    $currentEntry = array();
    $index = -1;
    forEach($execResult as $value) {
        $exploded = explode(' ', $value, 2);
        if (count($exploded) >= 2) {
            $key = substr(trim($exploded[0]), 0, -1);
            $value = $exploded[1];
            if ($key === 'file') {
                // next track
                if ($index != -1) {
                    $result[$index] = $currentEntry;
                }
                $index++;
                $currentEntry = array();
            }
            $currentEntry[$key] = $value;
        }
    }
    header('Content-Type: application/json');
    echo json_encode($result);
}

function handlePut() {
    $body = file_get_contents('php://input');
    $json = json_decode(trim($body), TRUE);
    if (validateRequest($json)) {
        $playlist = $json['playlist'];
        if($json['recursive'] === "true") {
            execScript("rfid_trigger_play.sh -d={$playlist} -v=\"recursive\"");
        } else {
            execScript("rfid_trigger_play.sh -d={$playlist}");
        }
    }
}

function validateRequest($json) {
    if ($json['playlist'] == null) {
        http_response_code(400);
        echo "playlist attribute missing";
        return false;
    } else if ($json['recursive'] == null) {
        http_response_code(400);
        echo "recursive attribute missing";
        return false;
    }
    return true;
}

?>
