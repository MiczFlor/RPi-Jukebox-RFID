<?php
include("config.php");
$pathSettings = realpath('../settings/');
if(file_exists($pathSettings.'/cover.jpg')) { 
    print '<center>';
    print '<img class="img-responsive img-thumbnail" src="image.php?img='.$pathSettings.'/cover.jpg" alt=""/>';
    print '</center>';
} else {
    print "";
}
?>