#!/bin/bash

# Deletes sample folders with files and streams 
# inside the $AUDIOFOLDERSPATH directory

PATHDATA="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
AUDIOFOLDERSPATH=`cat ../../settings/Audio_Folders_Path`

sudo rm -rf $AUDIOFOLDERSPATH/ZZZ\ MP3\ Whitespace\ StartUpSound
sudo rm -rf $AUDIOFOLDERSPATH/ZZZ\ SubMaster\ Whitespaces
sudo rm -rf $AUDIOFOLDERSPATH/ZZZ\ This\ American\ Life\ Podcast
sudo rm -rf $AUDIOFOLDERSPATH/ZZZ-AudioFormatsTest
sudo rm -rf $AUDIOFOLDERSPATH/ZZZ-LiveStream-Bayern2
sudo rm -rf $AUDIOFOLDERSPATH/ZZZ-MP3-StartUpSound
sudo rm -rf $AUDIOFOLDERSPATH/ZZZ-Podcast-DLF-Kinderhoerspiele
sudo rm -rf $AUDIOFOLDERSPATH/ZZZ-SubMaster
