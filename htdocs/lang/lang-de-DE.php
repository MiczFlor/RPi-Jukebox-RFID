<?php
$lang = array();

$lang['globalEdit'] = "Bearbeiten";
$lang['globalResume'] = "Fortsetzen";
$lang['globalPassword'] = "Passwort";
$lang['globalOff'] = "OFF";
$lang['globalOn'] = "ON";
$lang['globalSingle'] = "Einzel";
$lang['globalTrack'] = "Track";
$lang['globalList'] = "Liste";
$lang['globalPlaylist'] = "Wiedergabeliste";
$lang['globalCardId'] = "Karten-ID";
$lang['globalRFIDCard'] = "RFID-Karte";
$lang['globalRFIDCards'] = "RFID-Karten";
$lang['globalCardIdPlaceholder'] = "z.B.'1234567890'";
$lang['globalCardIdHelp'] = "Die Karten-ID ist in der Regel auf der Karte oder dem Anhänger aufgedruckt. Die verwendeten IDs findest du auf der Startseite.";
$lang['globalRegisterCard'] = "Neue Karten-ID registrieren";
$lang['globalRegisterCardShort'] = "Karten-ID";
$lang['globalLastUsedCard'] = "Zuletzt verwendete Karten-ID";
$lang['globalClose'] = "Schließen";
$lang['globalPlay'] = "Play";
$lang['globalVolume'] = "Lautstärke";
$lang['globalVolumeSettings'] = "Lautstärke-Einstellungen";
$lang['globalWifi'] = "WiFi";
$lang['globalWifiSettings'] = "WiFi-Einstellungen";
$lang['globalWifiNetwork'] = "WiFi-Einstellungen";
$lang['globalSSID'] = "SSID";
$lang['globalSet'] = "Set";
$lang['globalSettings'] = "Einstellungen";
$lang['globalFolder'] = "Ordner";
$lang['globalFolderName'] = "Ordnername";
$lang['globalFilename'] = "Dateiname";
$lang['globalStream'] = "Stream";
$lang['globalSubmit'] = "Absenden";
$lang['globalUpload'] = "Hochladen";
$lang['globalUpdate'] = "Aktualisierung";
$lang['globalCancel'] = "Abbrechen";
$lang['globalDelete'] = "Löschen";
$lang['globalCreate'] = "Erstellen";
$lang['globalMove'] = "Verschieben";
$lang['globalJumpTo'] = "Springe zu";
$lang['globalAutoShutdown'] = "Auto Shutdown";
$lang['globalIdleShutdown'] = "Leerlaufabschaltung";
$lang['globalAutoStopPlayout'] = "Stop Playout Timer";
$lang['globalStopTimer'] = "Stop Playout Timer";
$lang['globalSleepTimer'] = "Einschlaf-Timer";
$lang['globalExternalInterfaces'] = "Externe Geräte & Schnittstellen";
$lang['globalIdleTime'] = "Leerlaufzeit";
$lang['globalNotIdle'] = "Nicht im Leerlauf";
$lang['globalGpioButtons'] = "GPIO Buttons";
$lang['globalRfidReader'] = "RFID Reader";
$lang['globalEnabled'] = "Aktiviert";
$lang['globalDisabled'] = "Deaktiviert";
$lang['globalSwitchOn'] = "Switch ON";
$lang['globalSwitchOff'] = "Switch OFF";
$lang['globalSystem'] = "System";
$lang['globalVersion'] = "Version";
$lang['globalDescription'] = "Beschreibung";
$lang['globalRelease'] = "Release";
$lang['globalStorage'] = "Speicher";
$lang['globalShuffle'] = "Mischen";
$lang['globalReplay'] = "Wiederholung";
$lang['globalRepeat'] = "Wiederholen";
$lang['globalLoop'] = "Schleife";
$lang['globalLang'] = "Sprache";
$lang['globalLanguageSettings'] = "Spracheinstellungen";

// Edition (classic, +spotify)
$lang['globalEdition'] = "Edition";
$lang['classic'] = "Classic edition (barebones)";
$lang['plusSpotify'] = "Plus Edition (feat. Spotify Integration)";

