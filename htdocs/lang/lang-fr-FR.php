<?php
$lang = array();

$lang['globalEdit'] = "Editer";
$lang['globalResume'] = "Reprendre";
$lang['globalPassword'] = "Mot de passe";
$lang['globalOff'] = "OFF";
$lang['globalOn'] = "ON";
$lang['globalSingle'] = "Single";
$lang['globalTrack'] = "Piste";
$lang['globalList'] = "Lister";
$lang['globalPlaylist'] = "Playlist";
$lang['globalCardId'] = "Numero de série carte RFID";
$lang['globalRFIDCard'] = "Carte RFID";
$lang['globalRFIDCards'] = "Cartes RFID";
$lang['globalCardIdPlaceholder'] = "ex '1234567890'";
$lang['globalCardIdHelp'] = "The ID is usually printed on the card or fob. A list of used IDs can be found on the home page.";
$lang['globalRegisterCard'] = "Enregistrer une nouvelle carte";
$lang['globalRegisterCardShort'] = "Liste des cartes";
$lang['globalLastUsedCard'] = "Dernière carte utilisée";
$lang['globalClose'] = "Fermer";
$lang['globalPlay'] = "Lecture";
$lang['globalVolume'] = "Volume";
$lang['globalVolumeSettings'] = "Paramètres du volume";
$lang['globalWifi'] = "WiFi";
$lang['globalWifiSettings'] = "Paramètres WiFi";
$lang['globalWifiNetwork'] = "Paramètres WiFi";
$lang['globalSSID'] = "SSID";
$lang['globalSet'] = "Définir";
$lang['globalSettings'] = "Paramètres";
$lang['globalFolder'] = "Dossier";
$lang['globalFolderName'] = "Nom du dossier";
$lang['globalFilename'] = "Nom du fichier";
$lang['globalStream'] = "Stream";
$lang['globalSubmit'] = "Envoyer";
$lang['globalUpload'] = "Upload";
$lang['globalUpdate'] = "Mettre à jour";
$lang['globalCancel'] = "Annuler";
$lang['globalDelete'] = "Supprimer";
$lang['globalCreate'] = "Créer";
$lang['globalMove'] = "Déplacer";
$lang['globalJumpTo'] = "Aller à";
$lang['globalAutoShutdown'] = "Arrêt automatique";
$lang['globalIdleShutdown'] = "Arrêt après inactivité";
$lang['globalAutoStopPlayout'] = "Stop Playout Timer";
$lang['globalStopTimer'] = "Stop Playout Timer";
$lang['globalSleepTimer'] = "Minuteur d'arrêt";
$lang['globalShutdownVolumeReduction'] = "Shutdown Timer Volume Reduction";
$lang['globalExternalInterfaces'] = "Périphériques externes";
$lang['globalIdleTime'] = "Idle Time";
$lang['globalNotIdle'] = "Not Idle";
$lang['globalGpioButtons'] = "Bouttons GPIO";
$lang['globalRotaryKnob'] = "Rotary Knob";
$lang['globalRfidReader'] = "Lecteur RFID";
$lang['globalEnabled'] = "Activé";
$lang['globalDisabled'] = "Desactivé";
$lang['globalSwitchOn'] = "Allumer";
$lang['globalSwitchOff'] = "Eteindre";
$lang['globalSystem'] = "Systeme";
$lang['globalVersion'] = "Version";
$lang['globalDescription'] = "Description";
$lang['globalRelease'] = "Release";
$lang['globalStorage'] = "Stockage";
$lang['globalShuffle'] = "Aléatoire";
$lang['globalReplay'] = "Replay";
$lang['globalRepeat'] = "Repeat";
$lang['globalLoop'] = "Loop";
$lang['globalLang'] = "Langue";
$lang['globalLanguageSettings'] = "Paramètre de langue";
$lang['globalPriority'] = "Priorité";
$lang['globalEmail'] = "Email";
$lang['globalAudioSink'] = "Périphériques audio";

// Player title HTML
$lang['playerSeekBack'] = "retour arrière";
$lang['playerSeekAhead'] = "avancer";
$lang['playerSkipPrev'] = "piste précedente";
$lang['playerSkipNext'] = "piste suivante";
$lang['playerPlayPause'] = "lecture / pause";
$lang['playerReplay'] = "rejouer la piste";
$lang['playerLoop'] = "boucle";
$lang['playerStop'] = "stop";
$lang['playerVolDown'] = "baisser le volume";
$lang['playerVolUp'] = "augmenter le volume";
$lang['playerMute'] = "silence";
$lang['playerFilePlayed'] = "lecture en cours";
$lang['playerFileAdded'] = "ajouté à la playlist";
$lang['playerFileDeleted'] = "supprimer";


