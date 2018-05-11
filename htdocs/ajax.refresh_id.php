<?php
include("config.php");
$latestID = file_get_contents($conf['base_path'].'/shared/latestID.txt', true);
$onlyID = substr($latestID, 9, 10);
$temp = explode("'", "$latestID");
$onlyID = trim($temp[1]);
$shortcutready = file_get_contents($conf['base_path'].'/shared/shortcuts/'.$onlyID, true);
$dir = $conf['base_path']."/shared/audiofolders/".$shortcutready;

print "
          <input id=\"cardID\" name=\"cardID\" placeholder=\"\" class=\"form-control input-md\" type=\"text\" value=\"".$onlyID."\">
";
?>