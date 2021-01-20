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
        $folderskip = $json['folderskip'];
        if ($folderskip === 'true') {
            execScript("shuffle_folder.sh -c=enableskipfolder -d='{$playlist}'");
        } else {
            execScript("shuffle_folder.sh -c=disableskipfolder -d='{$playlist}'");
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
    } else if ($json['folderskip'] == null) {
        http_response_code(400);
        echo "folderskip attribute missing";
        return false;
    }
    return true;
}

?>
