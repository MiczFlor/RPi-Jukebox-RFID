#!/bin/bash

# Creates sample folders with streams for 
# * YouTube
# * Podcast
# * Web radio
# inside the shared/audiofolders directory
#
# ZZZ-Podcast-DLF-Kinderhoerspiele (dir)
# * podcast.txt (file)
# * http://www.kakadu.de/podcast-kinderhoerspiel.3420.de.podcast.xml (content)

mkdir ../../shared/audiofolders/ZZZ-Podcast-DLF-Kinderhoerspiele
echo "http://www.kakadu.de/podcast-kinderhoerspiel.3420.de.podcast.xml" > ../../shared/audiofolders/ZZZ-Podcast-DLF-Kinderhoerspiele/podcast.txt

# ZZZ-Podcast-Kakadu (dir)
# * podcast.txt (file)
# * http://www.kakadu.de/podcast-kakadu.2730.de.podcast.xml (content)

mkdir ../../shared/audiofolders/ZZZ-Podcast-Kakadu
echo "http://www.kakadu.de/podcast-kakadu.2730.de.podcast.xml" > ../../shared/audiofolders/ZZZ-Podcast-Kakadu/podcast.txt

# ZZZ-LiveStream-Bayern2 (dir)
# * livestream.txt (file)
# * http://br-br2-nord.cast.addradio.de/br/br2/nord/mp3/56/stream.mp3 (content)

mkdir ../../shared/audiofolders/ZZZ-LiveStream-Bayern2
echo "http://br-br2-nord.cast.addradio.de/br/br2/nord/mp3/56/stream.mp3" > ../../shared/audiofolders/ZZZ-LiveStream-Bayern2/livestream.txt

# ZZZ-YouTube-Phoniebox (dir)
# * youtube.txt (file)
# * https://youtu.be/7GI0VdPehQI (content) 

mkdir ../../shared/audiofolders/ZZZ-YouTube-Phoniebox
echo "https://youtu.be/7GI0VdPehQI" > ../../shared/audiofolders/ZZZ-YouTube-Phoniebox/youtube.txt

# ZZZ-MP3-StartUpSound (dir)
# * startupsound.mp3 (file)

mkdir ../../shared/audiofolders/ZZZ-MP3-StartUpSound
cp ../../misc/startupsound.mp3 ../../shared/audiofolders/ZZZ-MP3-StartUpSound/

# ZZZ MP3 Whitespace StartUpSound (dir)
# * startupsound.mp3 (file)

mkdir ../../shared/audiofolders/ZZZ\ MP3\ Whitespace\ StartUpSound
cp ../../misc/startupsound.mp3 ../../shared/audiofolders/ZZZ\ MP3\ Whitespace\ StartUpSound/