$lang['navEditionClassic'] = "Classic";
$lang['navEditionPlusSpotify'] = "+Spotify";

$lang['navBrand'] = "Phoniebox";
$lang['navHome'] = "Home";
$lang['navSettings'] = "Einstellungen";
$lang['navInfo'] = "Info";
$lang['navShutdown'] = "Herunterfahren";
$lang['navReboot'] = "Neustart";

$lang['indexAvailAudio'] = "Verfügbare Medien";
$lang['indexContainsFiles'] = "Enthält die folgenden Dateien:";
$lang['indexShowFiles'] = "Dateien anzeigen";
$lang['indexManageFilesChips'] = "Dateien und Chips verwalten";

$lang['Spotify'] = "Spotify";

/*
* Register & Edit Cards
*/
$lang['cardRegisterTitle'] = "Neue Karte hinzufügen";
$lang['cardEditTitle'] = "Karte bearbeiten oder hinzufügen";
$lang['cardRegisterMessageDefault'] = "Der Wert 'Zuletzt verwendete Karten-ID' im Formular wird beim Durchziehen einer RFID-Karte sofort aktualisiert.<br/>(Erfordert die Aktivierung von Javascript im Browser.)";
$lang['cardEditMessageDefault'] = "Die in diesem System verwendeten Karten-IDs sind auf der <a href='index.php' class='mainMenu'><i class='mdi mdi-home'>Startseite</i></a> aufgeführt.";
$lang['cardRegisterMessageSwipeNew'] = "Eine weitere Karte auslesen, wenn du sie registrieren möchtest.";
$lang['cardEditMessageInputNew'] = "Gib eine andere Karten-ID ein, wähle eine aus der Liste auf der <a href='index.php' class='mainMenu'><i class='mdi mdi-home'>Startseite</i></a> aus.";
$lang['cardRegisterErrorTooMuch'] = "<p>Das ist zu viel! Bitte wähle nur einen Audioordner aus. Entscheide dich.</p>";
$lang['cardRegisterErrorStreamAndAudio'] = "<p>Das ist zu viel! Entweder ein Stream oder ein Audio-Ordner. Entscheide dich.</p>";
$lang['cardRegisterErrorStreamOrAudio'] = "<p>Das ist nicht genug! Füge eine URL mit Stream-Typ hinzu oder wähle einen Audio-Ordner. 'Abbrechen', um zur Startseite zurückzukehren.</p>";
$lang['cardRegisterErrorExistingAndNew'] = "<p>Das ist zu viel! Wähle entweder einen bestehenden Ordner aus oder erstelle einen neuen.</p>";
$lang['cardRegisterErrorExistingFolder'] = "<p>Ein Ordner mit dem gleichen Namen existiert bereits! Wähle einen anderen. </p>";
$lang['cardRegisterErrorSuggestFolder'] = "Ein Ordnername für den Stream muss erstellt werden. Unten im Formular steht ein Vorschlag.";
$lang['cardRegisterStream2Card'] = "Stream ist mit der Karten-ID verknüpft.";
$lang['cardRegisterFolder2Card'] = "Audio-Ordner ist nun mit der Karten-ID verknüpft.";
$lang['cardRegisterDownloadingYT'] = "<p>YouTube Audio wird heruntergeladen. Dies kann einige Minuten dauern. Du kannst die Logdatei \"youtube-dl.log\" im Ordner \"shared\" ansehen.</p>";
$lang['cardRegisterSwipeUpdates'] = "Dies wird automatisch aktualisiert, wenn du eine RFID-Karte ausliest.";
$lang['cardRegisterManualLinks'] = "<p>Du kannst Karten auch manuell mit Ordnern verbinden. Das Handbuch erklärt, wie man sich <a href='https://github.com/MiczFlor/RPi-Jukebox-RFID/wiki/MANUAL#connecting-to-the-phoniebox-to-add-files' target='-blank'>mit der Phoniebox verbindet</a> und <a href='https://github.com/MiczFlor/RPi-Jukebox-RFID/wiki/MANUAL#registering-cards-manually-through-samba-without-the-web-app' target='_blank'>Karten registriert</a>.</p>";

