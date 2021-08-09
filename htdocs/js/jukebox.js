function init() {
    JUKEBOX = {};
    // Allow observers to react to changes to playlist or songs.
    // New playlist is selected
    JUKEBOX.playlistChangedListener = [];
    // Playlist data is downloaded
    JUKEBOX.playlistDataChangedListener = [];
    JUKEBOX.songChangedListener = [];
    JUKEBOX.folderChangedListener = [];

    // Allow observers to react to player changes
    JUKEBOX.playStateListener = [];
    JUKEBOX.timeListener = [];
    JUKEBOX.volumeChangedListener = [];
    JUKEBOX.repeatChangedListener = [];
    JUKEBOX.singleChangedListener = [];

    // Track which song is currently played.
    JUKEBOX.latestInfo = {};
    // Track the current status of the player
    JUKEBOX.playerInfo = {};
    // information about the current playlist
    JUKEBOX.playlistInfo = [];
}

function loadStatusRepeat() {
    clearTimeout(JUKEBOX.timeout);
    clearInterval(JUKEBOX.interval);
    loadStatus(() => {
        var counter = 0,
        interval  = setInterval(function () {
            interpolateTime();
            if (++counter == 5) {
                clearInterval(interval);
            }
        },1000)
        JUKEBOX.interval = interval;
        JUKEBOX.timeout = setTimeout(loadStatusRepeat, 5000);
    });
}

function interpolateTime()
{
    if (JUKEBOX.playerInfo.state == "play" && JUKEBOX.playerInfo.elapsed < JUKEBOX.playlistInfo.albumLength){
        ++JUKEBOX.playerInfo.elapsed;
    }
    notify(JUKEBOX.timeListener, JUKEBOX.playerInfo.time);
}


function loadStatus(completion) {
    $.ajax({
        url: 'api/player.php',
        datatype: 'json'
    }).success(data => {
        notifyOnDataChange(data);
    }).complete(() => {
        if (completion != null) {
            completion();
        }
    });
}

function notifyOnDataChange(data) {
    const oldPlayerInfo = JUKEBOX.playerInfo;
    JUKEBOX.playerInfo = data;
    if (data.state !== oldPlayerInfo.state) {
        notify(JUKEBOX.playStateListener, data.state);
    }

    if (data.playlist !== oldPlayerInfo.playlist) {
        notify(JUKEBOX.playlistChangedListener, data.playlist);
    }

    if (data.songid !== oldPlayerInfo.songid) {
        notify(JUKEBOX.songChangedListener, data.songid);
    }

    if (data.volume !== oldPlayerInfo.volume) {
        notify(JUKEBOX.volumeChangedListener, data.volume);
    }
    if (data.repeat != oldPlayerInfo.repeat) {
        notify(JUKEBOX.repeatChangedListener, data.repeat);
    }
    if (data.single != oldPlayerInfo.single) {
        notify(JUKEBOX.singleChangedListener, data.single);
    }
    notify(JUKEBOX.timeListener, data.time);
}

function notify(listeners, data) {
    listeners.forEach(listener => listener(data));
}

function playPlaylist(playlist, recursive) {
    const json = {
            playlist,
            recursive
    };
    $.ajax({
        url: `api/playlist.php`,
        method: 'PUT',
        data: JSON.stringify(json),
        success: function() {
          var infomessage = $("#phonieboxinfomessage");
          infomessage.html('<div class="alert alert-success alert-dismissible fade in"><a href="#" class="close" data-dismiss="alert" aria-label="close">&times;</a>' + playlist.toString().replace(/^.*[\\\/]/, '') + ' ' + JUKEBOX.lang['playerFilePlayed'] + '.</div>');
          infomessage.first().hide().fadeIn(200).delay(2000).fadeOut(1000, function () { $(this).hide(); });
        }
    }).success(data => {
        loadStatus();
    });
}

function loadPlaylist() {
    $.ajax({
        url: `api/playlist.php`
    }).success(data => {
        JUKEBOX.playlistInfo = data;
        notify(JUKEBOX.playlistDataChangedListener, data);
    });
}

function playSongInPlaylist(song) {
    $.ajax({
        url: `api/playlist/song.php`,
        method: 'PUT',
        data: song.toString(),
        success: function() {
          var infomessage = $("#phonieboxinfomessage");
          infomessage.html('<div class="alert alert-success alert-dismissible fade in"><a href="#" class="close" data-dismiss="alert" aria-label="close">&times;</a>' + song.toString() + ' ' + JUKEBOX.lang['playerFilePlayed'] + '.</div>');
          infomessage.first().hide().fadeIn(200).delay(2000).fadeOut(1000, function () { $(this).hide(); });
        }
    }).success(data => {
        loadStatus();
    });
}

