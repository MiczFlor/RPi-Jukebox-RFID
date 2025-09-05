<?php
include("config.php");

// Read the latest scanned RFID card ID
$latestID = file_get_contents($conf['base_path'].'/shared/latestID.txt', true);
$onlyID = substr($latestID, 9, 10);
$temp = explode("'", "$latestID");
$onlyID = trim($temp[1]);

// Get the audio folder associated with this RFID card
$Audio_Folders_Path = trim(file_get_contents('../settings/Audio_Folders_Path'));
$shortcutready = "";
if (file_exists($Audio_Folders_Path.'/'.$onlyID)) {
    $shortcutready = file_get_contents($Audio_Folders_Path.'/'.$onlyID, true);
}

// Display the RFID field with compact styling for the new alarm row
print "<input id=\"new-alarm-sound\" name=\"new-alarm-sound\" placeholder=\"Scan RFID card\" class=\"form-control input-sm\" type=\"text\" value=\"".$onlyID."\" readonly>";
?> 