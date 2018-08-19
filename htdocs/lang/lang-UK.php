<?php
$lang = array();

$lang['globalEdit'] = "Edit";
$lang['globalResume'] = "Resume";
$lang['globalOff'] = "OFF";
$lang['globalOn'] = "ON";
$lang['globalCardId'] = "Card ID";
$lang['globalRegisterCard'] = "Register new card ID";
$lang['globalLastUsedCard'] = "Last used Chip ID";
$lang['globalClose'] = "Close";
$lang['globalPlay'] = "Play";
$lang['globalVolume'] = "Volume";
$lang['globalSet'] = "Set";
$lang['globalFolder'] = "Set";
$lang['globalStream'] = "Stream";
$lang['globalSubmit'] = "Submit";
$lang['globalCancel'] = "Cancel";

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
* Register new cards
*/
$lang['cardRegisterTitle'] = "Add new card ID";
$lang['cardRegisterMessageDefault'] = "The 'Latest Card ID' value in the form is updated on the fly as you swipe a RFID card.<br/>(Requires Javascript in the browser to be enabled.)";
$lang['cardRegisterMessageSwipeNew'] = "Swipe another card, if you want to register more cards.";
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
foreach($lang as $key => $value) {
    $lang[$key] = "NEW".$value;
}
/**/
?>