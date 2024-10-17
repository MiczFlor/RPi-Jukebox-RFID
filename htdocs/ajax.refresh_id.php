<?php
include("config.php");

function validateInput($input) {
    // Ensure the input only contains valid characters
    return preg_match('/^[a-zA-Z0-9_\-\/\.]+$/', $input);
}

function sanitizeInput($input) {
    // Remove any potentially harmful characters from the input
    return htmlspecialchars($input, ENT_QUOTES, 'UTF-8');
}

$Audio_Folders_Path = trim(file_get_contents('../settings/Audio_Folders_Path'));
$Latest_Folder_Played = trim(file_get_contents('../settings/Latest_Folder_Played'));
$latestID = file_get_contents($conf['base_path'].'/shared/latestID.txt', true);
$onlyID = substr($latestID, 9, 10);
$temp = explode("'", "$latestID");
$onlyID = trim($temp[1]);
$shortcutready = file_get_contents($Audio_Folders_Path.'/'.$onlyID, true);
$dir = $Audio_Folders_Path."/".$shortcutready;

print "
          <input id=\"cardID\" name=\"cardID\" placeholder=\"\" class=\"form-control input-md\" type=\"text\" value=\"".sanitizeInput($onlyID)."\">
";
?>
