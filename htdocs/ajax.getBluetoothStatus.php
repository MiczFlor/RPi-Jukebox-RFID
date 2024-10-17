<?php

   // Attention: user www-data needs to be of group bluetooth to get meaningful results of bluetoothctl
   // sudo usermod -G bluetooth -a www-data
   // reboot for changes to take effect!
   // Requires bluetoothctl to be installed

   function validateInput($input) {
       // Ensure the input only contains valid characters
       return preg_match('/^[a-zA-Z0-9_\-\/\.]+$/', $input);
   }

   function sanitizeInput($input) {
       // Remove any potentially harmful characters from the input
       return escapeshellcmd($input);
   }

   $btPower = trim(shell_exec(sanitizeInput("bluetoothctl show | grep -o -c 'Powered: yes'")));
   if ($btPower == 0 ) {
     print "Bluetooth adapter powered down";
   } else {

     //  If no device is connected, there will be an error message returned, which does not match
     //  with -c we either get 0 or 1 as a return result
     $btDevConnected = trim(shell_exec(sanitizeInput("bluetoothctl info | grep -o -c 'Connected: yes'")));

     if($btDevConnected == 0) {
       print "Disconnected";
     } else {  
       //  Grep'ing the MAC address
       //  \K: Keep only the matched string after \K, which must be composed of MAC addres letters
       $btDevMac = trim(shell_exec(sanitizeInput("bluetoothctl info | grep -oP -e 'Device \K[A-Fa-f\d\:]*'")));
       $btDevName = trim(shell_exec(sanitizeInput("bluetoothctl info | grep -oP 'Name: \K.*'")));
       print "Connected ($btDevName - $btDevMac)";
     }
  }

?>
