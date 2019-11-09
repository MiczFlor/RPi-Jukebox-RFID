<?php
if($ShowCover == "ON") {
    echo '<div class="playerWrapperCover" id="coverWrapper">';
    include('inc.loadCover.php');
    echo '</div>';
}
?>

<div id="controlWrapper">
<?php
    include('inc.loadControls.php');
?>
</div>