// Edition (classic, +spotify)
$lang['globalEdition'] = "Edition";
$lang['classic'] = "Classic edition (barebones)";
$lang['plusSpotify'] = "Plus edition (feat. Spotify integration)";

$lang['navEditionClassic'] = "Classic";
$lang['navEditionPlusSpotify'] = "+Spotify";

$lang['navBrand'] = "Phoniebox";
$lang['navHome'] = "Lecteur";
$lang['navSearch'] = "Recherche";
$lang['navSettings'] = "Paramètres";
$lang['navInfo'] = "Info";
$lang['navShutdown'] = "Eteindre";
$lang['navReboot'] = "Redemarrer";

$lang['indexAvailAudio'] = "Titres disponibles";
$lang['indexContainsFiles'] = "Contient les fichiers suivants:";
$lang['indexShowFiles'] = "Afficher les fichiers";
$lang['indexManageFilesChips'] = "Gestion des fichiers et des cartes";

$lang['Spotify'] = "Spotify";

/*
* Register & Edit Cards
*/
$lang['cardRegisterTitle'] = "Ajouter une carte";
$lang['cardEditTitle'] = "Modifier ou ajouter une carte";
$lang['cardRegisterAnchorLink'] = "Enregistrement interactif d'une carte";
$lang['cardRegisterMessageDefault'] = "The 'Latest Card ID' value in the form is updated on the fly as you swipe a RFID card.<br/>(Requires Javascript in the browser to be enabled.)";
$lang['cardEditMessageDefault'] = "Les cartes utilisées par le systeme sont listées ici <a href='index.php' class='mainMenu'><i class='mdi mdi-home'></i> accueil</a>.";
$lang['cardRegisterMessageSwipeNew'] = "Passer une autre carte si vous souhaitez en enregistrer une autre.";
$lang['cardEditMessageInputNew'] = "Type another card ID pick one from the list on the <a href='index.php' class='mainMenu'><i class='mdi mdi-home'></i> home page</a>.";
$lang['cardRegisterErrorTooMuch'] = "<p>This is too much! Please select only one audiofolder. Make up your mind.</p>";
$lang['cardRegisterErrorStreamAndAudio'] = "<p>This is too much! Either specify a stream or select an audio folder or system command. Make up your mind.</p>";
$lang['cardRegisterErrorStreamOrAudio'] = "<p>Seems you haven't selected anything! Add an URL and stream type, select a folder or a system command. Or 'Cancel' to go back to the home page.</p>";
$lang['cardRegisterErrorExistingAndNew'] = "<p>This is too much! Either choose an existing folder or create a new one.</p>";
$lang['cardRegisterErrorExistingFolder'] = "<p>A folder named with the same name already exists! Chose a different one.</p>";
$lang['cardRegisterErrorSuggestFolder'] = "A folder name for the stream needs to be created. Below in the form I made a suggestion.";
$lang['cardRegisterErrorConvertSpotifyURL'] = "URL Spotify incorrecte, elle a été convertie au bon format";
$lang['cardRegisterStream2Card'] = "Le stream est lié à la carte.";
$lang['cardRegisterFolder2Card'] = "Le dossier audio est désormais lié à une carte.";
$lang['cardRegisterDownloadingYT'] = "<p>Piste YouTube en cours de téléchargement. Cela peut prendre plusieurs minutes. Log dans le fichier \"youtube-dl.log\".</p>";
$lang['cardRegisterSwipeUpdates'] = "Mise à jour automatique lors du passage d'une carte.";
$lang['cardRegisterManualLinks'] = "<p>Vous pouvez lier manuellement une carte à un dossier. Explication dans la documentation <a href='https://github.com/MiczFlor/RPi-Jukebox-RFID/wiki/MANUAL#connect' target='–blank'>connection à phoniebox</a> et <a href='https://github.com/MiczFlor/RPi-Jukebox-RFID/wiki/MANUAL#registering-cards-manually-through-samba-without-the-web-app' target='_blank'>enregistrer une carte</a>.</p>";
$lang['cardRegisterTriggerSuccess'] = "La carte est désormais lié à une commande :";

