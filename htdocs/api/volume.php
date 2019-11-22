<?php
namespace JukeBox\Api;

/**
 * Retrieves and sets the volume.
 */
include 'common.php';

if ($_SERVER['REQUEST_METHOD'] === 'GET') {
    $command = "playout_controls.sh -c=getvolume";
    execAndEcho($command);
} else if ($_SERVER['REQUEST_METHOD'] === 'PUT') {
    $body = file_get_contents('php://input');
    if (is_numeric($body)) {
        $command = "playout_controls.sh -c=setvolume -v=$body";
        execScript($command);
        echo $body;
    } else {
        http_response_code(400);
    }
} else {
    http_response_code(405);
}

?>
