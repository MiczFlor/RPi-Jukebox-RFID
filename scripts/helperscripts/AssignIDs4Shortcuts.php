#!/usr/bin/php
<?php

/*
* This script is called from the command line.
* It reads a CSV file and creates shortcuts for audiofolders from the file.
* It also creates a modified version of the file rfid_trigger_play.sh which controls the playout.
* As a source it uses rfid_trigger_play.sh.sample
*
* The CSV file needs to start with the line
id,value
* These will be the keys in the associated array created from the CSV file.
* The following lines might look like this:
0008861159,%CMDVOL95%
0007882996,%CMDSTOP%
0007901304,%CMDSHUTDOWN%
0008021289,%CMDNEXT%
0007910974,%CMDPREV%
0005088037,gruen-gruen-gruen
0005119578,o-du-lieber-augustin
0007831755,ein-maennlein-im-walde
* Here you can see the top five values will be used for the bash script and
* replace the placeholders in the script with the matching RFIDs to change the
* volume, stop playout, shutdown RPi, skip to next or previous track in a playlist.
* The three pairs at the bottom will create shortcuts from the RFID to an audio folder
* with the name of the second value.
*/

/*
* Variables - that should not need changing if you do the custom install
*/

$conf = array();
$conf['path2presetCSV']         = "/home/pi/RPi-Jukebox-RFID/misc/presets.csv"; // absolute path to CSV file with IDs
$conf['path2shortcuts']         = "/home/pi/RPi-Jukebox-RFID/shared/shortcuts"; // absolute path to shortcuts folder, no trailing slash
$conf['path2bashdaemonsource']  = "/home/pi/RPi-Jukebox-RFID/scripts/rfid_trigger_play.sh.sample"; // absolute path to sample file for daemon script
$conf['path2bashdaemontarget']  = "/home/pi/RPi-Jukebox-RFID/scripts/rfid_trigger_play.sh"; // absolute path to target where daemon script needs to live

$csvarray = csv_read_file2array($conf['path2presetCSV'], TRUE);
$bashfind = array(); // the value pairs that will be replaced in the bash script
$bashreplace = array(); // the value pairs that will be replaced in the bash script

/*
* Create shortcut files with matching folders
*/
foreach($csvarray as $pair) {
    // check if the pair contains values for the bash script
    if(string_startsWith($pair['value'], '%')) {
        $bashfind[] = $pair['value'];
        $bashreplace[] = $pair['id'];
    } else {
        // not for bash script
        // so create shortcut file
        $exec = "echo '".trim($pair['value'])."' > ".$conf['path2shortcuts']."/".$pair['id'];
        //print $exec."\n";
        exec($exec);
    }
}

/*
* Now replace the values in the sample script with IDs - if any
*/
//	  
$bashdaemon = file_get_contents($conf['path2bashdaemonsource']);
$bashdaemon = str_replace($bashfind, $bashreplace, $bashdaemon);
file_put_contents($conf['path2bashdaemontarget'], $bashdaemon);

function string_startsWith($haystack, $needle) {
    /*
    * returns true or false
    */
     $length = strlen($needle);
     return (substr($haystack, 0, $length) === $needle);
}

function csv_read_file2array($file, $thead = TRUE) {
  /*
  * Reads a csv file into an array.
  * The key for each set (row) will either be taken from the first row 
  * or will be 'col1', 'col2', etc.
  * This function assumes that the first row is the column header (like thead).
  * If this is not the case, pass on FALSE as the second value.
  * Examples:
  * $data = csv_read_file2array($inv['invdata']); // first csv line is column header
  * $data = csv_read_file2array($inv['invdata'], FALSE); // first csv line are values, NOT column header
  */
  $csv = array_map('str_getcsv', file($file));
  if($thead == FALSE) {
    // first line is not thead, create one
    $colcount = count($csv[0]); // number of columns
    if($colcount < 1) { // this is an error, the file was corrupt
      die("CSV file incorrect");
    } else {
      $counter = 1;
      $colhead = array();
      while($counter <= $colcount) {
        $colhead[] = "col".$counter++;
      }
      array_unshift($csv, $colhead); // add as column header
    }
  }
  array_walk($csv, function(&$a) use ($csv) {
    $a = array_combine($csv[0], $a);
  });
  array_shift($csv); // remove column header
  return $csv;
}

?>