/*
* Card edit form
*/
$lang['cardFormFolderLegend'] = "Lier la carte RFID à:";
$lang['cardFormFolderLabel'] = "Lier une carte à un dossier";
$lang['cardFormFolderSelectDefault'] = "Aucun (faites défiler pour choisir un dossier)";
$lang['cardFormFolderHelp'] = "Containing local files or add YouTube content (specify below).";
$lang['cardFormNewFolderLabel'] = "... ou liez un nouveau dossier";
$lang['cardFormNewFolderHelp'] = "Always use a new folder for streams (see below) and optionally for YouTube.";
$lang['cardFormNewFolderPlaceholder'] = "ex 'Nom de l'artiste/Album'";
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
$lang['trackEditTitle'] = "Gestion des pistes";
$lang['trackEditInformation'] = "Information sur la piste";
$lang['trackEditMove'] = "Déplacer une piste";
$lang['trackEditMoveSelectLabel'] = "Selectionner un dossier";
$lang['trackEditMoveSelectDefault'] = "Ne pas déplacer le fichier";
$lang['trackEditDelete'] = "Supprimer la piste";
$lang['trackEditDeleteLabel'] = "Etes vous sûr de vouloir supprimer ?";
$lang['trackEditDeleteHelp'] = "Aucun retour arrière pour la suppression d'une piste. Etes vous sûr ?";
$lang['trackEditDeleteNo'] = "Non, ne pas supprimer cette piste";
$lang['trackEditDeleteYes'] = "Oui, supprimer cette piste";

/*
* Settings
*/
$lang['settingsPlayoutBehaviourCard'] = "Paramètrage du lecteur RFID";
$lang['settingsPlayoutBehaviourCardLabel'] = "Passer ou poser la carte ?";
$lang['settingsPlayoutBehaviourCardSwipe'] = "Passer une carte lance le lecteur.";
$lang['settingsPlayoutBehaviourCardPlace'] = "Poser la carte pour lancer la lecture, l'enlever pour stopper.";
$lang['settingsPlayoutBehaviourCardHelp'] = "Si vous choisissez 'poser la carte', Cela affecte le deuxième passage.";

$lang['settingsVolChangePercent'] = "Changement du volume %";
$lang['settingsMaxVol'] = "Volume maximum";
$lang['settingsStartupVol'] = "Volume au démarrage";
$lang['settingsBootVol'] = "Volume après reboot";
$lang['settingsWifiRestart'] = "Les changements sur la configuration Wifi nécessitent un redémarrage.";
$lang['settingsWifiSsidPlaceholder'] = "ex: PhonieHomie";
$lang['settingsWifiSsidHelp'] = "Le nom de votre réseau Wifi 'mon super réseau'";
$lang['settingsWifiPassHelp'] = "Mot de passe Wifi (8 caractères minimum)";
$lang['settingsWifiPrioHelp'] = "Priorité du Wifi (0-100). Si plusieurs Wifi sont détéctés la box se connectera à celui qui a la priorité la plus haute.";
$lang['settingsSecondSwipe'] = "Deuxième passage de carte";
$lang['settingsSecondSwipeInfo'] = "Que se passe t'il lors du deuuxième passage d'une même carte ? Lecture / Pause ?";
$lang['settingsSecondSwipeRestart'] = "Reprendre la playlist au début";
$lang['settingsSecondSwipeSkipnext'] = "Piste suivante";
$lang['settingsSecondSwipePause'] = "Pause / Lecture";
$lang['settingsSecondSwipePlay'] = "Reprendre";
$lang['settingsSecondSwipeNoAudioPlay'] = "Ignorer les déclenchements automatiques, uniquement pour les commandes systeme";
$lang['settingsSecondSwipePauseInfo'] = "Ignorer le scan des nouvelle carte pour :";
$lang['second'] = "seconde";
$lang['seconds'] = "secondes";
$lang['settingsSecondSwipePauseControlsInfo'] = "Certain type de carte (ex augmentation et diminution du volume, piste suivante et précedente, reculer / avancer) ne devraient pas avoir de délai :";
$lang['settingsSecondSwipePauseControlsOn'] = "Utiliser la carte immédiatement";
$lang['settingsSecondSwipePauseControlsOff'] = "Utiliser la carte après un délai (secondes)";
$lang['settingsWebInterface'] = "Interface web";
$lang['settingsCoverInfo'] = "Voulez vous afficher les couvertures de vos playlist et titres ?";
$lang['settingsShowCoverON'] = "Afficher la couverture";
$lang['settingsShowCoverOFF'] = "Ne pas afficher la couverture";
$lang['settingsMessageLangfileNewItems'] = "Il y a des nouveautés pour le fichier de langue <em>lang-fr-FR.php</em>. Envoyer vos modiffications sur Github :)";
$lang['settingsWlanSendNav'] = "Envoyer l'IP par mail";
$lang['settingsWlanSendInfo'] = "Envoyer l'IP par mail après reboot ? (pratique si vous êtes en IP dynamique et qe vous souhaitez vous connecter)";
$lang['settingsWlanSendQuest'] = "Envoyer l'IP par mail ?";
$lang['settingsWlanSendEmail'] = "email";
$lang['settingsWlanSendON'] = "Oui, envoyer par mail";
$lang['settingsWlanSendOFF'] = "Non, ne pas envoyer par mail";

