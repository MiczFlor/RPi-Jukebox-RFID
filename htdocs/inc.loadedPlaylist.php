<script>

    $(document).ready(function () {

        function updateSongTime(time) {
            if (time) {
                const splitted = time.split(':');
                if (splitted.length == 2) {
                    $('#elapsedTime').html(formatTimeElapsedTotal(splitted[0], splitted[1]));
                }
            } else {
                $('#elapsedTime').html('');
            }
            updateChangingOutput();
        }

        function updateSongInfo(song) {
            $('#infoWrapper').html(createSongInformation(song));
            updateChangingOutput();
        }

        function updateChangingOutput() {
            updateOverallTime();
            updateChapters();
        }

        function updateOverallTime() {
            const song = JUKEBOX.playerInfo.song;
            if (song) {
                $('#overalltimeWrapper').html('<span class="badge" style="float: right">' + createOverallTimePlayed(song) + '</span>');
            }
        }

        function updateChapters() {
            const playerInfo = JUKEBOX.playerInfo;
            const chapters = playerInfo.chapters || [];
            const $chaptersSelect = $('#chapters-select');


            if (chapters.length === 0) {
                $('#chaptersWrapper').hide();
                return;
            }
            if($chaptersSelect.data('id') !== playerInfo.id) {
                updatedOptionsForChaptersSelectBox(playerInfo, $chaptersSelect, chapters);
            }
            markCurrentChapterAsSelected(playerInfo, $chaptersSelect, chapters);

            $('#chaptersWrapper').show();
        }

        function updatedOptionsForChaptersSelectBox(playerInfo, $chaptersSelect, chapters) {
            $chaptersSelect.html('');
            $chaptersSelect.data('id', playerInfo.id);
            for (var i = 0; i < chapters.length; i++) {
                var chapter = chapters[i];
                var option = document.createElement("option");
                option.value = chapters[i].name;
                option.text = chapters[i].name;
                option.setAttribute("data-start", chapter.start);
                $chaptersSelect.append(option);
            }
        }

        function markCurrentChapterAsSelected(playerInfo, $chaptersSelect, chapters) {
            var selectedIndex = 0;
            for (var i = 0; i < chapters.length; i++) {
                var elapsed = +playerInfo.elapsed;
                var start = +chapters[i].start;
                if (start <= elapsed) {
                    selectedIndex = i;
                }
            }
            $chaptersSelect[0].selectedIndex = selectedIndex;
        }


        function createSongInformation(song) {
            var songInfo = '';
            if (song) {
                const playerInfo = JUKEBOX.playerInfo;
                if (playerInfo.title != null) {

                    const title = `<strong>${playerInfo.title}<span id="chapter-current-name"></span></strong>`;

                    var artist = (playerInfo.artist) ? '<br><i>' + playerInfo.artist.replace(/;/gi, ' & ') + '</i>' : '';
                    if (!artist && playerInfo.name) {
                        artist = '<br><i>' + playerInfo.name + '</i>';
                    }
                    const album = playerInfo.album != null ? `<br>${playerInfo.album}` : '';
                    const date = playerInfo.date != null ? `<br>${playerInfo.date}` : '';
                    songInfo = [title, artist, album, date].join('') + '<div id="chapters-select-container"></div>';
                } else {
                    songInfo = `<strong>${playerInfo.file}</strong>`;
                }
            }
            return songInfo;
        }

        function createOverallTimePlayed(song) {
            var overallTime = "";
            const tracks = JUKEBOX.playlistInfo.tracks;
            const playerInfo = JUKEBOX.playerInfo;
            if (song && typeof tracks != "undefined" && tracks.length > 0) {
                const countTracksWithTime = tracks
                    .filter(track => typeof track.time != "undefined")
                    .length;
                if (countTracksWithTime) {
                    const songInt = parseInt(song);
                    const elapsedInt = typeof playerInfo.elapsed !== 'undefined' ? playerInfo.elapsed : 0;
                    const elapsed = tracks
                        .filter(track => parseInt(track.pos) < songInt)
                        .filter(track => typeof track.time != "undefined")
                        .map(track => parseInt(track.time))
                        .reduce(sum, 0) + Math.ceil(parseInt(elapsedInt));
                    const total = tracks
                        .filter(track => typeof track.time != "undefined")
                        .map(track => parseInt(track.time))
                        .reduce(sum, 0);
                    overallTime = formatTimeElapsedTotal(elapsed, total);
                }
            }
            return overallTime;
        }

        function sum(a, b) {
            return a + b
        }

        function updatePlaylistData(playlistData) {
            //console.debug(playlistData);
            $playListToggle = $("#showPlaylistToggle");
            $playListToggle.hide();
            $playlistTable = $("#playlistTable");
            $playlistTable.empty();

            if (typeof playlistData != "undefined" && typeof playlistData.tracks != "undefined" && playlistData.tracks.length > 0) {
                $playlistTable.html(playlistData.tracks
                    .map(track => createPlaylistTrack(track))
                    .reduce((a, b) => a + b, ''));
                $('#overalltimeWrapper').html('<span class="badge" style="float: right">' + createOverallTimePlayed(JUKEBOX.playerInfo.song) + '</span>');

                updateSongInfo(JUKEBOX.playerInfo.id);
                $playListToggle.show();
            }
        }

        function createPlaylistTrack(track) {
            var trackPosTemp = parseInt(track.pos, 10) + 1;
            var result = '<tr style="border-bottom: 1px solid #444;"> ' +
                '<td style="width: 40px!important; border-collapse: collapse;"> ' +
                '    <a onclick="playSongInPlaylist(' + trackPosTemp + ');" class="btn btn-success" style="margin: 3px!important;"><i class="mdi mdi-play" aria-hidden="true"></i></a>' +
                '</td> ' +
                '<td style="width: 40px!important; border-collapse: collapse;"> ' +
                '    <a onclick="removeSongFromPlaylist(' + trackPosTemp + ');" class="btn btn-danger btn-sm" style="margin: 3px!important;"><i class="mdi mdi-delete" aria-hidden="true"></i></a>' +
                '</td> ' +
                '<td style="width: 40px!important; border-collapse: collapse;"> ' +
                '    <a onclick="moveUpSongInPlaylist(' + trackPosTemp + ');" class="btn btn-warning btn-sm" style="margin: 3px!important;"><i class="mdi mdi-arrow-up-thick" aria-hidden="true"></i></a>' +
                '</td> ' +
                '<td style="width: 50px!important; border-collapse: collapse;"> ' +
                '    <a onclick="moveDownSongInPlaylist(' + trackPosTemp + ');" class="btn btn-warning btn-sm" style="margin: 3px!important;"><i class="mdi mdi-arrow-down-thick" aria-hidden="true"></i></a>' +
                '</td> ' +
                '<td style="border-collapse: collapse;">';
            if (track.title != null) {
                result += `<strong>${track.title}</strong>`;
            } else {
                result += `<strong>${track.file}</strong>`;
            }
            if (track.artist != null) {
                result += '<br><i>' + track.artist.replace(";", " and ",) + '</i>';
            }
            if (track.album != null) {
                result += `<br><font color=#7d7d7d>${track.album}`;
                if (track.date != null) {
                    result += ` (${track.date})`;
                }
                result += "</font>";
            }
            result += '</td><td style="width: 20px; border-collapse: collapse;">';
            // Livestreams and podcasts have no time length, check to suppress badge
            const time = track.time;
            if (time > 0 && time < 3600) {
                result += '<span class="badge" style="float: right; margin: 3px!important;">' + formatTimeMinutes(time) + '</span>';
            } else if (time >= 3600) {
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

<table
    style="margin-bottom: 20px; width: 100%; border-collapse: collapse; border-top: 1px solid #444; border-bottom: 1px solid #444">
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
        <td style="padding: 10px 0;border-collapse: collapse;">
            <div id="showPlaylistToggle" style="display: none"><i class="mdi mdi-playlist-play"></i> <a
                    data-toggle="collapse" href="#collapse1" class="panel-title">Show playlist</a></div>
        </td>
        <td style="padding: 10px 0;width: 50px; border-collapse: collapse;">
            <div id="overalltimeWrapper"></div>
        </td>
    </tr>
</table>
<div id="collapse1" class="panel-collapse collapse" style="margin-bottom: 40px;">
    <ul class="list-group" style="list-style: none;">
        <li>
            <div id="loadPlaylist">
                <table style="width: 100%; border-collapse: collapse; border-top: 1px solid #444;" id="playlistTable">
                </table>
            </div>
        </li>
    </ul>
</div>
