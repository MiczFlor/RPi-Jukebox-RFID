
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

include("inc.header.php");

/*
* Variables - that should not need changing if you do the custom install
*/

$csv = "\"id\",\"value\"\n";
$shortcuts = array();
$conf = array();
// path to script folder from github repo on RPi
$conf['shortcuts_abs'] = realpath(getcwd().'/../shared/shortcuts');
$conf['settings_abs'] = realpath(getcwd().'/../settings');

/******************************************
* read RFID trigger commands already in use
*/
$rfidUsedRaw = "";
$fn = fopen($conf['settings_abs']."/rfid_trigger_play.conf","r");
while(! feof($fn))  {
    $result = fgets($fn);
    if(
        !startsWith($result, "#")           // ignore comments
        && !endsWith(trim($result), "%\"")  // ignore placeholders like "%CMDSEEKBACK%"
        && trim($result) != ""              // ignore empty lines
    ) {
        $rfidUsedRaw .= $result."\n";
    }
}
fclose($fn);
$rfidUsedArr = parse_ini_string($rfidUsedRaw);
foreach ($rfidUsedArr as $key => $value) {
    $shortcuts[$value] = "%" . $key . "%";
}
/******************************************/

// read the shortcuts used
$shortcutstemp = array_filter(glob($conf['shortcuts_abs'].'/*'), 'is_file');
// read files' content into array
foreach ($shortcutstemp as $shortcuttemp) {
    if(basename($shortcuttemp) != "placeholder") {
        $shortcuts[basename($shortcuttemp)] = trim(file_get_contents($shortcuttemp));
    }
}
//print "<pre>"; print_r($shortcutstemp); print "</pre>"; //???
//print "<pre>"; print_r($shortcuts); print "</pre>"; //???

foreach($shortcuts as $id => $value) {
    $csv .= "\"".$id."\",\"".$value."\"\n";
}
//file_put_contents($conf['path2csvtarget'], $csv);

/**/
$filename = "PhonieboxRFID-" . date("Y-m-d") . "_" . date("G-i-s") . ".csv";
header('Content-Disposition: attachment; filename='.$filename);
header('Content-Type: text/csv');  
header('Content-Length: ' . strlen($csv));
header('Connection: close');
/**/

print $csv;

?>