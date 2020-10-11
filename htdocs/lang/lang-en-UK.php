<?php
$lang = array();

$lang['globalEdit'] = "Edit";
$lang['globalResume'] = "Resume";
$lang['globalPassword'] = "Password";
$lang['globalOff'] = "OFF";
$lang['globalOn'] = "ON";
$lang['globalSingle'] = "Single";
$lang['globalTrack'] = "Track";
$lang['globalList'] = "List";
$lang['globalPlaylist'] = "Playlist";
$lang['globalCardId'] = "Card RFID ID";
$lang['globalRFIDCard'] = "RFID Card";
$lang['globalRFIDCards'] = "RFID Cards";
$lang['globalCardIdPlaceholder'] = "e.g. '1234567890'";
$lang['globalCardIdHelp'] = "The ID is usually printed on the card or fob. A list of used IDs can be found on the home page.";
$lang['globalRegisterCard'] = "Register new card ID";
$lang['globalRegisterCardShort'] = "Card ID";
$lang['globalLastUsedCard'] = "Last used Chip ID";
$lang['globalClose'] = "Close";
$lang['globalPlay'] = "Play";
$lang['globalVolume'] = "Volume";
$lang['globalVolumeSettings'] = "Volume Settings";
$lang['globalWifi'] = "WiFi";
$lang['globalWifiSettings'] = "WiFi Settings";
$lang['globalWifiNetwork'] = "WiFi Settings";
$lang['globalSSID'] = "SSID";
$lang['globalSet'] = "Set";
$lang['globalSettings'] = "Settings";
$lang['globalFolder'] = "Folder";
$lang['globalFolderName'] = "Folder name";
$lang['globalFilename'] = "File name";
$lang['globalStream'] = "Stream";
$lang['globalSubmit'] = "Submit";
$lang['globalUpload'] = "Upload";
$lang['globalUpdate'] = "Update";
$lang['globalCancel'] = "Cancel";
$lang['globalDelete'] = "Delete";
$lang['globalCreate'] = "Create";
$lang['globalMove'] = "Move";
$lang['globalJumpTo'] = "Jump to";
$lang['globalAutoShutdown'] = "Auto Shutdown";
$lang['globalIdleShutdown'] = "Idle Shutdown";
$lang['globalAutoStopPlayout'] = "Stop Playout Timer";
$lang['globalStopTimer'] = "Stop Playout Timer";
$lang['globalSleepTimer'] = "Shutdown Timer";
$lang['globalExternalInterfaces'] = "External Devices & Interfaces";
$lang['globalIdleTime'] = "Idle Time";
$lang['globalNotIdle'] = "Not Idle";
$lang['globalGpioButtons'] = "GPIO Buttons";
$lang['globalRotaryKnob'] = "Rotary Knob";
$lang['globalRfidReader'] = "RFID Reader";
$lang['globalEnabled'] = "Enabled";
$lang['globalDisabled'] = "Disabled";
$lang['globalSwitchOn'] = "Switch ON";
$lang['globalSwitchOff'] = "Switch OFF";
$lang['globalSystem'] = "System";
$lang['globalVersion'] = "Version";
$lang['globalDescription'] = "Description";
$lang['globalRelease'] = "Release";
$lang['globalStorage'] = "Storage";
$lang['globalShuffle'] = "Shuffle";
$lang['globalReplay'] = "Replay";
$lang['globalRepeat'] = "Repeat";
$lang['globalLoop'] = "Loop";
$lang['globalLang'] = "Language";
$lang['globalLanguageSettings'] = "Language Settings";
$lang['globalPriority'] = "Priority";
$lang['globalEmail'] = "Email address";

// Player title HTML
$lang['playerSeekBack'] = "seek back";
$lang['playerSeekAhead'] = "seek forward";
$lang['playerSkipPrev'] = "previous track";
$lang['playerSkipNext'] = "next track";
$lang['playerPlayPause'] = "play / pause";
$lang['playerReplay'] = "replay track";
$lang['playerLoop'] = "loop";
$lang['playerStop'] = "stop player";
$lang['playerVolDown'] = "volume down";
$lang['playerVolUp'] = "volume up";
$lang['playerMute'] = "toggle mute";
$lang['playerFilePlayed'] = "is playing";
$lang['playerFileAdded'] = "added to playlist";
$lang['playerFileDeleted'] = "removed";