function removeSongFromPlaylist(song) {
    $.ajax({
        url: `api/playlist/removeSongFromPlaylist.php`,
        method: 'PUT',
        data: song.toString(),
        success: function() {
          var infomessage = $("#phonieboxinfomessage");
          infomessage.html('<div class="alert alert-danger alert-dismissible fade in"><a href="#" class="close" data-dismiss="alert" aria-label="close">&times;</a>' +  song.toString() + ' ' + JUKEBOX.lang['playerFileDeleted'] + '.</div>');
          infomessage.first().hide().fadeIn(200).delay(2000).fadeOut(1000, function () { $(this).hide(); });
        }
    }).success(data => {
        loadStatus();
    });
}

function removeSongFromPlaylist(song) {
    $.ajax({
        url: `api/playlist/removeSongFromPlaylist.php`,
        method: 'PUT',
        data: song.toString()
    }).success(data => {
        loadStatus();
    });
}

function moveUpSongInPlaylist(song) {
    $.ajax({
        url: `api/playlist/moveUpSongInPlaylist.php`,
        method: 'PUT',
        data: song.toString()
    }).success(data => {
        loadStatus();
    });
}

function moveDownSongInPlaylist(song) {
    $.ajax({
        url: `api/playlist/moveDownSongInPlaylist.php`,
        method: 'PUT',
        data: song.toString()
    }).success(data => {
        loadStatus();
    });
}

function appendFileToPlaylist(file) {
    $.ajax({
        url: `api/playlist/appendFileToPlaylist.php`,
        method: 'PUT',
        data: file.toString(),
        success: function() {
          var infomessage = $("#phonieboxinfomessage");
          infomessage.html('<div class="alert alert-success alert-dismissible fade in"><a href="#" class="close" data-dismiss="alert" aria-label="close">&times;</a>' + file.toString().replace(/^.*[\\\/]/, '') + ' ' + JUKEBOX.lang['playerFileAdded'] + '.</div>');
          infomessage.first().hide().fadeIn(200).delay(2000).fadeOut(1000, function () { $(this).hide(); });
        }
    }).success(data => {
        loadStatus();
    });
}

function playSingleFile(file) {
    $.ajax({
        url: `api/playlist/playsinglefile.php`,
        method: 'PUT',
        data: file.toString(),
        success: function() {
          var infomessage = $("#phonieboxinfomessage");
          infomessage.html('<div class="alert alert-success alert-dismissible fade in"><a href="#" class="close" data-dismiss="alert" aria-label="close">&times;</a>' + file.toString().replace(/^.*[\\\/]/, '') + ' ' + JUKEBOX.lang['playerFilePlayed'] + '.</div>');
          infomessage.first().hide().fadeIn(200).delay(2000).fadeOut(1000, function () { $(this).hide(); });
        }
    }).success(data => {
        loadStatus();
    });
}

function executePlayerCommand(command, completion, value) {
    hideApiError();
    clearTimeout(JUKEBOX.timeout);
    $.ajax({
        url: 'api/player.php',
        method: 'PUT',
        contentType: "application/json; charset=utf-8",
        data: JSON.stringify({ 'command': command, "value": arguments.length === 3 ? value : null })
    }).success(data => {
         if (completion != null) {
             completion(data);
         }
     }).error(error => {
         $("#api-alert").html(`An error occured: ${error.responseText}`);
         showApiError();
     }).complete(data => {
        loadStatusRepeat();
     });
}

/**
 * Although there is a playout_controls.sh command "playernextchapter" it is implemented manually to keep the ui responsive
 */
function nextChapter() {
    gotoChapter($('#chapters-select').find('option:selected').next());
}

/**
 * Although there is a playout_controls.sh command "playerprevchapter" it is implemented manually to keep the ui responsive
 */
function previousChapter() {
    var timerSeconds = 5;
    var playerInfo = JUKEBOX.playerInfo;
    var elapsed = +playerInfo.elapsed;
    var $selectedChapter = $('#chapters-select').find('option:selected');
    var selectedChapterStart = +$selectedChapter.data('start');

    // if chapter is playing for more than 5 seconds return to start of chapter instead of going to the previous one
    // to keep responsive during the ajax requests, set a timer that blocks this behavior after the first trigger
    if(elapsed - selectedChapterStart > timerSeconds && !this.timerActive) {
        gotoChapter($selectedChapter);
        this.timerActive = true;
        window.setTimeout(() => {
            this.timerActive = false;
        }, timerSeconds*1000 + 1);

    } else {
        gotoChapter($selectedChapter.prev());
    }
}

/**
 * Will only change the selected item and trigger change - see onChangeChapter for event handler
 * @param chapter
 */
function gotoChapter(chapter) {
    if(chapter.length !== 0) {
        $('#chapters-select').val(chapter.val()).change();
    }
}

