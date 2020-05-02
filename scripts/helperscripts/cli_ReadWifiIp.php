#!/usr/bin/php
<?php
$wlanDevice = "wlan0";
//$wlanDevice = "wlp4s0"; // this is the device name on my ubuntu, just for testing 

$wifiIp = exec("sudo ifconfig ".$wlanDevice." | grep \"inet \" | awk -F'[: ]+' '{ print $3 }'");
//$wifiIp = "0.123.456.789"; // testing all possibly numbers

$array = str_split($wifiIp);
$concat = "silence-2sec.mp3|";
foreach ($array as $char) {
 $concat .= "number0".$char.".mp3|silence-0.5sec.mp3|";
}
$concat .= "silence-2sec.mp3";

// create and read mp3
exec("sudo ffmpeg -i \"concat:".$concat."\" -acodec copy WifiIp.mp3; sudo mpg123 WifiIp.mp3");
// delete mp3 after playout
exec("sudo rm WifiIp.mp3");

?>
