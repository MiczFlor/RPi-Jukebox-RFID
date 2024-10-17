<?php
function validateInput($input) {
    // Ensure the input only contains valid characters
    return preg_match('/^[a-zA-Z0-9_\-\/\.]+$/', $input);
}

function sanitizeInput($input) {
    // Remove any potentially harmful characters from the input
    return escapeshellcmd($input);
}

$mpdstatus = exec(sanitizeInput("systemctl status mpd |grep 'Active: '|sed 's/Active: //g'"));
?>
<div class="col-md-6"><?php echo trim($mpdstatus); ?></div>
