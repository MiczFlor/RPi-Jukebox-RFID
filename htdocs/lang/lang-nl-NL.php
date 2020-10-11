<?php
$lang = array();

$lang['globalEdit'] = "Bewerk";
$lang['globalResume'] = "Vervolg";
$lang['globalPassword'] = "Wachtwoord";
$lang['globalOff'] = "UIT";
$lang['globalOn'] = "AAN";
$lang['globalSingle'] = "Enkele (single)";
$lang['globalTrack'] = "Track";
$lang['globalList'] = "Lijst";
$lang['globalPlaylist'] = "Afspeellijst";
$lang['globalCardId'] = "Kaart ID";
$lang['globalRFIDCard'] = "RFID kaart";
$lang['globalRFIDCards'] = "RFID kaarten";
$lang['globalCardIdPlaceholder'] = "bijv. '1234567890'";
$lang['globalCardIdHelp'] = "De ID wordt meestal afgedrukt op de kaart of fob. Een lijst met gebruikte ID's is te vinden op de startpagina.";
$lang['globalRegisterCard'] = "Registreer nieuwe kaart ID";
$lang['globalRegisterCardShort'] = "kaart ID";
$lang['globalLastUsedCard'] = "laatst gebruikte Chip ID";
$lang['globalClose'] = "Sluiten";
$lang['globalPlay'] = "Afspelen";
$lang['globalVolume'] = "Volume";
$lang['globalVolumeSettings'] = "Volume instellingen";
$lang['globalWifi'] = "WiFi";
$lang['globalWifiSettings'] = "WiFi instellingen";
$lang['globalWifiNetwork'] = "WiFi instellingen";
$lang['globalSSID'] = "SSID";
$lang['globalSet'] = "Instellen";
$lang['globalSettings'] = "Instellingen";
$lang['globalFolder'] = "Map";
$lang['globalFolderName'] = "Mapnaam";
$lang['globalFilename'] = "Bestandsnaam";
$lang['globalStream'] = "Stream";
$lang['globalSubmit'] = "Verstuur";
$lang['globalUpload'] = "Upload";
$lang['globalUpdate'] = "Update";
$lang['globalCancel'] = "Annuleren";
$lang['globalDelete'] = "Verwijderen";
$lang['globalCreate'] = "Aanmaken";
$lang['globalMove'] = "Verplaats";
$lang['globalJumpTo'] = "Verspring naar";
$lang['globalAutoShutdown'] = "Auto afsluiten";
$lang['globalIdleShutdown'] = "Afsluiten na inactiviteit";
$lang['globalAutoStopPlayout'] = "Stop Playout Timer";
$lang['globalStopTimer'] = "Stop Playout Timer";
$lang['globalSleepTimer'] = "Shutdown Timer";
$lang['globalExternalInterfaces'] = "Externe apparaten en interfaces";
$lang['globalIdleTime'] = "inactieve tijd";
$lang['globalNotIdle'] = "niet inactief";
$lang['globalGpioButtons'] = "GPIO knoppen";
$lang['globalRotaryKnob'] = "Draaiknop";
$lang['globalRfidReader'] = "RFID lezer";
$lang['globalEnabled'] = "Ingeschakeld";
$lang['globalDisabled'] = "Uitgeschakeld";
$lang['globalSwitchOn'] = "zet AAN";
$lang['globalSwitchOff'] = "zet UIT";
$lang['globalSystem'] = "Systeem";
$lang['globalVersion'] = "Versie";
$lang['globalDescription'] = "Omschrijving";
$lang['globalRelease'] = "Release";
$lang['globalStorage'] = "Opslag";
$lang['globalShuffle'] = "Shuffle";
$lang['globalReplay'] = "Opnieuw afspelen";
$lang['globalRepeat'] = "Herhalen";
$lang['globalLoop'] = "Loop";
$lang['globalLang'] = "Taal";
$lang['globalLanguageSettings'] = "Taalinstellingen";

$lang['playerFilePlayed'] = "is gespeeld";
$lang['playerFileAdded'] = "is toegevoegd aan de playlist";
$lang['playerFileDeleted'] = "is verwijderd";

// Edition (classic, +spotify)
$lang['globalEdition'] = "Editie";
$lang['classic'] = "Classic editie (barebones)";
$lang['plusSpotify'] = "Plus editie (incl. Spotify integratie)";

$lang['navEditionClassic'] = "Classic";
$lang['navEditionPlusSpotify'] = "+Spotify";

