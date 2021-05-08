<?php
include("config.php");
$Audio_Folders_Path = trim(file_get_contents('../settings/Audio_Folders_Path'));
$Latest_Folder_Played = trim(file_get_contents('../settings/Latest_Folder_Played'));
$latestID = file_get_contents($conf['base_path'].'/shared/latestID.txt', true);
$onlyID = substr($latestID, 9, 10);
$temp = explode("'", "$latestID");
$onlyID = trim($temp[1]);
$shortcutready = file_get_contents($Audio_Folders_Path.'/'.$onlyID, true);
$dir = $Audio_Folders_Path."/".$shortcutready;

print "
          <input id=\"cardID\" name=\"cardID\" placeholder=\"\" class=\"form-control input-md\" type=\"text\" value=\"".$onlyID."\">
";
?>