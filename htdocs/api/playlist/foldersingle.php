<?php
namespace JukeBox\Api;

/**
 * Enables or disabled single folder play.
 */
include('../common.php');

if ($_SERVER['REQUEST_METHOD'] === 'PUT') {
    $body = file_get_contents('php://input');
    $json = json_decode(trim($body), TRUE);
    if (validateRequest($json)) {
        $playlist = $json['playlist'];
        $foldersingle = $json['foldersingle'];
        if ($foldersingle === 'true') {
            execScript("shuffle_folder.sh -c=enablesinglefolder -d='{$playlist}'");
        } else {
            execScript("shuffle_folder.sh -c=disablesinglefolder -d='{$playlist}'");
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
    } else if ($json['foldersingle'] == null) {
        http_response_code(400);
        echo "foldersingle attribute missing";
        return false;
    }
    return true;
}

?>