$lang['navBrand'] = "Phoniebox";
$lang['navHome'] = "Home";
$lang['navSearch'] = "Zoeken";
$lang['navSettings'] = "Instellingen";
$lang['navInfo'] = "Info";
$lang['navShutdown'] = "Afsluiten";
$lang['navReboot'] = "Herstarten";

$lang['indexAvailAudio'] = "Beschikbare audio";
$lang['indexContainsFiles'] = "Bevat de volgende bestand(en):";
$lang['indexShowFiles'] = "Toon bestanden";
$lang['indexManageFilesChips'] = "Beheer Bestanden en fiches";

$lang['Spotify'] = "Spotify";

/*
* Register & Edit Cards
*/
$lang['cardRegisterTitle'] = "Nieuwe kaart toevoegen";
$lang['cardEditTitle'] = "Nieuwe kaart toevoegen of bewerken";
$lang['cardRegisterMessageDefault'] = "De waarde 'Nieuwste kaart-ID' in het formulier wordt direct bijgewerkt terwijl u een RFID-kaart veegt. <br/> (Javascript in browser vereist om ingeschakeld te kunnen worden.)";
$lang['cardEditMessageDefault'] = "De kaart-ID's die in dit systeem worden gebruikt, staan ​​vermeld op de <a href='index.php' class='mainMenu'><i class='mdi mdi-home'></i> home page</a>.";
$lang['cardRegisterMessageSwipeNew'] = "Veeg nog een kaart als u meer kaarten wilt registreren.";
$lang['cardEditMessageInputNew'] = "Typ een andere kaart-ID en kies er een uit de lijst op de<a href='index.php' class='mainMenu'><i class='mdi mdi-home'></i> home page</a>.";
$lang['cardRegisterErrorTooMuch'] = "<p>Dit is te veel! Selecteer alstublieft slechts één audiomap. Maak een besluit.</p>";
$lang['cardRegisterErrorStreamAndAudio'] = "<p>Dit is te veel! Ofwel een stream of een audiomap. Maak een besluit.</p>";
$lang['cardRegisterErrorStreamOrAudio'] = "<p>Dit is niet genoeg! Voeg een URL toe inclusief streamtype of selecteer een audiomap. Of 'Annuleren' om terug te gaan naar de startpagina.</p>";
$lang['cardRegisterErrorExistingAndNew'] = "<p>Dit is te veel! Kies een bestaande map of maak een nieuwe map aan.</p>";
$lang['cardRegisterErrorExistingFolder'] = "<p>Er bestaat al een map met dezelfde naam! Kies een andere.</p>";
$lang['cardRegisterErrorSuggestFolder'] = "Er moet een mapnaam voor de stream worden gemaakt. Hieronder in het formulier heb ik een suggestie gedaan.";
$lang['cardRegisterStream2Card'] = "Stream is gekoppeld aan kaart-ID.";
$lang['cardRegisterFolder2Card'] = "De audiomap is nu gekoppeld aan kaart-ID";
$lang['cardRegisterDownloadingYT'] = "<p>YouTube-audio wordt gedownload. Dit kan een paar minuten duren. U kunt het logbestand 'youtube-dl.log' in de gedeelde map controleren.</p>";
$lang['cardRegisterSwipeUpdates'] = "Dit wordt automatisch bijgewerkt terwijl je een RFID-kaart veegt.";
$lang['cardRegisterManualLinks'] = "<p>U kunt kaarten ook handmatig met mappen verbinden. In de handleiding wordt uitgelegd hoe u <a href='https://github.com/chbuehlmann/RPi-Jukebox-RFID/wiki/MANUAL#connecting-to-the-phoniebox-to-add-files' target='–blank'>verbinding maakt met de phoniebox</a> en <a href='https://github.com/chbuehlmann/RPi-Jukebox-RFID/wiki/MANUAL#registering-cards-manually-through-samba-without-the-web-app' target='_blank'>kaarten registreert</a>.</p>";

