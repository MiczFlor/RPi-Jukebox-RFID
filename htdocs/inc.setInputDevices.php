<ul class="list-group">
  <li class="list-group-item">
	<div class="row">
		<div class="col-xs-6">
<?php
$gpiostatus = exec("/bin/systemctl status gpio-buttons.service | grep running");
if ($gpiostatus != "") {
	print $lang['globalGpioButtons'].' <span class="label label-success">'.$lang['globalEnabled'].'</span>';
	print '</div><!-- / .col-xs-6 -->';
	print '<div class="col-xs-6">';
	print "<a href='?gpiostatus=turnoff' class='btn btn-sm btn-danger'><i class='fa  fa-power-off'></i> ".$lang['globalSwitchOff']."</a>";
}
else {
	print $lang['globalGpioButtons'].' <span class="label label-danger">'.$lang['globalDisabled'].'</span>';
	print '</div><!-- / .col-xs-4 -->';
	print '<div class="col-xs-4">';
	print "<a href='?gpiostatus=turnon' class='btn btn-sm btn-success'><i class='fa fa-play'></i> ".$lang['globalSwitchOn']."</a>";
}
?>
		</div><!-- / .col-xs-6 -->
	</div><!-- / .row -->
  </li>

  <li class="list-group-item">
	<div class="row">
		<div class="col-xs-6">
<?php
$rfidstatus = exec("/bin/systemctl status rfid-reader.service | grep running");
if ($rfidstatus != "") {
	print $lang['globalRfidReader'].' <span class="label label-success">'.$lang['globalEnabled'].'</span>';
	print '</div><!-- / .col-xs-6 -->';
	print '<div class="col-xs-6">';
	print "<a href='?rfidstatus=turnoff' class='btn btn-sm btn-danger'><i class='fa  fa-power-off'></i> ".$lang['globalSwitchOff']."</a>";
}
else {
	print $lang['globalRfidReader'].' <span class="label label-danger">'.$lang['globalDisabled'].'</span>';
	print '</div><!-- / .col-xs-4 -->';
	print '<div class="col-xs-4">';
	print "<a href='?rfidstatus=turnon' class='btn btn-sm btn-success'><i class='fa fa-play'></i> ".$lang['globalSwitchOn']."</a>";
}
?>
		</div><!-- / .col-xs-6 -->
	</div><!-- / .row -->
  </li>
</ul>
