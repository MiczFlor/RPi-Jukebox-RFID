<?php
$mopidystatus = exec("sudo systemctl status mopidy |grep 'Active: '|sed 's/Active: //g'");
?>
          <div class="col-md-6"><?php echo trim($mopidystatus); ?></div>