/*
* Card edit form
*/
$lang['cardFormFolderLegend'] = "Audio-Ordner";
$lang['cardFormFolderLabel'] = "a) Karte mit Audio-Ordner verbinden";
$lang['cardFormFolderSelectDefault'] = "Keiner (--Wählen-- zur Auswahl eines Ordners)";
$lang['cardFormStreamLabel'] = "b) ..... oder Verbindung mit Stream-URL";
$lang['cardFormStreamPlaceholderClassic'] = "Livestream: http(....).mp3 / .m3u / .ogg / ....";
$lang['cardFormStreamPlaceholderPlusSpotify'] = "spotify:(user:username:)album/track/playlist:#### / Livestream: http(....).mp3 / .m3u / .ogg / ....";
$lang['cardFormStreamHelp'] = "Füge die URL für spotify, Podcast, Webradio, Stream oder andere Online-Medien hinzu";
$lang['cardFormStreamTypeSelectDefault'] = "Wähle den Typ";
$lang['cardFormStreamTypeHelp'] = "Wähle den Typ, den du hinzufügen möchtest";
$lang['cardFormStreamFolderPlaceholder'] = "z.B.'Album/Playlist/Stationsname'";
$lang['cardFormStreamFolderHelp'] = "Name für den Audio-Ordner, der die Stream-URL enthält";
$lang['cardFormYTLegend'] = "YouTube";
$lang['cardFormYTLabel'] = "c) .... oder YouTube-Audio herunterladen";
$lang['cardFormYTPlaceholder'] = "z.B. https://www.youtube.com/watch?v=7GI0VdPehQI";
$lang['cardFormYTSelectDefault'] = "--Wählen--, um einen Ordner auszuwählen oder einen neuen darunter zu erstellen";
$lang['cardFormYTFolderPlaceholder'] = "z.B. 'Neuer Ordner'";
$lang['cardFormYTFolderHelp'] = "Name für den Audio-Ordner, der das YouTube-Audio enthält";
$lang['cardFormYTHelp'] = "Füge die volle YouTube-URL wie im Beispiel hinzu";
$lang['cardFormRemoveCard'] = "Karten-ID entfernen";

/*
* Track edit form
*/
$lang['trackEditTitle'] = "Track-Management";
$lang['trackEditInformation'] = "Track-Informationen";
$lang['trackEditMove'] = "Track verschieben";
$lang['trackEditMoveSelectLabel'] = "Neuen Ordner auswählen";
$lang['trackEditMoveSelectDefault'] = "Datei nicht verschieben";
$lang['trackEditDelete'] = "Track löschen";
$lang['trackEditDeleteLabel'] = "Möchtest du wirklich löschen?";
$lang['trackEditDeleteHelp'] = "Es gibt kein Rückgängigmachen für gelöschte Dateien. Sie sind weg! Bist du sicher?";
$lang['trackEditDeleteNo'] = "Diesen Track NICHT löschen";
$lang['trackEditDeleteYes'] = "Ja, diesen Track LÖSCHEN";


/*
* Settings
*/
$lang['settingsVolChangePercent'] = "Lautst. Änderung";
$lang['settingsMaxVol'] = "Max. Lautstärke";
$lang['settingsWifiRestart'] = "Die Änderungen an der WiFi-Verbindung erfordern einen Neustart, um wirksam zu werden";
$lang['settingsWifiSsidPlaceholder'] = "z.B. PhonieHomie";
$lang['settingsWifiSsidHelp'] = "Der Name, unter dem dein WiFi als 'verfügbares Netzwerk' angezeigt wird";
$lang['settingsSecondSwipe'] = "Erneute Aktivierung";
$lang['settingsSecondSwipeInfo'] = "Aktion, wenn dieselbe Karte ein weiteres Mal aktiviert wird:";
$lang['settingsSecondSwipeRestart'] = "Wiedergabeliste neu starten";
$lang['settingsSecondSwipeSkipnext'] = "Zum nächsten Track springen";
$lang['settingsSecondSwipePause'] = "Pause / Wiedergabe umschalten";
$lang['settingsSecondSwipeNoAudioPlay'] = "Nur Systembefehle mehrfach ausführen";
$lang['settingsWebInterface'] = "Web-Oberfläche";
$lang['settingsCoverInfo'] = "Willst du Cover neben den Alben und Playlisten auf der Hauptseite anzeigen?";
$lang['settingsShowCoverON'] = "Cover anzeigen";
$lang['settingsShowCoverOFF'] = "Kein Cover anzeigen";
$lang['settingsMessageLangfileNewItems'] = "Es gibt neue Sprachelemente in der originalen Sprachdatei <em>lang-en-UK.php</em>. Möglicherweise möchtest du deine Sprachdatei aktualisieren und Ihre Änderungen in den Phoniebox-Code übernehmen? :)";