// Edition (classic, +spotify)
$lang['globalEdition'] = "Edition";
$lang['classic'] = "Classic edition (barebones)";
$lang['plusSpotify'] = "Plus edition (feat. Spotify integration)";

$lang['navEditionClassic'] = "Classic";
$lang['navEditionPlusSpotify'] = "+Spotify";

$lang['navBrand'] = "Phoniebox";
$lang['navHome'] = "Player";
$lang['navSearch'] = "Search";
$lang['navSettings'] = "Settings";
$lang['navInfo'] = "Info";
$lang['navShutdown'] = "Shutdown";
$lang['navReboot'] = "Reboot";

$lang['indexAvailAudio'] = "Available audio";
$lang['indexContainsFiles'] = "Contains the following file(s):";
$lang['indexShowFiles'] = "Show files";
$lang['indexManageFilesChips'] = "Manage Files and Chips";

$lang['Spotify'] = "Spotify";

/*
* Register & Edit Cards
*/
$lang['cardRegisterTitle'] = "Add new card";
$lang['cardEditTitle'] = "Edit or add card";
$lang['cardRegisterAnchorLink'] = "Interactive RFID Registration";
$lang['cardRegisterMessageDefault'] = "The 'Latest Card ID' value in the form is updated on the fly as you swipe a RFID card.<br/>(Requires Javascript in the browser to be enabled.)";
$lang['cardEditMessageDefault'] = "The card IDs used in this system are listed on the <a href='index.php' class='mainMenu'><i class='mdi mdi-home'></i> home page</a>.";
$lang['cardRegisterMessageSwipeNew'] = "Swipe another card, if you want to register more cards.";
$lang['cardEditMessageInputNew'] = "Type another card ID pick one from the list on the <a href='index.php' class='mainMenu'><i class='mdi mdi-home'></i> home page</a>.";
$lang['cardRegisterErrorTooMuch'] = "<p>This is too much! Please select only one audiofolder. Make up your mind.</p>";
$lang['cardRegisterErrorStreamAndAudio'] = "<p>This is too much! Either specify a stream or select an audio folder or system command. Make up your mind.</p>";
$lang['cardRegisterErrorStreamOrAudio'] = "<p>Seems you haven't selected anything! Add an URL and stream type, select a folder or a system command. Or 'Cancel' to go back to the home page.</p>";
$lang['cardRegisterErrorExistingAndNew'] = "<p>This is too much! Either choose an existing folder or create a new one.</p>";
$lang['cardRegisterErrorExistingFolder'] = "<p>A folder named with the same name already exists! Chose a different one.</p>";
$lang['cardRegisterErrorSuggestFolder'] = "A folder name for the stream needs to be created. Below in the form I made a suggestion.";
$lang['cardRegisterStream2Card'] = "Stream is linked to Card ID.";
$lang['cardRegisterFolder2Card'] = "Audio folder is now linked to Card.";
$lang['cardRegisterDownloadingYT'] = "<p>YouTube audio is downloading. This may take a couple of minutes. You may check the logfile \"youtube-dl.log\" in the shared folder.</p>";
$lang['cardRegisterSwipeUpdates'] = "This will automatically update as you swipe a RFID card.";
$lang['cardRegisterManualLinks'] = "<p>You can also connect cards to folders manually. The manual explains how to <a href='https://github.com/chbuehlmann/RPi-Jukebox-RFID/wiki/MANUAL#connecting-to-the-phoniebox-to-add-files' target='–blank'>connect to the phoniebox</a> and <a href='https://github.com/chbuehlmann/RPi-Jukebox-RFID/wiki/MANUAL#registering-cards-manually-through-samba-without-the-web-app' target='_blank'>register cards</a>.</p>";
$lang['cardRegisterTriggerSuccess'] = "The card is now linked to trigger the command:";

