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
$lang['globalRotaryKnob'] = "Drehknopf";
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
$lang['globalPriority'] = "Priorität";
$lang['globalEmail'] = "Email address";

// Player title HTML
$lang['playerSeekBack'] = "Rückwärts spulen";
$lang['playerSeekAhead'] = "Vorwärts spulen";
$lang['playerSkipPrev'] = "Vorheriger Titel";
$lang['playerSkipNext'] = "Nächster Titel";
$lang['playerPlayPause'] = "Play / Pause";
$lang['playerReplay'] = "Titel wiederholen";
$lang['playerLoop'] = "Wiederholung";
$lang['playerStop'] = "Player stoppen";
$lang['playerVolDown'] = "Lautstärke verringern";
$lang['playerVolUp'] = "Lautstärke erhöhen";
$lang['player'] = "Stumm ein/aus";
$lang['playerFilePlayed'] = "wird abgespielt";
$lang['playerFileAdded'] = "wurde der Playlist hinzugef&uuml;gt";
$lang['playerFileDeleted'] = "entfernt";

// Edition (classic, +spotify)
$lang['globalEdition'] = "Edition";
$lang['classic'] = "Classic edition (barebones)";
$lang['plusSpotify'] = "Plus Edition (feat. Spotify Integration)";

$lang['navEditionClassic'] = "Classic";
$lang['navEditionPlusSpotify'] = "+Spotify";

$lang['navBrand'] = "Phoniebox";
$lang['navHome'] = "Player";
$lang['navSearch'] = "Suchen";
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
* Karten registrieren & bearbeiten
*/
$lang['cardRegisterTitle'] = "Neue Karte hinzufügen";
$lang['cardEditTitle'] = "Karte bearbeiten oder hinzufügen";
$lang['cardRegisterAnchorLink'] = "RFID-Registrierung interaktiv";
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
$lang['cardRegisterManualLinks'] = "<p>Du kannst Karten auch manuell mit Ordnern verbinden. Das Handbuch erklärt, wie man sich <a href='https://github.com/chbuehlmann/RPi-Jukebox-RFID/wiki/MANUAL#connecting-to-the-phoniebox-to-add-files' target='-blank'>mit der Phoniebox verbindet</a> und <a href='https://github.com/chbuehlmann/RPi-Jukebox-RFID/wiki/MANUAL#registering-cards-manually-through-samba-without-the-web-app' target='_blank'>Karten registriert</a>.</p>";
$lang['cardRegisterTriggerSuccess'] = "Die Karte ist jetzt verknüpft um die Funktion auszuführen:";

/*
* "Karten bearbeiten"-Formular
*/
$lang['cardFormFolderLegend'] = "RFID-Karte verlinken mit:";
$lang['cardFormFolderLabel'] = "Einen Audio-Ordner auswählen";
$lang['cardFormFolderSelectDefault'] = "Keiner (--Wählen-- zur Auswahl eines Ordners)";
$lang['cardFormFolderHelp'] = "Enthält lokale Dateien / Stream. Bzw. ein YouTube Download für diesen Ordner (s.u.).";
$lang['cardFormNewFolderLabel'] = "... oder einen neuen Ordner erstellen";
$lang['cardFormNewFolderHelp'] = "Für einen Stream (s.u.) <strong>muss</strong> ein neuer Ordner erstellt werden. Für YouTube optional.";
$lang['cardFormNewFolderPlaceholder'] = "e.g. 'Artist Name/Album'";
$lang['cardFormTriggerLegend'] = "Phoniebox Funktion verknüpfen";
$lang['cardFormTriggerLabel'] = "... eine Phoniebox Funktion auswählen";
$lang['cardFormTriggerHelp'] = "Wähle eine Funktion aus der Liste aus (z.B. 'pause', 'volume up', 'shutdown'). Bestehende Verknüpfungen werden im Pulldown-Menü angezeigt.";
$lang['cardFormTriggerSelectDefault'] = "Wähle eine Phoniebox Funktion";

$lang['cardFormStreamLegend'] = "Stream verlinken / erstellen";
$lang['cardFormStreamLabel'] = "Stream URL (benötigt immer einen neuen Ordner - s.o.)";
$lang['cardFormStreamPlaceholderClassic'] = "http(...).mp3 / .m3u / .ogg / .rss / .xml / ...";
$lang['cardFormStreamPlaceholderPlusSpotify'] = "spotify:album/artist/playlist/track:#### / Livestream: http(....).mp3 / .m3u / .ogg / ....";
$lang['cardFormStreamHelp'] = "Füge die URL für spotify, Podcast, Webradio, Stream oder andere Online-Medien hinzu";
$lang['cardFormStreamTypeSelectDefault'] = "Wähle den Typ";
$lang['cardFormStreamTypeHelp'] = "Wähle die Art des Streams, den du hinzufügen möchtest";