/*
* System info
*/
$lang['infoOsDistrib'] = "Betriebssystem";
$lang['infoOsCodename'] = "Codename";
$lang['infoStorageUsed'] = "Speicherverbrauch";
$lang['infoMopidyStatus'] = "Mopidy Server Status";
$lang['infoMPDStatus'] = "MPD Server Status";

/*
* Folder Management and File Upload
*/
$lang['manageFilesFoldersTitle'] = "Ordner &amp; Dateien";
$lang['manageFilesFoldersUploadFilesLabel'] = "Dateien von deinem Laufwerk auswählen";
$lang['manageFilesFoldersUploadLegend'] = "Dateien hochladen";
$lang['manageFilesFoldersUploadLabel'] = "Neuen Ordner auswählen und/oder erstellen";
$lang['manageFilesFoldersUploadFolderHelp'] = "Wenn du einen Ordner auswählst UND einen neuen benennst, wird der neue Ordner im ausgewählten Ordner erstellt";
$lang['manageFilesFoldersNewFolderTitle'] = "Neuen Ordner erstellen";
$lang['manageFilesFoldersNewFolderPositionLegend'] = "Ordnerposition";
$lang['manageFilesFoldersNewFolderPositionDefault'] = "Der neue Ordner befindet sich auf der Root-Ebene oder unterhalb des unten ausgewählten";
$lang['manageFilesFoldersErrorNewFolderName'] = "<p>Kein gültiger Ordnername angegeben.</p>";
$lang['manageFilesFoldersErrorNewFolder'] = "<p>Kein Ordner ausgewählt und kein gültiger neuer Ordner angegeben.</p>";
$lang['manageFilesFoldersErrorNoNewFolder'] = "<p>Kein Ordner ausgewählt und kein gültiger neuer Ordner angegeben.</p>";
$lang['manageFilesFoldersErrorNewFolderExists'] = "<p>Ein Ordner mit diesem Namen existiert bereits. Gib einen neuen eindeutigen Namen ein.</p>";
$lang['manageFilesFoldersErrorNewFolderNotParent'] = "<p>Der übergeordnete Ordner existiert nicht.</p>";
$lang['manageFilesFoldersSuccessNewFolder'] = "Neuer Ordner erstellt: ";
$lang['manageFilesFoldersSelectDefault'] = "--Wählen--, um einen Ordner auszuwählen und/oder einen neuen Unterordner zu erstellen";

$lang['manageFilesFoldersRenewDB'] = "Datenbank erneuern";
$lang['manageFilesFoldersLocalScan'] = "Musikbibliothek scannen";
$lang['manageFilesFoldersRenewDBinfo'] = "Bitte scanne deine Musikbibliothek, nachdem du neue Dateien hochgeladen oder Ordner verschoben hast. Der Scan ist nicht notwendig, um Musik zu hören, aber es ist notwendig, um Track-Informationen in der Web-Oberfläche zu sehen. Es werden nur neue oder verschobene Dateien gescannt. Während der Scan läuft, wird Mopidy gestoppt. Nach Abschluss des Scans startet Mopidy automatisch neu. Den Serverstatus siehst du im Abschnitt Info.";


?>