/*
* Card edit form
*/
$lang['cardFormFolderLegend'] = "Link RFID to:";
$lang['cardFormFolderLabel'] = "Link card to existing audio folder";
$lang['cardFormFolderSelectDefault'] = "None (pulldown to select a folder)";
$lang['cardFormFolderHelp'] = "Containing local files or add YouTube content (specify below).";
$lang['cardFormNewFolderLabel'] = "... or link a new folder";
$lang['cardFormNewFolderHelp'] = "Always use a new folder for streams (see below) and optionally for YouTube.";
$lang['cardFormNewFolderPlaceholder'] = "e.g. 'Artist Name/Album'";
$lang['cardFormTriggerLegend'] = "Trigger system command";
$lang['cardFormTriggerLabel'] = "... or link to a system command";
$lang['cardFormTriggerHelp'] = "Select system commands (like 'pause', 'volume up', 'shutdown') from the list of available commands. If a RFID card is already linked to a function, the ID is shown in the pulldown menu.";
$lang['cardFormTriggerSelectDefault'] = "Select command to link";

$lang['cardFormStreamLegend'] = "Link Stream";
$lang['cardFormStreamLabel'] = "Stream URL (always requires new folder above)";
$lang['cardFormStreamPlaceholderClassic'] = "http(...).mp3 / .m3u / .ogg / .rss / .xml / ...";
$lang['cardFormStreamPlaceholderPlusSpotify'] = "spotify:album/artist/playlist/track:### / Stream/Podcast like http....mp3 .xml .rss .ogg";
$lang['cardFormStreamHelp'] = "Add the URL for spotify, podcast, web radio, stream or other online media";
$lang['cardFormStreamTypeSelectDefault'] = "Select type";
$lang['cardFormStreamTypeHelp'] = "Select the type you are adding";

$lang['cardFormYTLegend'] = "Download YouTube";
$lang['cardFormYTLabel'] = "YouTube URL (single clip or playlist)";
$lang['cardFormYTPlaceholder'] = "e.g. https://www.youtube.com/watch?v=7GI0VdPehQI";
$lang['cardFormYTSelectDefault'] = "Pull down to select a folder or create a new one below";
$lang['cardFormYTHelp'] = "Full YouTube-URL of clip or playlist. Will be downloaded in the folder specified above or the new one if specified.";
$lang['cardFormRemoveCard'] = "Remove Card ID";

// Export Card IDs as .csv file
$lang['cardExportAnchorLink'] = "Export all RFID links (audio playout and commands)";
$lang['cardExportButtonLink'] = "Create .csv file of available RFID links";

// Import Card IDs as .csv file
$lang['cardImportAnchorLink'] = "Import RFID links from .csv file";
$lang['cardImportFileLabel'] = "Select .csv file to create RFID links";
$lang['cardImportFileSuccessUpload'] = "Successful upload of file: ";
$lang['cardImportFileErrorUpload'] = "<p>There was an error uploading the file, please try again!</p>";
$lang['cardImportFileErrorFiletype'] = "<p>Wrong file type! The file must be a <em>.csv</em> file.</p>";
$lang['cardImportFormOverwriteLabel'] = "Select import action";
$lang['cardImportFormOverwriteHelp'] = "Specify what to do with the uploaded RFID links.";
$lang['cardImportFormOverwriteAll'] = "Overwrite both: audio AND commands";
$lang['cardImportFormOverwriteAudio'] = "Overwrite ONLY audio triggers";
$lang['cardImportFormOverwriteCommands'] = "Overwrite ONLY system commands";
$lang['cardImportFileOverwriteMessageCommands'] = "<p><i class='mdi mdi-check'></i> <strong>System commands</strong> were overwritten with uploaded RFID IDs.</p>";
$lang['cardImportFileOverwriteMessageAudio'] = "<p><i class='mdi mdi-check'></i> Links to <strong>audio</strong> playlists etc. were overwritten with uploaded RFID IDs.</p>";
$lang['cardImportFormDeleteLabel'] = "Delete or keep other RFID links?";
$lang['cardImportFormDeleteNone'] = "Keep all existing: audio AND commands";
$lang['cardImportFormDeleteAll'] = "Delete both: audio AND commands";
$lang['cardImportFormDeleteAudio'] = "Delete ONLY audio triggers";
$lang['cardImportFormDeleteCommands'] = "Delete ONLY system commands";
$lang['cardImportFormDeleteHelp'] = "Which of the existing RFID links should be kept, which deleted?.";
$lang['cardImportFileDeleteMessageCommands'] = "<p><i class='mdi mdi-delete'></i> <strong>System commands</strong> deleted.</p>";
$lang['cardImportFileDeleteMessageAudio'] = "<p><i class='mdi mdi-delete'></i> <strong>Audio links</strong> deleted.</p>";

