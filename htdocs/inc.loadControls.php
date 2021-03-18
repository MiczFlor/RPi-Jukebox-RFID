
<div class="playerWrapper">
    <a onclick="executePlayerCommand('seekBack')" class='btn btn-player-l'
        title='<?php print $lang['playerSeekBack']; ?>'><i
        class="mdi mdi-24px mdi-replay"></i></a>
    <a onclick="executePlayerCommand('prev')" class='btn btn-player-l'
        title='<?php print $lang['playerSkipPrev']; ?>'><i
        class="mdi mdi-48px mdi-rewind"></i></a>

<?php

print '<a id="play" onclick="play();" class="btn btn-player-xl" title="' . $lang['playerPlayPause'] . '" style="display: none"><i class="mdi mdi-72px mdi-play"></i></a>';
print '<a id="pause" onclick="pause();" class="btn btn-player-xl" title="' . $lang['playerPlayPause'] . '" style="display: none"><i class="mdi mdi-72px mdi-pause"></i></a>';

?>

<a onclick="executePlayerCommand('next')" class='btn btn-player-l'
        title='<?php print $lang['playerSkipNext']; ?>'><i
        class="mdi mdi-48px mdi-fast-forward"></i></a> <a
        onclick="executePlayerCommand('seekAhead')" class='btn btn-player-l'
        title='<?php print $lang['playerSeekAhead']; ?>'><i
        class="mdi mdi-24px mdi-flip-h mdi-replay"></i></a>


    <div id="chaptersWrapper" style="display:none;">
        <a onclick="previousChapter()" class='btn btn-player-l'
           title='<?php print $lang['playerSkipPrev']; ?>'><i
                class="mdi mdi-48px mdi-rewind"></i></a>
        <select onchange="onChangeChapter();" name="chapters-select" id="chapters-select" class="selectpicker form-control" initialized="false" style="width:30vw;max-width:200px;display:inline;text-align-last:center;"></select>
        <a onclick="nextChapter()" class='btn btn-player-l'
           title='<?php print $lang['playerSkipNext']; ?>'><i
                class="mdi mdi-48px mdi-fast-forward"></i></a>
    </div>

</div>
<!-- ./playerWrapper -->
<div class="playerWrapperSub">
    <div class="btn-group controlVolumeUpDown" role="group"
        aria-label="volume" style="margin-bottom: 0.5em;">
        <!--a href="#collapsePlaylist" class="btn btn-lg collapsed" role="button" data-toggle="collapse" aria-expanded="false" aria-controls="collapseExample" m="1"><i class="mdi mdi-playlist-play"></i></a-->
        <a onclick="executePlayerCommand('replay');" class='btn  btn-lg'
            title='<?php print $lang['playerReplay']; ?>'><i
            class='mdi mdi-backup-restore'></i></a>
        <!-- currently unused: -->
        <!--a href='?player=replay' class='btn btn-default btn-success btn-lg'><i class='mdi mdi-loop'></i></a-->
        <!--a href="?player=random" class="btn  btn-lg"><i class="mdi mdi-shuffle"></i></a-->
            <?php
            print '<a id="repeatPlaylist" onclick="repeatSingle();" class="btn btn-lg" title="' . $lang['playerLoop'] . ': ' . $lang['globalList'] . '" style="display: none"><i class="mdi mdi-repeat"></i> ' . $lang['globalList'] . '</a>';
            print '<a id="repeatSingle" onclick="repeatOff();" class="btn  btn-lg" title="' . $lang['playerLoop'] . ": " . $lang['globalTrack'] . '" style="display: none"><i class="mdi mdi-repeat-once"></i> ' . $lang['globalTrack'] . '</a>';
            print '<a id="repeatOff" onclick="repeatPlaylist();" class="btn btn-lg" title="' . $lang['playerLoop'] . ': ' . $lang['globalOff'] . '" style="display: none"><i class="mdi mdi-repeat-off"></i> ' . $lang['globalOff'] . '</a>';
            print '<a id="stop" onclick="stop();" class="btn  btn-lg" title="' . $lang['playerStop'] . '"><i class="mdi mdi-stop"></i></a>';
            ?>
        </div>
    <!-- ./btn-group -->
<?php
/*
 * <a href="#collapseVolume" class="btn btn-lg collapsed" data-toggle="collapse" aria-expanded="false" aria-controls="collapseExample" m="1"><i class="mdi mdi-volume-high"></i></a>
 *
 * <div class="collapse well" id="collapseVolume" aria-expanded="false" style="height: 0px;">
 */
