<div class="playerWrapperCover" id="coverWrapper"></div>
<div id="controlWrapper"></div>

<script>
$(document).ready(function() {
    $('#coverWrapper').load('ajax.loadCover.php');
	$('#controlWrapper').load('ajax.loadControls.php');
    var refreshId = setInterval(function() {
        $('#coverWrapper').load('ajax.loadCover.php?' + 1*new Date());
		$('#controlWrapper').load('ajax.loadControls.php?' + 1*new Date());
    }, 2000);
});
</script> 
