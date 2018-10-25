<?php
$mpdstatus = exec("systemctl status mpd |grep 'Active: '|sed 's/Active: //g'");
?>
          <div class="col-md-6"><?php echo trim($mpdstatus); ?></div>