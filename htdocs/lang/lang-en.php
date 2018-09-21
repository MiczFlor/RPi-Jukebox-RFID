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
$lang['globalCardId'] = "Card ID";
$lang['globalRFIDCard'] = "RFID Card";
$lang['globalRFIDCards'] = "RFID Cards";
$lang['globalCardIdPlaceholder'] = "e.g. '1234567890'";
$lang['globalCardIdHelp'] = "The ID is usually printed on the card or fob. A list of used IDs can be found on the home page.";
$lang['globalRegisterCard'] = "Register new card ID";
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
$lang['globalFilename'] = "File name";
$lang['globalStream'] = "Stream";
$lang['globalSubmit'] = "Submit";
$lang['globalUpload'] = "Upload";
$lang['globalUpdate'] = "Update";
$lang['globalCancel'] = "Cancel";
$lang['globalDelete'] = "Delete";
$lang['globalMove'] = "Move";
$lang['globalJumpTo'] = "Jump to";
$lang['globalAutoShutdown'] = "Auto Shutdown";
$lang['globalIdleShutdown'] = "Idle Shutdown";
$lang['globalSleepTimer'] = "Sleep Timer";
$lang['globalExternalInterfaces'] = "External Devices & Interfaces";
$lang['globalIdleTime'] = "Idle Time";
$lang['globalNotIdle'] = "Not Idle";
$lang['globalGpioButtons'] = "GPIO Buttons";
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

$lang['navBrand'] = "Phoniebox";
$lang['navHome'] = "Home";
$lang['navSettings'] = "Settings";
$lang['navInfo'] = "Info";
$lang['navShutdown'] = "Shutdown";
$lang['navReboot'] = "Reboot";

$lang['indexAvailAudio'] = "Available audio";
$lang['indexContainsFiles'] = "Contains the following file(s):";
$lang['indexShowFiles'] = "Show files";
$lang['indexManageFilesChips'] = "Manage Files and Chips";

/*
* Register & Edit Cards
*/
$lang['cardRegisterTitle'] = "Add new card";
$lang['cardEditTitle'] = "Edit or add card";
$lang['cardRegisterMessageDefault'] = "The 'Latest Card ID' value in the form is updated on the fly as you swipe a RFID card.<br/>(Requires Javascript in the browser to be enabled.)";
$lang['cardEditMessageDefault'] = "The card IDs used in this system are listed on the <a href='index.php' class='mainMenu'><i class='mdi mdi-home'></i> home page</a>.";
$lang['cardRegisterMessageSwipeNew'] = "Swipe another card, if you want to register more cards.";
$lang['cardEditMessageInputNew'] = "Type another card ID pick one from the list on the <a href='index.php' class='mainMenu'><i class='mdi mdi-home'></i> home page</a>.";
$lang['cardRegisterErrorTooMuch'] = "<p>This is too much! Please select only one audiofolder. Make up your mind.</p>";
$lang['cardRegisterErrorStreamAndAudio'] = "<p>This is too much! Either a stream or an audio folder. Make up your mind.</p>";
$lang['cardRegisterErrorStreamOrAudio'] = "<p>This is not enough! Add a stream or select an audio folder. Or 'Cancel' to go back to the home page.</p>";
$lang['cardRegisterErrorExistingAndNew'] = "<p>This is too much! Either choose an existing folder or create a new one.</p>";
$lang['cardRegisterErrorExistingFolder'] = "<p>A folder named with the same name already exists! Chose a different one.</p>";
$lang['cardRegisterErrorSuggestFolder'] = "A folder name for the stream needs to be created. Below in the form I made a suggestion.";
$lang['cardRegisterStream2Card'] = "Stream is linked to Card ID.";
$lang['cardRegisterFolder2Card'] = "Audio folder is now linked to Card.";
$lang['cardRegisterDownloadingYT'] = "<p>YouTube audio is downloading. This may take a couple of minutes. You may check the logfile \"youtube-dl.log\" in the shared folder.</p>";
$lang['cardRegisterSwipeUpdates'] = "This will automatically update as you swipe a RFID card.";
$lang['cardRegisterManualLinks'] = "<p>You can also connect cards to folders manually. The manual explains how to <a href='https://github.com/MiczFlor/RPi-Jukebox-RFID/blob/master/docs/MANUAL.md#connecting-to-the-phoniebox-to-add-files' target='–blank'>connect to the phoniebox</a> and <a href='https://github.com/MiczFlor/RPi-Jukebox-RFID/blob/master/docs/MANUAL.md#registering-cards-manually-through-samba-without-the-web-app' target='_blank'>register cards</a>.</p>";

/*
* Card edit form
*/
$lang['cardFormFolderLegend'] = "Audio Folder";
$lang['cardFormFolderLabel'] = "a) Link card to audio folder";
$lang['cardFormFolderSelectDefault'] = "None (pulldown to select a folder)";
$lang['cardFormStreamLabel'] = "b) ... or connect with Stream URL";
$lang['cardFormStreamPlaceholder'] = "http(...).mp3 / .m3u / .ogg / ...";
$lang['cardFormStreamHelp'] = "Add the URL for a podcast, web radio, stream or other online media";
$lang['cardFormStreamTypeSelectDefault'] = "Select type of stream";
$lang['cardFormStreamTypeHelp'] = "Select the type of URL / stream you are adding";
$lang['cardFormStreamFolderPlaceholder'] = "e.g. 'Station Name'";
$lang['cardFormStreamFolderHelp'] = "Name for the audio folder that will contain the stream URL.";
$lang['cardFormYTLegend'] = "YouTube";
$lang['cardFormYTLabel'] = "c) ... or download YouTube audio";
$lang['cardFormYTPlaceholder'] = "e.g. https://www.youtube.com/watch?v=7GI0VdPehQI";
$lang['cardFormYTSelectDefault'] = "Pull down to select a folder or create a new one below";
$lang['cardFormYTFolderPlaceholder'] = "e.g. 'New Folder'";
$lang['cardFormYTFolderHelp'] = "Name for the audio folder that will contain the YouTube audio.";
$lang['cardFormYTHelp'] = "Add the full YouTube-URL like in the example";
$lang['cardFormRemoveCard'] = "Remove Card ID";

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
$lang['settingsWifiRestart'] = "The changes applied to your WiFi connection require a restart to take effect.";
$lang['settingsWifiSsidPlaceholder'] = "e.g.: PhonieHomie";
$lang['settingsWifiSsidHelp'] = "The name under which your WiFi shows up as 'available network'";

/*
* System info
*/
$lang['infoOsDistrib'] = "OS Distribution";
$lang['infoOsCodename'] = "Codename";
$lang['infoStorageUsed'] = "Storage usage";

/*
* File Upload
*/
$lang['fileUploadTitle'] = "Upload files";
$lang['fileUploadFilesLabel'] = "Select files from your drive";
$lang['fileUploadLegend'] = "Select files and folder";
$lang['fileUploadLabel'] = "Select folder or create new";
$lang['fileUploadFolderHelp'] = "Name for the audio folder that will contain the uploaded files.";


?>

