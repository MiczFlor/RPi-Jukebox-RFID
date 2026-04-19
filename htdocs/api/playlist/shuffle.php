<?php
namespace JukeBox\Api;

/**
 * Enables or disabled shuffle for a playlist.
 */
include('../common.php');

if ($_SERVER['REQUEST_METHOD'] !== 'PUT') {
    http_response_code(405);
    exit;
}

$body = file_get_contents('php://input');
$json = json_decode($body, true);

if (!validateRequest($json)) {
    exit;
}

$playlist = $json['playlist'];
$shuffle  = filter_var($json['shuffle'], FILTER_VALIDATE_BOOLEAN, FILTER_NULL_ON_FAILURE);

if ($shuffle === null) {
    http_response_code(400);
    echo "Invalid shuffle value";
    exit;
}

if (!preg_match('/^[a-zA-Z0-9_-]+$/', $playlist)) {
    http_response_code(400);
    echo "Invalid playlist value";
    exit;
}

$playlistSafe = escapeshellarg($playlist);
$command = $shuffle
    ? "shuffle_play.sh -c=enableshuffle -d={$playlistSafe}"
    : "shuffle_play.sh -c=disableshuffle -d={$playlistSafe}";

execScript($command);


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
