<?php
namespace JukeBox\Api;

/**
 * Enables or disabled single for a playlist.
 */
include('../common.php');

if ($_SERVER['REQUEST_METHOD'] === 'PUT') {
    $body = file_get_contents('php://input');
    $json = json_decode(trim($body), TRUE);
    if (validateRequest($json)) {
        $playlist = $json['playlist'];
        $shuffle = $json['single'];
        if ($shuffle === 'true') {
            execScript("single_play.sh -c=singleenable -d='{$playlist}'");
        } else {
            execScript("single_play.sh -c=singledisable -d='{$playlist}'");
        }
    }
} else {
    http_response_code(405);
}


function validateRequest($json) {
    if ($json['playlist'] == null) {
        http_response_code(400);
        echo "playlist attribute missing";
        return false;
    } else if ($json['single'] == null) {
        http_response_code(400);
        echo "single attribute missing";
        return false;
    }
    return true;
}

?>
