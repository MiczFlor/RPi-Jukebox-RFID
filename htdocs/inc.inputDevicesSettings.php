<ul class="list-group">
  <li class="list-group-item">
	<div class="row">
		<div class="col-xs-6">
<?php
$gpiostatus = exec("/bin/systemctl status gpio-buttons.service | grep running");
if ($gpiostatus != "") {
	print 'GPIO Buttons <span class="label label-success">Enabled</span>';
	print '</div><!-- / .col-xs-6 -->';
	print '<div class="col-xs-6">';
	print "<a href='?gpiostatus=turnoff' class='btn btn-sm btn-danger'><i class='fa  fa-power-off'></i> Turn off</a>";
}
else {
	print 'GPIO Buttons <span class="label label-danger">Disabled</span>';
	print '</div><!-- / .col-xs-4 -->';
	print '<div class="col-xs-4">';
	print "<a href='?gpiostatus=turnon' class='btn btn-sm btn-success'><i class='fa fa-play'></i> Turn on</a>";
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
	print 'RFID Reader <span class="label label-success">Enabled</span>';
	print '</div><!-- / .col-xs-6 -->';
	print '<div class="col-xs-6">';
	print "<a href='?rfidstatus=turnoff' class='btn btn-sm btn-danger'><i class='fa  fa-power-off'></i> Turn off</a>";
}
else {
	print 'RFID Reader <span class="label label-danger">Disabled</span>';
	print '</div><!-- / .col-xs-4 -->';
	print '<div class="col-xs-4">';
	print "<a href='?rfidstatus=turnon' class='btn btn-sm btn-success'><i class='fa fa-play'></i> Turn on</a>";
}
?>
		</div><!-- / .col-xs-6 -->
	</div><!-- / .row -->
  </li>
</ul>
