<script>

$(document).ready(function() {

    function updateSongTime(time) {
        if (time) {
            const splitted = time.split(':');
            if (splitted.length == 2) {
                $('#elapsedTime').html(formatTimeElapsedTotal(splitted[0], splitted[1]));
            }
        } else {
            $('#elapsedTime').html('');
        }
        updateOverallTime();
    }

    function updateSongInfo(song) {
        $('#infoWrapper').html(createSongInformation(song));
        updateOverallTime();
    }

    function updateOverallTime() {
        const song = JUKEBOX.playerInfo.song;
        if (song) {
            $('#overalltimeWrapper').html('<span class="badge" style="float: right">' + createOverallTimePlayed(song) + '</span>');
        }
    }

    function createSongInformation(songId) {
        const tracks = JUKEBOX.playlistInfo.filter(track => track.Id === songId);
        if (tracks.length > 0) {
            const track = tracks[0];
            if (track.Title != null) {
                const title = `<strong>${track.Title}</strong>`;
                const artist = '<br><i>' + track.Artist.replace(';', ' and ') + '</i>';
                const album = track.Album != null ? `<br>${track.Album}` : '';
                const date = track.Date != null ? `<br>${track.Date}` : '';
                return [title, artist, album, date].join('');
            } else {
                return `<strong>${track.file}</strong>`;
            }
        }
        return '';
    }

    function createOverallTimePlayed(song) {
        if (song && JUKEBOX.playlistInfo.length > 0) {
            const songInt = parseInt(song);
            const elapsedInt = typeof JUKEBOX.playerInfo.elapsed !== 'undefined' ? JUKEBOX.playerInfo.elapsed : 0;
            const elapsed = JUKEBOX.playlistInfo.filter(track => parseInt(track.Pos) < songInt).map(track => parseInt(track.Time)).reduce(sum, 0) + Math.ceil(parseInt(elapsedInt));
            const total = JUKEBOX.playlistInfo.map(track => parseInt(track.Time)).reduce(sum, 0);
            return formatTimeElapsedTotal(elapsed, total);
        } else {
            return '';
        }
    }

    function sum(a, b) {
        return a + b
    }

    function updatePlaylistData(playlistData) {
        $("#playlistTable").empty();
        $('#overalltimeWrapper').html('<span class="badge" style="float: right">' + createOverallTimePlayed(JUKEBOX.playerInfo.song) + '</span>');
        $("#playlistTable").html(playlistData.map(track => createPlaylistTrack(track)).reduce((a, b) => a + b, ''));
        if (playlistData.length > 0) {
            updateSongInfo(JUKEBOX.playerInfo.Id);
            $("#showPlaylistToggle").css('display', 'initial');
        } else {
            $("#showPlaylistToggle").css('display', 'none');
        }
    }

    function createPlaylistTrack(track) {
        var result = '<tr style="border-bottom: 1px solid #444;"> ' +
            '<td style="width: 70px!important; border-collapse: collapse;"> ' +
            '    <a onclick="playSongInPlaylist(' + track.Pos + ');" class="btn btn-success" style="margin: 3px!important;"><i class="mdi mdi-play" aria-hidden="true"></i></a>' +
            '</td> ' +
            '<td style="border-collapse: collapse;">';
        if (track.Title != null) {
            result += `<strong>${track.Title}</strong>`;
        } else {
            result += `<strong>${track.File}</strong>`;
        }
        if (track.Artist != null) {
            result += '<br><i>' + track.Artist.replace(";", " and ",) + '</i>';
        }
        if(track.Album != null) {
            result += `<br><font color=#7d7d7d>${track.Album}`;
            if(track.Date.trim() !== "") {
                result += ` (${track.Date})`;
            }
            result += "</font>";
        }
        result += '</td><td style="width: 20px; border-collapse: collapse;">';
        // Livestreams and podcasts have no time length, check to suppress badge
        const time = track.Time;
        if ( time > 0 && time < 3600 ) {
            result += '<span class="badge" style="float: right; margin: 3px!important;">' + formatTimeMinutes(time) + '</span>';
        } else if ( time >= 3600 ) {
            result += '<span class="badge" style="float: right; margin: 3px!important;">' + formatTimeHours(time) + '</span>';
        }
        result += '</td></tr>';
        return result;
    }

    $(document).ready(() => {
        JUKEBOX.timeListener.push(updateSongTime);
        JUKEBOX.songChangedListener.push(updateSongInfo);
        JUKEBOX.playlistDataChangedListener.push(updatePlaylistData);
    });
});
</script>

<table style="margin-bottom: 20px; width: 100%; border-collapse: collapse; border-top: 1px solid #444; border-bottom: 1px solid #444">
    <tr>
        <td style="padding: 10px 0; border-collapse: collapse;"><i class="mdi"></i>
            <span id="infoWrapper">

            </span>
        </td>
        <td style="padding: 10px 0;width: 50px; border-collapse: collapse;">
            <div id="timeWrapper">
                <span id="elapsedTime" class="badge" style="float: right"></span>
            </div>
        </td>
    </tr>
    <tr>
        <td style="padding: 10px 0;border-collapse: collapse;"><div id="showPlaylistToggle" style="display: none"><i class="mdi mdi-playlist-play"></i> <a data-toggle="collapse" href="#collapse1" class="panel-title">Show playlist</a></div></td>
        <td style="padding: 10px 0;width: 50px; border-collapse: collapse;"><div id="overalltimeWrapper"></div></td>
    </tr>
</table>
<div id="collapse1" class="panel-collapse collapse" style="margin-bottom: 40px;">
    <ul class="list-group">
        <li>
            <div id="loadPlaylist">
                <table style="width: 100%; border-collapse: collapse; border-top: 1px solid #444;" id="playlistTable">
                </table>
            </div>
        </li>
    </ul>
</div>
