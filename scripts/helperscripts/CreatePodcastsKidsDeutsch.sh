#!/bin/bash

# Creates sample folders with files and streams 
# inside the $AUDIOFOLDERSPATH directory

PATHDATA="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"

# ZZZ-Podcast-DLF-Kinderhoerspiele (dir)
# * podcast.txt (file)
# * http://www.kakadu.de/podcast-kinderhoerspiel.3420.de.podcast.xml (content)

AUDIOFOLDERSPATH=`cat ../../settings/Audio_Folders_Path`

mkdir $AUDIOFOLDERSPATH/PODCASTS

mkdir $AUDIOFOLDERSPATH/PODCASTS/BR-Betthupferl
echo "https://feeds.br.de/betthupferl/feed.xml" > $AUDIOFOLDERSPATH/PODCASTS/BR-Betthupferl/podcast.txt

mkdir $AUDIOFOLDERSPATH/PODCASTS/Kakadu
echo "http://www.kakadu.de/podcast-kakadu.2730.de.podcast.xml" > $AUDIOFOLDERSPATH/PODCASTS/Kakadu/podcast.txt

mkdir $AUDIOFOLDERSPATH/PODCASTS/MDR-Figarino
echo "http://www.mdr.de/figarino/podcast/streiche102-podcast.xml" > $AUDIOFOLDERSPATH/PODCASTS/MDR-Figarino/podcast.txt

mkdir $AUDIOFOLDERSPATH/PODCASTS/WDR-Baerenbude
echo "https://kinder.wdr.de/radio/kiraka/hoeren/podcast/baerenbude192.podcast" > $AUDIOFOLDERSPATH/PODCASTS/WDR-Baerenbude/podcast.txt

mkdir $AUDIOFOLDERSPATH/PODCASTS/BR-Klaro-Nachrichten
echo "https://feeds.br.de/klaro-nachrichten-fuer-kinder/feed.xml" > $AUDIOFOLDERSPATH/PODCASTS/BR-Klaro-Nachrichten/podcast.txt

mkdir $AUDIOFOLDERSPATH/PODCASTS/WDR-KiRaKa
echo "https://kinder.wdr.de/radio/kiraka/hoeren/podcast/kinderhoerspiel-podcast-108.podcast" > $AUDIOFOLDERSPATH/PODCASTS/WDR-KiRaKa/podcast.txt

# chmod chown
sudo chown -R :www-data $AUDIOFOLDERSPATH/PODCASTS
sudo chmod -R 777 $AUDIOFOLDERSPATH/PODCASTS