/*
* Card edit form
*/
$lang['cardFormFolderLegend'] = "Audiomap";
$lang['cardFormFolderLabel'] = "a) Link kaart naar audiomap";
$lang['cardFormFolderSelectDefault'] = "Geen (Pulldown om een ​​map te selecteren)";
$lang['cardFormStreamLabel'] = "b) ... of maak verbinding met de Stream-URL";
$lang['cardFormStreamPlaceholderClassic'] = "Livestream: http(...).mp3 / .m3u / .ogg / ...";
$lang['cardFormStreamPlaceholderPlusSpotify'] = "spotify:album/artist/playlist/track:### / Livestream: http(...).mp3 / .m3u / .ogg / ...";
$lang['cardFormStreamHelp'] = "Voeg de URL toe voor spotify, podcast, webradio, stream of andere online media";
$lang['cardFormStreamTypeSelectDefault'] = "Selecteer type";
$lang['cardFormStreamTypeHelp'] = "Selecteer het type dat u toevoegt";
$lang['cardFormStreamFolderPlaceholder'] = "bijv. 'Album / Afspeellijst / Stationsnaam'";
$lang['cardFormStreamFolderHelp'] = "Naam voor de audiomap die de stream-URL bevat.";
$lang['cardFormYTLegend'] = "YouTube";
$lang['cardFormYTLabel'] = "c) ... of download YouTube-audio";
$lang['cardFormYTPlaceholder'] = "bijv. https://www.youtube.com/watch?v=7GI0VdPehQI";
$lang['cardFormYTSelectDefault'] = "Pulldown om een ​​map te selecteren of maak hieronder een nieuwe aan";
$lang['cardFormYTFolderPlaceholder'] = "bijv. 'Nieuwe Map'";
$lang['cardFormYTFolderHelp'] = "Naam voor de audiomap die de YouTube-audio bevat.";
$lang['cardFormYTHelp'] = "Voeg de volledige YouTube-URL toe zoals in het voorbeeld";
$lang['cardFormRemoveCard'] = "Verwijder kaart-ID";

/*
* Track edit form
*/
$lang['trackEditTitle'] = "Track management";
$lang['trackEditInformation'] = "Track informatie";
$lang['trackEditMove'] = "Verplaats track";
$lang['trackEditMoveSelectLabel'] = "Selecteer een nieuwe map";
$lang['trackEditMoveSelectDefault'] = "Verplaats het bestand niet";
$lang['trackEditDelete'] = "Verwijder track";
$lang['trackEditDeleteLabel'] = "Weet je zeker dat je wilt verwijderen???";
$lang['trackEditDeleteHelp'] = "Er is geen 'ongedaan maken' voor verwijderde bestanden. Ze zijn weg! Weet je het zeker?";
$lang['trackEditDeleteNo'] = "Verwijder deze track NIET";
$lang['trackEditDeleteYes'] = "Ja, VERWIJDER deze track";


/*
* Settings
*/
$lang['settingsVolChangePercent'] = "Vol. verandering %";
$lang['settingsMaxVol'] = "Maximaal Volume";
$lang['settingsWifiRestart'] = "De wijzigingen die zijn aangebracht op uw WiFi-verbinding vereisen dat een herstart van kracht wordt.";
$lang['settingsWifiSsidPlaceholder'] = "Bijv.: PhonieHomie";
$lang['settingsWifiSsidHelp'] = "De naam waaronder uw WiFi wordt weergegeven als 'beschikbaar netwerk'";
$lang['settingsSecondSwipe'] = "Tweede veeg";
$lang['settingsSecondSwipeInfo'] = "Wanneer u dezelfde RFID voor de tweede keer gebruikt, wat gebeurt er dan? Start de afspeellijst opnieuw? Schakelen tussen pauze / afspelen?";
$lang['settingsSecondSwipeRestart'] = "afspeellijst opnieuw afspelen";
$lang['settingsSecondSwipeSkipnext'] = "Ga naar het volgende nummer";
$lang['settingsSecondSwipePause'] = "Schakelen tussen pauze / afspelen";
$lang['settingsSecondSwipeNoAudioPlay'] = "Negeer audio playout-triggers, alleen systeemopdrachten";
$lang['settingsSecondSwipePauseInfo'] = "Negeer het opnieuw scannen van dezelfde kaart voor:";
$lang['second'] = "Seconde";
$lang['seconds'] = "Seconden";
$lang['settingsSecondSwipePauseControlsInfo'] = "Bepaalde functiekaarten (bijv. Volume omhoog / omlaag, volgende / vorige track, snel vooruit / terugspoelen) mogen geen vertraging hebben (zoals eerder ingesteld in de instelling):";
$lang['settingsSecondSwipePauseControlsOn'] = "Functiekaarten zonder vertraging";
$lang['settingsSecondSwipePauseControlsOff'] = "Functiekaarten met vertraging (seconden als voorheen)";
$lang['settingsWebInterface'] = "Web Interface";
$lang['settingsCoverInfo'] = "Wil je albumhoezen naast de albums en afspeellijsten op de hoofdpagina weergeven?";
$lang['settingsShowCoverON'] = "Albumhoes laten zien";
$lang['settingsShowCoverOFF'] = "Albumhoes niet laten zien";
$lang['settingsMessageLangfileNewItems'] = "Er zijn nieuwe taalitems in het oorspronkelijke <em> lang-en-UK.php </ em> -bestand. Uw taalbestand is bijgewerkt en bevat nu deze (in het Engels). Misschien wilt u uw taalbestand bijwerken en uw wijzigingen in de Phoniebox-code aanbrengen :) ";

