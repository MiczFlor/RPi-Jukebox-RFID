# helper scripts

## Analytics_AfterInstallScript.sh

Checks the system and all conf files to give some feedback in the case of problems.
Might be outdated...

## AssignIDs4Shortcuts.php

This script is used by the web app.
This script is called from the command line.
It reads a CSV file and creates shortcuts for audiofolders from the file.
It also creates a modified version of the file rfid_trigger_play.sh which controls the playout.
As a source it uses rfid_trigger_play.sh.sample

## CreateCsvFromShortcuts.php

This script is used by the web app.
This script is called from the command line.
It will read all shortcut files and create a CSV file with matching pairs
of RFID and audio folder name.
The created CSV file starts with the line
"id","value"

## CreatePodcastsKidsDeutsch.sh

Creates sample folders with files and streams 
inside the $AUDIOFOLDERSPATH directory

## CreateSampleAudiofoldersStreams.sh

Creates sample folders with files and streams 
inside the $AUDIOFOLDERSPATH directory

## DeleteAllConfig.sh

This script will delete all config files 
including mpd.conf and the like.

## DeleteSampleAudiofoldersStreams.sh

Deletes sample folders with files and streams 
inside the $AUDIOFOLDERSPATH directory

## cli-player.py

Command line player to play folders on the Phoniebox.

A command line replacement some functionality of the phoniebox-web-ui, which challenges the raspberry pi zero. 
Using this small script significantly reduces resource usage on the system.

## cli_ReadWifiIp.php

Reads out the IP of the Phoniebox in English language on boot.

## organizeFiles.py

A small script for conveniently organizing audio folders, 
linking them to RFID cards, finding audio folders that are currently 
not bound to any RFID card, and fixing broken links.

A command line replacement some functionality of the phoniebox-web-ui, which challenges the raspberry pi zero. 
Using this small script significantly reduces resource usage on the system.

## setup_autohotspot.sh

Script to setup the autohotspot feature. It automatically sets up a wifi hotspot if no known network is found.
This is already included in the main install script, but can also be manually run.

usage: 
setup_autohotspot.sh <jukeboxDir> <activation=YES|NO> <ssid> <countryCode (e.g. DE, GB, CZ, ...)> <password (8..63 characters)> <ipAdress>"

### activate
```
chmod +x ./scripts/helperscripts/setup_autohotspot.sh
./scripts/helperscripts/setup_autohotspot.sh . YES phoniebox DE PlayItLoud 10.0.0.5
```

### deactivate
```
chmod +x ./scripts/helperscripts/setup_autohotspot.sh
./scripts/helperscripts/setup_autohotspot.sh . NO
```