/*
* Track edit form
*/
$lang['trackEditTitle'] = "Track management";
$lang['trackEditInformation'] = "Track information";
$lang['trackEditMove'] = "Move track";
$lang['trackEditMoveSelectLabel'] = "Select new folder";
$lang['trackEditMoveSelectDefault'] = "Do not move file";
$lang['trackEditDelete'] = "Delete track";
$lang['trackEditDeleteLabel'] = "Sure you want to delete???";
$lang['trackEditDeleteHelp'] = "There is no 'undo' for deleted files. They are gone! Are you sure?";
$lang['trackEditDeleteNo'] = "Do NOT delete this track";
$lang['trackEditDeleteYes'] = "Yes, DELETE this track";

/*
* Settings
*/
$lang['settingsVolChangePercent'] = "Vol. Change %";
$lang['settingsMaxVol'] = "Maximum Volume";
$lang['settingsStartupVol'] = "Startup Volume";
$lang['settingsWifiRestart'] = "The changes applied to your WiFi connection require a restart to take effect.";
$lang['settingsWifiSsidPlaceholder'] = "e.g.: PhonieHomie";
$lang['settingsWifiSsidHelp'] = "The name under which your WiFi shows up as 'available network'";
$lang['settingsWifiPassHelp'] = "The password of your WiFi (8 characters at least)";
$lang['settingsWifiPrioHelp'] = "Your WiFi's priority (0-100). If more than  one WiFi is found the box will connect to the one with the higher priority";
$lang['settingsSecondSwipe'] = "Second Swipe";
$lang['settingsSecondSwipeInfo'] = "When you swipe the same RFID a second time, what happens? Start the playlist again? Toggle pause/play?";
$lang['settingsSecondSwipeRestart'] = "Re-start playlist";
$lang['settingsSecondSwipeSkipnext'] = "Skip to next track";
$lang['settingsSecondSwipePause'] = "Toggle pause / play";
$lang['settingsSecondSwipePlay'] = "Resume playback";
$lang['settingsSecondSwipeNoAudioPlay'] = "Ignore audio playout triggers, only system commands";
$lang['settingsSecondSwipePauseInfo'] = "Ignore rescanning of the same card for:";
$lang['second'] = "second";
$lang['seconds'] = "seconds";
$lang['settingsSecondSwipePauseControlsInfo'] = "Certain function cards (e.g. volume up / down, next / previous track, forward / rewind) should not have a delay (as set in the setting previously):";
$lang['settingsSecondSwipePauseControlsOn'] = "Function cards without delay";
$lang['settingsSecondSwipePauseControlsOff'] = "Function cards with delay (seconds as before)";
$lang['settingsWebInterface'] = "Web Interface";
$lang['settingsCoverInfo'] = "Do you want to show covers beside the albums and playlists on the main page?";
$lang['settingsShowCoverON'] = "Show cover";
$lang['settingsShowCoverOFF'] = "Don't show cover";
$lang['settingsMessageLangfileNewItems'] = "There are new language items in the original <em>lang-en-UK.php</em> file. Your language file has been updated and now contains these (in English). You might want to update your language file and commit your changes to the Phoniebox code :)";
$lang['settingsWlanSendNav'] = "Mail Wlan IP";
$lang['settingsWlanSendInfo'] = "Send Wlan IP over email on boot? (useful if you hook your Phoniebox into a new Wlan networt with dynamic IP)";
$lang['settingsWlanSendQuest'] = "Send Wlan IP?";
$lang['settingsWlanSendEmail'] = "email addr.";
$lang['settingsWlanSendON'] = "Yes, send email.";
$lang['settingsWlanSendOFF'] = "No, do not send email.";