$lang['settingsVolumeManager'] = "Sélectionner le gestionnaire de volume";

$lang['settingsWlanReadNav'] = "Lecture de l'IP";
$lang['settingsWlanReadInfo'] = "Récupérer l'IP (wifi) après chaque reboot ? (pratique si vous êtes en IP dynamique et qe vous souhaitez vous connecter)";
$lang['settingsWlanReadQuest'] = "Lire mon IP réseau ?";
$lang['settingsWlanReadON'] = "Oui, lire mon IP.";
$lang['settingsWlanReadOFF'] = "Non, ne pas lire mon IP.";

/*
* System info
*/
$lang['infoOsDistrib'] = "Distribtion Linux";
$lang['infoOsCodename'] = "Version de l'OS";
$lang['infoOsTemperature'] = "Température";
$lang['infoOsThrottle'] = "Throttling";
$lang['infoStorageUsed'] = "Utilisation disque";
$lang['infoMopidyStatus'] = "Etat du serveur Mopidy";
$lang['infoMPDStatus'] = "Etat du serveur MPD";
$lang['infoDebugLogTail'] = "<b>Fichier debug</b>: Les 40 dernières lignes";
$lang['infoDebugLogClear'] = "Effacer le contenu du fichier debug.log";
$lang['infoDebugLogSettings'] = "Paramètres de debug";
$lang['infoAudioActive'] = "Périphériques audio activés";
$lang['infoBluetoothStatus'] = "Etat du Bluetooth";

/*
* Folder Management and File Upload
*/
$lang['manageFilesFoldersTitle'] = "Dossier &amp; Fichier";
$lang['manageFilesFoldersUploadFilesLabel'] = "Sélection du fichier depuis votre PC";
$lang['manageFilesFoldersUploadLegend'] = "Uploader un fichier";
$lang['manageFilesFoldersUploadLabel'] = "Sélectionner un dossier ou en créer un nouveau";
$lang['manageFilesFoldersUploadFolderHelp'] = "Si vous selectionnez un dossier ET que vous en créez un, le nouveau dossier sera inclus dans celui selectionné.";
$lang['manageFilesFoldersNewFolderTitle'] = "Créer un nouveau dossier";
$lang['manageFilesFoldersNewFolderPositionLegend'] = "Position du dossier";
$lang['manageFilesFoldersNewFolderPositionDefault'] = "Le nouveau dossier peut être à la racine ou inclus dans un dossier existant";
$lang['manageFilesFoldersErrorNewFolderName'] = "<p>Nom du dossier invalide.</p>";
$lang['manageFilesFoldersErrorNewFolder'] = "<p>Aucun dossier selectionné ou aucun dossier valide renseigné.</p>";
$lang['manageFilesFoldersErrorNoNewFolder'] = "<p>Aucun dossier selectionné ou aucun dossier valide renseigné.</p>";
$lang['manageFilesFoldersErrorNewFolderExists'] = "<p>Le dossier existe deja.</p>";
$lang['manageFilesFoldersErrorNewFolderNotParent'] = "<p>Le dossier parent est absent.</p>";
$lang['manageFilesFoldersSuccessNewFolder'] = "Création du nouveau dossier ok: ";
$lang['manageFilesFoldersSelectDefault'] = "Faites défiler pour choisir un dossier existant ou créez en un nouveau";

$lang['manageFilesFoldersRenewDB'] = "Renouvellement de la base";
$lang['manageFilesFoldersLocalScan'] = "Scanner la bibliothèque";
$lang['manageFilesFoldersRenewDBinfo'] = "Il est conseillé de scanner votre librairie après chaque ajout de fichier ou modification de dossier. Seules les nouvelles musiques ou les modifications seront scannées. Modipy sera stoppé lors du scan et relancé automatiquement à la fin du scan.";

/*
* File search
*/
$lang['searchTitle'] = "Recherche de fichiers audio";
$lang['searchExample'] = "ex Stromae";
$lang['searchSend'] = "Rechercher";
$lang['searchResult'] = "Resultats:";

/*
* Filter
*/
$lang['filterall'] = "Tout afficher";
$lang['filterfile'] = "Fichiers";
$lang['filterlivestream'] = "Livestream";
$lang['filterpodcast'] = "Podcast";
$lang['filterspotify'] = "Spotify";
$lang['filteryoutube'] = "YouTube";
?>
