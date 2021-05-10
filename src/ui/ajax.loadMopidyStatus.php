<?php
$mopidyserverstatus = exec("echo -e status\\nclose | nc -w 1 localhost 6600 | grep 'OK MPD'| sed 's/^.*$/ACTIVE/'");
if ($mopidyserverstatus == "ACTIVE") {
$mopidystatus = "Mopidy.Server: Connected<br>Mopidy.Service: " . exec("systemctl status mopidy | grep 'Active: '| sed 's/Active: //g'");
} else {
$mopidystatus = "Mopidy.Server: Disconnected!<br>Mopidy.Service: " . exec("systemctl status mopidy | grep 'Active: '| sed 's/Active: //g'");
}
?>
          <div class="col-md-6"><?php echo trim($mopidystatus); ?></div>