$lang['settingsVolumeManager'] = "Select volume manager";

$lang['settingsWlanReadNav'] = "Read Wlan IP";
$lang['settingsWlanReadInfo'] = "Read IP address of wlan (wifi) each time after booting? (useful if you hook your Phoniebox into a new wlan networt with dynamic IP)";
$lang['settingsWlanReadQuest'] = "Read wlan IP?";
$lang['settingsWlanReadON'] = "Yes, read wlan IP.";
$lang['settingsWlanReadOFF'] = "No, do not read wlan IP.";

/*
* System info
*/
$lang['infoOsDistrib'] = "OS Distribution";
$lang['infoOsCodename'] = "Codename";
$lang['infoOsTemperature'] = "Temperature";
$lang['infoOsThrottle'] = "Throttling";
$lang['infoStorageUsed'] = "Storage usage";
$lang['infoMopidyStatus'] = "Mopidy Server Status";
$lang['infoMPDStatus'] = "MPD Server Status";
$lang['infoDebugLogTail'] = "<b>DEBUG log file</b>: Last 40 lines";
$lang['infoDebugLogClear'] = "Clear all content from debug.log";
$lang['infoDebugLogSettings'] = "Debug Log Settings";

/*
* Folder Management and File Upload
*/
$lang['manageFilesFoldersTitle'] = "Folders &amp; Files";
$lang['manageFilesFoldersUploadFilesLabel'] = "Select files from your drive";
$lang['manageFilesFoldersUploadLegend'] = "Upload files";
$lang['manageFilesFoldersUploadLabel'] = "Select and/or create new folder";
$lang['manageFilesFoldersUploadFolderHelp'] = "If you select AND name a new folder, the new folder will be created inside the selected folder.";
$lang['manageFilesFoldersNewFolderTitle'] = "Create new folder";
$lang['manageFilesFoldersNewFolderPositionLegend'] = "Folder position";
$lang['manageFilesFoldersNewFolderPositionDefault'] = "The new folder will be on the root level or inside (choose below)";
$lang['manageFilesFoldersErrorNewFolderName'] = "<p>No valid folder name given.</p>";
$lang['manageFilesFoldersErrorNewFolder'] = "<p>No folder selected nor a valid new folder specified.</p>";
$lang['manageFilesFoldersErrorNoNewFolder'] = "<p>No folder selected nor a valid new folder specified.</p>";
$lang['manageFilesFoldersErrorNewFolderExists'] = "<p>A folder by that name already exists. Be original, type a new name.</p>";
$lang['manageFilesFoldersErrorNewFolderNotParent'] = "<p>The parent folder does not exist.</p>";
$lang['manageFilesFoldersSuccessNewFolder'] = "New folder created: ";
$lang['manageFilesFoldersSelectDefault'] = "Pull down to select a folder and/or create a new child folder below";

$lang['manageFilesFoldersRenewDB'] = "Renew database";
$lang['manageFilesFoldersLocalScan'] = "Scan Music Library";
$lang['manageFilesFoldersRenewDBinfo'] = "Please scan your music library after you have uploaded new files or moved folders. The scan is not necessary to hear music, but it is necessary to see track information in the Web UI. Only new or moved files will be scanned. While the scan is running, mopidy will be stopped. After scan is complete, mopidy starts automatically. You can see the server status in the Info section.";

/*
* File search
*/
$lang['searchTitle'] = "Search for audiofiles";
$lang['searchExample'] = "z.B. Moonlight";
$lang['searchSend'] = "Search";
$lang['searchResult'] = "Search-Results:";

/*
* Filter
*/
$lang['filterall'] = "Show all";
$lang['filterfile'] = "Files";
$lang['filterlivestream'] = "Livestream";
$lang['filterpodcast'] = "Podcast";
$lang['filterspotify'] = "Spotify";
$lang['filteryoutube'] = "YouTube";
?>
