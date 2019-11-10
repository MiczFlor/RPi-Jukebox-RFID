<?php
/**
 * Starts to play a song in the current playlist.
 */
include('../common.php');

if ($_SERVER['REQUEST_METHOD'] === 'PUT') {
    $body = file_get_contents('php://input');
    if (is_numeric($body)) {
        // This script always returns with returncode 1, so we cannot check that the returncode is 0
        execScriptWithoutCheck("playout_controls.sh -c=playerplay -v={$body}");
    } else {
        http_response_code(400);
    }
} else {
    http_response_code(405);
}

?>