?>
       <div class="btn-group controlVolumeUpDown" role="group"
        aria-label="volume" style="margin-bottom: 0.5em;">
<?php
        $muted = file_exists('../settings/Audio_Volume_Level');
        print '<a id="muted" onclick="unMute();" class="btn  btn-lg" title="' . $lang['playerMute'] . '" style="display:' . ($muted ? 'initial' : 'none') . '"><i class="mdi mdi-volume-off"></i></a>';
        print '<a id="unmuted" onclick="mute();" class="btn  btn-lg" title="' . $lang['playerMute'] . '" style="display:' . (! $muted ? 'initial' : 'none') . '"><i class="mdi mdi-volume-high"></i></a>';
?>

            <a onclick="volumeDown();" class='btn  btn-lg'
            title='<?php print $lang['playerVolDown']; ?>'><i
            class='mdi mdi-volume-minus'></i></a> <a onclick="volumeUp();"
            class='btn  btn-lg' title='<?php print $lang['playerVolUp']; ?>'><i
            class='mdi mdi-volume-plus'></i></a>
    </div>
</div>
<script>

    function play() {
        if (JUKEBOX.playerInfo.playlistlength === '0') {
            // no playlist currently selected, we will play the latest playlist
            $.ajax({
                url: 'api/latest.php'
            }).success((data) => {
                if (data.playlist != null) {
                    playPlaylist(data.playlist, 'false');
                }
            });
        } else {
            executePlayerCommand('play', () => {
                $('#play').css('display', 'none');
                $('#pause').css('display', 'inline-block');
            });
        }
    }

    function pause() {
        clearInterval(JUKEBOX.interval);
        executePlayerCommand('pause', () => {
            $('#play').css('display', 'inline-block');
            $('#pause').css('display', 'none');
        });
    }

    function repeatSingle() {
        executePlayerCommand('single', () => {
            $('#repeatPlaylist').css('display', 'none');
            $('#repeatSingle').css('display', 'initial');
            $('#repeatOff').css('display', 'none');
        });
    }

    function repeatPlaylist() {
        executePlayerCommand('repeat', () => {
            $('#repeatPlaylist').css('display', 'initial');
            $('#repeatSingle').css('display', 'none');
            $('#repeatOff').css('display', 'none');
        });
    }

    function repeatOff() {
        executePlayerCommand('repeatoff', () => {
            $('#repeatPlaylist').css('display', 'none');
            $('#repeatSingle').css('display', 'none');
            $('#repeatOff').css('display', 'initial');
        });
    }

    function mute() {
        executePlayerCommand('mute', () => {
            $('#muted').css('display', 'initial');
            $('#unmuted').css('display', 'none');
        });
    }

    function unMute() {
        executePlayerCommand('mute', () => {
            $('#muted').css('display', 'none');
            $('#unmuted').css('display', 'initial');
        });
    }

    function showApiError() {
         $("#api-alert").css('display', 'block');
    }

    function hideApiError() {
         $("#api-alert").css('display', 'none');
    }

    function updatePlayerState(state) {
        if (state === 'play') {
            $('#play').css('display', 'none');
            $('#pause').css('display', 'inline-block');
        } else {
            $('#play').css('display', 'inline-block');
            $('#pause').css('display', 'none');
        }
    }

    function updateRepeatState() {
        if (JUKEBOX.playerInfo.single === '0' && JUKEBOX.playerInfo.repeat === '1') {
            $('#repeatOff').css('display', 'none');
            $('#repeatPlaylist').css('display', 'initial');
            $('#repeatSingle').css('display', 'none');
 	    } else if (JUKEBOX.playerInfo.single === '1' && JUKEBOX.playerInfo.repeat === '1') {
            $('#repeatOff').css('display', 'none');
            $('#repeatPlaylist').css('display', 'none');
            $('#repeatSingle').css('display', 'initial');
        } else {
            $('#repeatPlaylist').css('display', 'none');
            $('#repeatSingle').css('display', 'none');
            $('#repeatOff').css('display', 'initial');
        }
    }

    $(document).ready(() => {
        JUKEBOX.playStateListener.push(updatePlayerState);
        JUKEBOX.repeatChangedListener.push(updateRepeatState);
        JUKEBOX.singleChangedListener.push(updateRepeatState);
    });

</script>
<!-- ./playerWrapper -->
