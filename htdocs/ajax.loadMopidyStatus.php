<?php
function validateInput($input) {
    // Ensure the input only contains valid characters
    return preg_match('/^[a-zA-Z0-9_\-\/\.]+$/', $input);
}

function sanitizeInput($input) {
    // Remove any potentially harmful characters from the input
    return escapeshellcmd($input);
}

$mopidyserverstatus = exec(sanitizeInput("echo -e status\\nclose | nc -w 1 localhost 6600 | grep 'OK MPD'| sed 's/^.*$/ACTIVE/'"));
if ($mopidyserverstatus == "ACTIVE") {
    $mopidystatus = "Mopidy.Server: Connected<br>Mopidy.Service: " . exec(sanitizeInput("systemctl status mopidy | grep 'Active: '| sed 's/Active: //g'"));
} else {
    $mopidystatus = "Mopidy.Server: Disconnected!<br>Mopidy.Service: " . exec(sanitizeInput("systemctl status mopidy | grep 'Active: '| sed 's/Active: //g'"));
}
?>
<div class="col-md-6"><?php echo trim($mopidystatus); ?></div>
