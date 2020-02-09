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
    loadStatus(() => {
        setTimeout(loadStatusRepeat, 5000);
    });
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
        data: JSON.stringify(json)
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
        data: song.toString()
    }).success(data => {
        loadStatus();
    });
}

function appendFileToPlaylist(file) {
    $.ajax({
        url: `api/playlist/appendfiletoplaylist.php`,
        method: 'PUT',
        data: file.toString()
    }).success(data => {
        loadStatus();
    });
}

function playSingleFile(file) {
    $.ajax({
        url: `api/playlist/playsinglefile.php`,
        method: 'PUT',
        data: file.toString()
    }).success(data => {
        loadStatus();
    });
}

function executePlayerCommand(command, completion) {
    hideApiError();
    $.ajax({
        url: 'api/player.php',
        method: 'PUT',
        contentType: "application/json; charset=utf-8",
        data: JSON.stringify({ 'command': command })
    }).success(data => {
         if (completion != null) {
             completion(data);
         }
     }).error(error => {
         $("#api-alert").html(`An error occorured: ${error.responseText}`);
         showApiError();
     });
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
