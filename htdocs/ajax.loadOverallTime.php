<?php
include("inc.playerStatus.php");

function validateInput($input) {
    // Ensure the input only contains valid characters
    return preg_match('/^[a-zA-Z0-9_\-\/\.]+$/', $input);
}

function sanitizeInput($input) {
    // Remove any potentially harmful characters from the input
    return htmlspecialchars($input, ENT_QUOTES, 'UTF-8');
}

$playlistOverallTime = sanitizeInput($playlistOverallTime);
$playlistPlayedTime = sanitizeInput($playlistPlayedTime);

if ($playlistOverallTime > 0 && $playlistOverallTime < 3600) {
    print '<span class="badge" style="float: right">' . date("i:s", $playlistPlayedTime) . ' / ' . date("i:s", $playlistOverallTime) . '</span>';
} elseif ($playlistOverallTime > 0) {
    print '<span class="badge" style="float: right">' . gmdate("H:i:s", $playlistPlayedTime) . ' / ' . gmdate("H:i:s", $playlistOverallTime) . '</span>';
}
?>
