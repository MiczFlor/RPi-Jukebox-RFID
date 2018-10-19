<div id="controlVolume"></div>

<script>
$(document).ready(function() {
	$('#controlVolume').load('ajax.loadVolume.php');
	var refreshId = setInterval(function() {
		$('#controlVolume').load('ajax.loadVolume.php?' + 1*new Date());
	}, 2000);
});
</script>
