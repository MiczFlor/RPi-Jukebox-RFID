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

$title = sanitizeInput($playerStatus['title']);
$album = sanitizeInput($playerStatus['album']);
$artist = sanitizeInput($playerStatus['artist']);
$date = sanitizeInput($playerStatus['date']);
$file = sanitizeInput($playerStatus['file']);

if(trim($title) != "") {
    print "<strong>".$title."</strong>";
    print "<br><i>".str_replace(";", " and ", $artist)."</i>";
    if (empty($album) != true) {
        print "<br>".$album;
        if (empty($date) != true) {
            print " (".$date.")";
        }
    }
} else {
    print "<strong>".basename($file)."</strong>";
}
?>