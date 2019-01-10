<?php

$debug = "false"; // true or false
//include("inc.langLoad.php");
include("config.php");
include("func.php");
// path to settings folder from github repo on RPi
$conf['settings_abs'] = realpath(getcwd().'/../settings/');
$Audio_Folders_Path = realpath(trim(file_get_contents($conf['settings_abs'].'/Audio_Folders_Path')));
//print $_GET['rss'];

/* $sortby sets the order in which tracks are listed. */
$sortby = "filedesc"; 
/*
    Options: 
    "newest" = newest on top
    "oldest" = oldest on top
    "filedesc" = alphabetically descending
    "fileasc" = alphabetically ascending
*/

// replace certain characters that are not accepted by some podcast apps
$find = array("/ä/","/ö/","/ü/","/Ä/","/Ö/","/Ü/","/ß/", "/'/");
$replace = array("ae","oe","ue","Ae","Oe","Ue","ss", "");
/*
* http://stackoverflow.com/questions/10152894/php-replacing-special-characters-like-%C3%A0-a-%C3%A8-e
*  echo iconv('UTF-8', 'ISO-8859-1//TRANSLIT//IGNORE', $string);
*    // output: ABBASABAD
*    // Yay! That's what I wanted!
*/

/*****************************************************************************************/

if(isset($_GET['rss'])) {
    $filesMp3 = unserialize($_GET['rss']);
    $title = urldecode($_GET['title']);
    phoniepodcastxml($filesMp3, $title);
} else {
    $file = realpath($_GET['file']);
    if(startsWith($file, $Audio_Folders_Path)) {
        # starts with == file found
        header('Content-Description: File Transfer');
        header('Content-Type: media/mpeg');
        header('Content-Disposition: attachment; filename="'.basename($file).'"');
        header('Expires: 0');
        header('Cache-Control: must-revalidate');
        header('Pragma: public');
        header('Content-Length: ' . filesize($file));
        readfile($file);
        exit;
    } else {
        print "file not found";
        die;
    }
}

function phoniepodcastxml($filesMp3, $title) {
  global $sortby;
  $conf['url_abs']    = "http://".$_SERVER['HTTP_HOST'].$_SERVER['PHP_SELF']; // URL to PHP_SELF
  // get "now" time for timestamp in xml feed, because the publishing time will order the list e.g. on iOS Podcast
  $now = time();
  header('Content-type: text/xml', true);

  //$channeltitle = substr($loc['mp3basefolder'], strlen($loc['scriptbasefolder']));

  print"<?xml version='1.0' encoding='UTF-8'?>";
  print "
  <rss xmlns:itunes='http://www.itunes.com/DTDs/Podcast-1.0.dtd' version='2.0'>";
  print "
  <channel>
    <title>".$title."</title>
    <link>".$conf['url_abs']."/rss-mp3.php?rss=".serialize($filesMp3)."</link>
    <itunes:author>Phoniebox</itunes:author>
  ";
  
  // go through files and create <item> for podcast
  foreach ($filesMp3 as $fileMp3) {
/*
    // set empty array for metadata
    $iteminfo = array(
      "TPE1" => "",
      "TIT2" => "",
      "WOAF" => "",
      "Filename" => ""
    );
    // read id3 from shell command
    $idtag = explode("\n",shell_exec("id3v2 -R $fileMp3"));
    foreach($idtag as $line) {
      // to to match key => value from each line
      preg_match("/((\w+): (.*))/", $line, $results);
      // if ID3 tag found, results will return four values
      if(count($results) == 4) {
        $iteminfo[$results[2]] = $results[3];
      }
    }
    $filename = substr($fileMp3, 5);
    // if title too short, use filename as title
    if (strlen($iteminfo['TIT2']) < 2) {
    	 $iteminfo['TIT2'] = $filename;
    }
*/

    print "
    <item>
      <title>".basename($fileMp3)."</title>
      <itunes:author>Phoniebox</itunes:author>
      <itunes:subtitle>RSS feed with local files</itunes:subtitle>
      <description>".basename($fileMp3)." | Recorded: ".date ("r", filemtime($fileMp3))."</description>
      <enclosure url=\"".$conf['url_abs']."?file=".$fileMp3."\" length=\"".filesize($fileMp3)."\" type=\"audio/mpeg\"/>
      <guid>".$fileMp3."</guid>
      <pubDate>".date ("r", filemtime($fileMp3))."</pubDate>
    </item>";
  }

  print"
  </channel>

  </rss>";
}


?>


