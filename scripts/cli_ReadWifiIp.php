#!/usr/bin/php
<?php
$wifiIp = exec("ifconfig wlan0 | grep \"inet \" | awk -F'[: ]+' '{ print $3 }'");
print $wifiIp;
$array = str_split($wifiIp);
foreach ($array as $char) {
 echo $char."-";
}
?>