$lang['cardFormYTLegend'] = "Von YouTube Herunterladen";
$lang['cardFormYTLabel'] = "YouTube URL (einzelner Track oder Playlist)";
$lang['cardFormYTPlaceholder'] = "z.B. https://www.youtube.com/watch?v=7GI0VdPehQI";
$lang['cardFormYTSelectDefault'] = "--Wählen--, um einen Ordner auszuwählen oder einen neuen darunter zu erstellen";
$lang['cardFormYTHelp'] = "Füge die volle YouTube-URL wie im Beispiel hinzu";
$lang['cardFormRemoveCard'] = "Karten-ID entfernen";

// Karten IDs als .csv-Datei exportieren
$lang['cardExportAnchorLink'] = "Alle RFID Verknüpfungen exportieren (Audio und Systembefehle)";
$lang['cardExportButtonLink'] = ".csv-Datei aller verfügbaren RFID-Verknüpfungen erstellen";

// Karten IDs aus .csv-Datei importieren
$lang['cardImportAnchorLink'] = "RFID Verknüpfungen aus .csv-Datei importieren";
$lang['cardImportFileLabel'] = ".csv-Datei auswählen um RFID-Verknüpfungen zu erstellen";
$lang['cardImportFileSuccessUpload'] = "Datei erfolgreich hochgeladen: ";
$lang['cardImportFileErrorUpload'] = "<p>Fehler beim Hochladen der Datei, bitte erneut versuchen!</p>";
$lang['cardImportFileErrorFiletype'] = "<p>Falscher Datei-Typ! Die Datei muss eine <em>.csv</em> Datei sein.</p>";
$lang['cardImportFormOverwriteLabel'] = "Importvorgang auswählen";
$lang['cardImportFormOverwriteHelp'] = "Was soll mit den hochgeladenen RFID-Verknüpfungen gemacht werden.";
$lang['cardImportFormOverwriteAll'] = "Beide überschreiben: Audio UND Systembefehle";
$lang['cardImportFormOverwriteAudio'] = "NUR Audio überschreiben";
$lang['cardImportFormOverwriteCommands'] = "NUR Systembefehle überschreiben";
$lang['cardImportFileOverwriteMessageCommands'] = "<p><i class='mdi mdi-check'></i> <strong>Systembefehle</strong> wurden mit hochgeladenen RFID-IDs überschrieben.</p>";
$lang['cardImportFileOverwriteMessageAudio'] = "<p><i class='mdi mdi-check'></i> Verknüpfungen zu <strong>Audio</strong> Playlisten usw. wurden mit hochgeladenen RFID-IDs überschrieben.</p>";
$lang['cardImportFormDeleteLabel'] = "Andere RFID-Verknüpfungen löschen oder behalten?";
$lang['cardImportFormDeleteNone'] = "Alle vorhandenen behalten: Audio UND Systembefehle";
$lang['cardImportFormDeleteAll'] = "Beide löschen: Audio UND Systembefehle";
$lang['cardImportFormDeleteAudio'] = "NUR Audio löschen";
$lang['cardImportFormDeleteCommands'] = "NUR Systembefehle löschen";
$lang['cardImportFormDeleteHelp'] = "Welche der bestehenden RFID-Verknüpfungen sollen behalten werden, welche gelöscht?";
$lang['cardImportFileDeleteMessageCommands'] = "<p><i class='mdi mdi-delete'></i> <strong>Systembefehle</strong> gelöscht.</p>";
$lang['cardImportFileDeleteMessageAudio'] = "<p><i class='mdi mdi-delete'></i> <strong>Audio Verknüpfungen</strong> gelöscht.</p>";

