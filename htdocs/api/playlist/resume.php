<?php
/**
 * Enables or disabled resume for a playlist.
 */
include('../common.php');

if ($_SERVER['REQUEST_METHOD'] === 'PUT') {
    $body = file_get_contents('php://input');
    $json = json_decode(trim($body), TRUE);
    if (validateRequest($json)) {
        $playlist = $json['playlist'];
        $resume = $json['resume'];
        if ($resume === 'true') {
            execScript("resume_play.sh -c=enableresume -d={$playlist}");
        } else {
            execScript("resume_play.sh -c=disableresume -d={$playlist}");
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
    } else if ($json['resume'] == null) {
        http_response_code(400);
        echo "resume attribute missing";
        return false;
    }
    return true;
}

?>