/*
* System info
*/
$lang['infoOsDistrib'] = "OS-distributie";
$lang['infoOsCodename'] = "Codenaam";
$lang['infoOsTemperature'] = "Temperatuur";
$lang['infoOsThrottle'] = "Beperking";
$lang['infoStorageUsed'] = "Opslag gebruik";
$lang['infoMopidyStatus'] = "Mopidy Server Status";
$lang['infoMPDStatus'] = "MPD Server Status";

/*
* Folder Management and File Upload
*/
$lang['manageFilesFoldersTitle'] = "Mappen &amp; bestanden";
$lang['manageFilesFoldersUploadFilesLabel'] = "Selecteer bestanden van uw schijf";
$lang['manageFilesFoldersUploadLegend'] = "Upload bestanden";
$lang['manageFilesFoldersUploadLabel'] = "Selecteer en / of maak een nieuwe map";
$lang['manageFilesFoldersUploadFolderHelp'] = "Als u een nieuwe map selecteert EN een folder-naam opgeeft, wordt de nieuwe map in de geselecteerde map gemaakt.";
$lang['manageFilesFoldersNewFolderTitle'] = "Maak een nieuwe map";
$lang['manageFilesFoldersNewFolderPositionLegend'] = "Map positie";
$lang['manageFilesFoldersNewFolderPositionDefault'] = "De nieuwe map bevindt zich op het hoofdniveau of binnenin (kies hieronder)";
$lang['manageFilesFoldersErrorNewFolderName'] = "<p>Geen geldige mapnaam opgegeven.</p>";
$lang['manageFilesFoldersErrorNewFolder'] = "<p>Geen map geselecteerd of een geldige nieuwe map opgegeven.</p>";
$lang['manageFilesFoldersErrorNoNewFolder'] = "<p>Geen map geselecteerd of een geldige nieuwe map opgegeven.</p>";
$lang['manageFilesFoldersErrorNewFolderExists'] = "<p>Er bestaat al een map met die naam. Wees origineel, typ een nieuwe naam.</p>";
$lang['manageFilesFoldersErrorNewFolderNotParent'] = "<p>De bovenliggende map bestaat niet.</p>";
$lang['manageFilesFoldersSuccessNewFolder'] = "Nieuwe map gemaakt:";
$lang['manageFilesFoldersSelectDefault'] = "Trek naar beneden om een ​​map te selecteren en / of maak hieronder een nieuwe onderliggende map";

$lang['manageFilesFoldersRenewDB'] = "Database vernieuwen";
$lang['manageFilesFoldersLocalScan'] = "Scan muziekbibliotheek";
$lang['manageFilesFoldersRenewDBinfo'] = "Scan uw muziekbibliotheek na het uploaden van nieuwe bestanden of het verplaatsen van mappen. De scan is niet nodig om muziek te horen, maar het is noodzakelijk om nummerinformatie te zien in de Web UI. Alleen nieuwe of verplaatste bestanden worden gescand. Terwijl de scan wordt uitgevoerd, wordt mopidy gestopt. Nadat de scan is voltooid, start de mopidy automatisch. U kunt de serverstatus zien in het gedeelte Info.";

$lang['searchTitle'] = "Zoeken naar audiobestanden";
$lang['searchExample'] = "z.B. Moonlight";
$lang['searchSend'] = "Zoeken";
$lang['searchResult'] = "Zoekresultaten:";

/*
* Filter
*/
$lang['filterall'] = "Toon alles";
$lang['filterfile'] = "Bestanden";
$lang['filterlivestream'] = "Livestream";
$lang['filterpodcast'] = "Podcast";
$lang['filterspotify'] = "Spotify";
$lang['filteryoutube'] = "YouTube";
?>

