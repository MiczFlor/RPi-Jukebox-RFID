#!/usr/bin/php

<?php

/*
* This script is called from the command line.
* It will read all shortcut files and create a CSV file with matching pairs
* of RFID and audio folder name.
* The created CSV file starts with the line
"id","value"
* The following lines might look like this:
"0005088037","gruen-gruen-gruen"
"0005119578","o-du-lieber-augustin"
"0007831755","ein-maennlein-im-walde"
*/

/*
* Variables - that should not need changing if you do the custom install
*/

$conf = array();
$conf['path2shortcuts'] = "/home/pi/RPi-Jukebox-RFID/shared/shortcuts"; // no trailing slash
$conf['path2csvtarget'] = "/home/pi/RPi-Jukebox-RFID/misc/shortcuts-backup.csv"; // absolute path to target


// read the shortcuts used
$shortcutstemp = array_filter(glob($conf['path2shortcuts'].'/*'), 'is_file');
$shortcuts = array(); // the array with pairs of ID => foldername
// read files' content into array
foreach ($shortcutstemp as $shortcuttemp) {
    $shortcuts[basename($shortcuttemp)] = trim(file_get_contents($shortcuttemp));
}
//print "<pre>"; print_r($shortcutstemp); print "</pre>"; //???
//print "<pre>"; print_r($shortcuts); print "</pre>"; //???

$csv = "\"id\",\"value\"\n";

foreach($shortcuts as $id => $value) {
    $csv .= "\"".$id."\",\"".$value."\"\n";
}
file_put_contents($conf['path2csvtarget'], $csv);
?>