function onChangeChapter() {
    const $selectedOption = $('#chapters-select').find('option:selected');

    if ($selectedOption.length === 0) {
        return;
    }
    // this is not 100% accurate, but floats are not supported by mpc to seek a position
    const seekPosition = $selectedOption.data('start');
    executePlayerCommand("seekPosition", null, seekPosition);
}

function volumeUp() {
    executePlayerCommand('volumeup', () => {
        loadVolume()
    });
}

function volumeDown() {
    executePlayerCommand('volumedown', () => {
        loadVolume()
    });
}

function loadVolume() {
    $.ajax({
        url: 'api/volume.php',
        method: 'GET'
    }).success(data => {
        displayVolume(data);
     });
}

function stop() {
    pause();
    executePlayerCommand('stop');
}

function toggleShuffle(element) {
    togglePlaylistCommand(element, 'shuffle')
}

function toggleResume(element) {
    console.log("toggle resume");
    console.log(element);
    togglePlaylistCommand(element, 'resume')
}

function toggleSingle(element) {
    togglePlaylistCommand(element, 'single')
}

function togglePlaylistCommand(element, toggleAttributeName) {
    const attribute = $(element).attr(toggleAttributeName);
    const newAttributeValue = attribute === 'true' ? 'false' : 'true';
    const playlist = $(element).attr('playlist');
    hideApiError();
    const jsonData = { playlist };
    jsonData[toggleAttributeName] = newAttributeValue;

    $.ajax({
        url: 'api/playlist/' + toggleAttributeName + '.php',
        method: 'PUT',
        contentType: "application/json; charset=utf-8",
        data: JSON.stringify(jsonData)
    }).success(data => {
        $(element).attr(toggleAttributeName, newAttributeValue);
        if (newAttributeValue == 'true') {
            $(element).html(JUKEBOX.lang['global' + capitalizeFirstLetter(toggleAttributeName)] + ": " + JUKEBOX.lang['globalOn'] + "<i class='mdi mdi-toggle-switch-off-outline' aria-hidden='true'/>");
            $(element).attr('class', 'btn btn-success');
        } else {
            $(element).html(JUKEBOX.lang['global' + capitalizeFirstLetter(toggleAttributeName)] + ": " + JUKEBOX.lang['globalOff'] + "<i class='mdi mdi-toggle-switch' aria-hidden='true'/>");
            $(element).attr('class', 'btn btn-warning');
        }
     }).error(error => {
         $("#api-alert").html(`An error occured: ${error.responseText}`);
         showApiError();
     });
}

function capitalizeFirstLetter(string) {
    return string.charAt(0).toUpperCase() + string.slice(1);
}

function formatTimeElapsedTotal(elapsedInSeconds, totalInSeconds) {
    if (!isNaN(elapsedInSeconds) || !isNaN(totalInSeconds)) {

        const elapsedInSecondsInt = parseInt(elapsedInSeconds);
        const totalInSecondsInt = parseInt(totalInSeconds);
        if (totalInSecondsInt === 0) {
            if (elapsedInSecondsInt >= 3600) {
                return formatTimeHours(elapsedInSecondsInt);
            } else {
                return formatTimeMinutes(elapsedInSecondsInt);
            }
        }
        if (totalInSecondsInt >= 3600) {
            return formatTimeHours(elapsedInSecondsInt) + ' / ' + formatTimeHours(totalInSecondsInt);
        } else {
            return formatTimeMinutes(elapsedInSecondsInt) + ' / ' + formatTimeMinutes(totalInSecondsInt);
        }
    }
}

function formatTimeMinutes(timeInSeconds) {
    const seconds = timeInSeconds % 60;
    const minutes = (Math.floor(timeInSeconds / 60) % 60);
    const hours = Math.floor(timeInSeconds / 3600);

    const secondsString = formatWithDigits(seconds, 2);
    const minutesString = formatWithDigits(minutes, 2);
    const hoursString = formatWithDigits(hours, 2);
    return [minutesString, secondsString].join(' : ');
}

function formatTimeHours(timeInSeconds) {
    const seconds = timeInSeconds % 60;
    const minutes = (Math.floor(timeInSeconds / 60) % 60);
    const hours = Math.floor(timeInSeconds / 3600);

    const secondsString = formatWithDigits(seconds, 2);
    const minutesString = formatWithDigits(minutes, 2);
    const hoursString = formatWithDigits(hours, 2);
    return [hoursString, minutesString, secondsString].join(' : ');
}

function formatWithDigits(number, digits) {
    return (number).toLocaleString('en-US', {minimumIntegerDigits: digits, useGrouping:false})
}

init();
loadStatusRepeat();

JUKEBOX.playlistChangedListener.push(loadPlaylist);
