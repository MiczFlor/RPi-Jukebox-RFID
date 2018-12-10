<?php
if($ShowCover == "ON") {
    print '<div class="playerWrapperCover" id="coverWrapper"></div>';
}
?>

<div id="controlWrapper"></div>

<script>
$(document).ready(function() {
<?php
if($ShowCover == "ON") {
    print "
    $('#coverWrapper').load('ajax.loadCover.php');";
}
?>

	$('#controlWrapper').load('ajax.loadControls.php');
    var refreshId = setInterval(function() {
<?php
if($ShowCover == "ON") {
    print "
        $('#coverWrapper').load('ajax.loadCover.php?' + 1*new Date());";
}
?>

		$('#controlWrapper').load('ajax.loadControls.php?' + 1*new Date());
    }, 2000);
});
</script> 
