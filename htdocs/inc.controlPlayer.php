
<?php
/*
if(file_exists($conf['base_path'].'/shared/audiofolders/Suli Pushban/cover.jpg')) { 
    print '<div class="playerWrapperCover"><center>';
    print '<img class="img-responsive img-thumbnail" src="image.php?img='.$conf['base_path'].'/shared/audiofolders/Suli Pushban/cover.jpg" alt="Suli Pushban"/>';
    print '</center></div>';
}
*/
?>
<div class="playerWrapper">
    <!--a href='?player=seekBack15' class='btn btn-player-l'><i class="mdi mdi-24px mdi-replay"></i></a-->
    <a href='?player=prev' class='btn btn-player-l'><i class="mdi mdi-48px mdi-rewind"></i></a>

<?php
    if (array_key_exists('state', $playerStatus) && $playerStatus['state'] === 'play') {
        print '<a href="?player=pause" class="btn btn-player-xl"><i class="mdi mdi-72px mdi-pause"></i></a>';
    }
    else {
        print '<a href="?player=play" class="btn btn-player-xl"><i class="mdi mdi-72px mdi-play"></i></a>';
    }
?>

    <a href='?player=next' class='btn btn-player-l' ><i class="mdi mdi-48px mdi-fast-forward"></i></a>
    <!--a href='?player=seekForward15' class='btn btn-player-l'><i class="mdi mdi-24px mdi-flip-h mdi-replay"></i></a-->

</div><!-- ./playerWrapper -->
<div class="playerWrapper">
        <div class="btn-group controlVolumeUpDown" role="group" aria-label="volume" style="margin-bottom:0.5em;">
            <!--a href="#collapsePlaylist" class="btn btn-lg collapsed" role="button" data-toggle="collapse" aria-expanded="false" aria-controls="collapseExample" m="1"><i class="mdi mdi-playlist-play"></i></a-->
            <a href='?player=replay' class='btn  btn-lg' title='<?php print $lang['globalReplay']; ?>'><i class='mdi mdi-backup-restore'></i></a>
<!-- currently unused: -->
<!--a href='?player=replay' class='btn btn-default btn-success btn-lg'><i class='mdi mdi-loop'></i></a-->
<!--a href="?player=random" class="btn  btn-lg"><i class="mdi mdi-shuffle"></i></a-->
<?php
    if ($playerStatus['repeat'] == "0") {
        print '<a href="?player=repeat" class="btn btn-lg" title="'.$lang['globalLoop'].': '.$lang['globalOff'].'"><i class="mdi mdi-repeat-off"></i> '.$lang['globalOff'].'</a>'; 
    }
    elseif ($playerStatus['single'] == "1") {
        print '<a href="?player=repeatoff" class="btn  btn-lg" title="'.$lang['globalLoop'].": ".$lang['globalTrack'].'"><i class="mdi mdi-repeat-once"></i> '.$lang['globalTrack'].'</a>'; 
    }
    else {
        print '<a href="?player=single" class="btn  btn-lg" title="'.$lang['globalLoop'].': '.$lang['globalList'].'"><i class="mdi mdi-repeat"></i> '.$lang['globalList'].'</a>'; 
    }
    if (array_key_exists('state', $playerStatus)) {
        print '         <a href="?stop=true" class="btn  btn-lg"><i class="mdi mdi-stop"></i></a>';
    }
?>
        </div><!-- ./btn-group -->
<?php
include("inc.controlVolumeUpDown.php");
?>        
</div><!-- ./playerWrapper -->