/*
* "Track bearbeiten"-Formular
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
* Einstellungen
*/
$lang['settingsVolChangePercent'] = "Lautst. Änderung";
$lang['settingsMaxVol'] = "Max. Lautstärke";
$lang['settingsStartupVol'] = "Start-Lautstärke";
$lang['settingsWifiRestart'] = "Die Änderungen an der WiFi-Verbindung erfordern einen Neustart, um wirksam zu werden";
$lang['settingsWifiSsidPlaceholder'] = "z.B. PhonieHomie";
$lang['settingsWifiSsidHelp'] = "Der Name, unter dem dein WiFi als 'verfügbares Netzwerk' angezeigt wird";
$lang['settingsWifiPassHelp'] = "Das Passwort für dein WiFi (mindestens 8 Zeichen)";
$lang['settingsWifiPrioHelp'] = "Die Priorität deines WiFi (0-100). Wenn mehr als ein WiFi gefunden wird, verbindet sich die Box mit dem, das die höhere Priorität hat";
$lang['settingsSecondSwipe'] = "Erneute Aktivierung";
$lang['settingsSecondSwipeInfo'] = "Aktion, wenn dieselbe Karte ein weiteres Mal aktiviert wird:";
$lang['settingsSecondSwipeRestart'] = "Wiedergabeliste neu starten";
$lang['settingsSecondSwipeSkipnext'] = "Zum nächsten Track springen";
$lang['settingsSecondSwipePause'] = "Pause / Wiedergabe umschalten";
$lang['settingsSecondSwipePlay'] = "Wiedergabe fortsetzen";
$lang['settingsSecondSwipeNoAudioPlay'] = "Nur Systembefehle mehrfach ausführen";
$lang['settingsSecondSwipePauseInfo'] = "Ignoriere das erneute Scannen derselben Karte für:";
$lang['second'] = "Sekunde";
$lang['seconds'] = "Sekunden";
$lang['settingsSecondSwipePauseControlsInfo'] = "Bestimmte Funktionskarten (z.B. Lautstärke hoch/runter, Nächster/Voriger Titel, Vor-/Zurückspulen) sollen keine Verzögerung (wie in der Einstellung zuvor eingestellt) haben:";
$lang['settingsSecondSwipePauseControlsOn'] = "Funktionskarten ohne Verzögerung";
$lang['settingsSecondSwipePauseControlsOff'] = "Funktionskarten mit Verzögerung (Sekunden wie zuvor)";
$lang['settingsWebInterface'] = "Web-Oberfläche";
$lang['settingsCoverInfo'] = "Willst du Cover neben den Alben und Playlisten auf der Hauptseite anzeigen?";
$lang['settingsShowCoverON'] = "Cover anzeigen";
$lang['settingsShowCoverOFF'] = "Kein Cover anzeigen";
$lang['settingsMessageLangfileNewItems'] = "Es gibt neue Sprachelemente in der originalen Sprachdatei <em>lang-en-UK.php</em>. Möglicherweise möchtest du deine Sprachdatei aktualisieren und Ihre Änderungen in den Phoniebox-Code übernehmen? :)";
$lang['settingsWlanSendNav'] = "Wlan IP mailen";
$lang['settingsWlanSendInfo'] = "Wlan IP beim Systemstart per E-Mail senden? (nützlich wenn du deine Phoniebox in ein neues Wlan-Netzwerk mit dynamischer IP verbindest)";
$lang['settingsWlanSendQuest'] = "Wlan IP senden?";
$lang['settingsWlanSendEmail'] = "E-Mail Adr.";
$lang['settingsWlanSendON'] = "Ja, E-Mail senden.";
$lang['settingsWlanSendOFF'] = "Nein, E-Mail nicht senden.";


$lang['settingsWlanReadNav'] = "Wlan IP vorlesen";
$lang['settingsWlanReadInfo'] = "Wlan IP bei jedem Systemstart vorlesen? (nützlich wenn du deine Phoniebox in ein neues Wlan-Netzwerk mit dynamischer IP verbindest)";
$lang['settingsWlanReadQuest'] = "Wlan IP vorlesen?";
$lang['settingsWlanReadON'] = "Ja, Wlan IP vorlesen.";
$lang['settingsWlanReadOFF'] = "Nein, Wlan IP nicht vorlesen.";

/*
* Systeminformationen
*/
$lang['infoOsDistrib'] = "Betriebssystem";
$lang['infoOsCodename'] = "Codename";
$lang['infoOsTemperature'] = "Temperatur";
$lang['infoOsThrottle'] = "Drosselung";
$lang['infoStorageUsed'] = "Speicherverbrauch";
$lang['infoMopidyStatus'] = "Mopidy Server Status";
$lang['infoMPDStatus'] = "MPD Server Status";
$lang['infoDebugLogTail'] = "<b>DEBUG Logdatei</b>: Letzte 40 Zeilen";
$lang['infoDebugLogClear'] = "Lösche Inhalt von debug.log";
$lang['infoDebugLogSettings'] = "Debug Log Einstellungen";

/*
* Ordnerverwaltung und Dateien hochladen
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

/*
* Dateisuche
*/
$lang['searchTitle'] = "Audiodateien suchen";
$lang['searchExample'] = "z.B. Moonlight";
$lang['searchSend'] = "Suchen";
$lang['searchResult'] = "Suchergebnisse:";

/*
* Filter
*/
$lang['filterall'] = "Zeige alle";
$lang['filterfile'] = "Dateien";
$lang['filterlivestream'] = "Livestream";
$lang['filterpodcast'] = "Podcast";
$lang['filterspotify'] = "Spotify";
$lang['filteryoutube'] = "YouTube";
?>
