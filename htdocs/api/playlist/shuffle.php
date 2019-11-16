<?php
namespace JukeBox\Api;

/**
 * Enables or disabled shuffle for a playlist.
 */
include('../common.php');

if ($_SERVER['REQUEST_METHOD'] === 'PUT') {
    $body = file_get_contents('php://input');
    $json = json_decode(trim($body), TRUE);
    if (validateRequest($json)) {
        $playlist = $json['playlist'];
        $shuffle = $json['shuffle'];
        if ($shuffle === 'true') {
            execScript("shuffle_play.sh -c=enableshuffle -d='{$playlist}'");
        } else {
            execScript("shuffle_play.sh -c=disableshuffle -d='{$playlist}'");
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
    } else if ($json['shuffle'] == null) {
        http_response_code(400);
        echo "shuffle attribute missing";
        return false;
    }
    return true;
}

?>
