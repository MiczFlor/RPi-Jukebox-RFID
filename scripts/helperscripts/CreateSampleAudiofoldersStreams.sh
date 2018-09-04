#!/bin/bash

# Creates sample folders with streams for 
# * YouTube
# * Podcast
# * Web radio
# inside the shared/audiofolders directory

# ZZZ-Podcast-DLF-Kinderhoerspiele (dir)
# * podcast.txt (file)
# * http://www.kakadu.de/podcast-kinderhoerspiel.3420.de.podcast.xml (content)

AUDIOFOLDERSPATH=`cat ../../settings/Audio_Folders_Path`

mkdir $AUDIOFOLDERSPATH/ZZZ-Podcast-DLF-Kinderhoerspiele
echo "http://www.kakadu.de/podcast-kinderhoerspiel.3420.de.podcast.xml" > $AUDIOFOLDERSPATH/ZZZ-Podcast-DLF-Kinderhoerspiele/podcast.txt

# ZZZ-Podcast-Kakadu (dir)
# * podcast.txt (file)
# * http://www.kakadu.de/podcast-kakadu.2730.de.podcast.xml (content)

mkdir $AUDIOFOLDERSPATH/ZZZ-Podcast-Kakadu
echo "http://www.kakadu.de/podcast-kakadu.2730.de.podcast.xml" > $AUDIOFOLDERSPATH/ZZZ-Podcast-Kakadu/podcast.txt

mkdir $AUDIOFOLDERSPATH/ZZZ-Podcast-WDR-Hörspielspeicher
echo "https://www1.wdr.de/mediathek/audio/hoerspiel-speicher/wdr_hoerspielspeicher150.podcast" > $AUDIOFOLDERSPATH/ZZZ-Podcast-WDR-Hörspielspeicher/podcast.txt

# ZZZ-LiveStream-Bayern2 (dir)
# * livestream.txt (file)
# * http://br-br2-nord.cast.addradio.de/br/br2/nord/mp3/56/stream.mp3 (content)

mkdir $AUDIOFOLDERSPATH/ZZZ-LiveStream-Bayern2
echo "http://br-br2-nord.cast.addradio.de/br/br2/nord/mp3/56/stream.mp3" > $AUDIOFOLDERSPATH/ZZZ-LiveStream-Bayern2/livestream.txt

# ZZZ-MP3-StartUpSound (dir)
# * startupsound.mp3 (file)

mkdir $AUDIOFOLDERSPATH/ZZZ-MP3-StartUpSound
cp ../../misc/sampleconfigs/startupsound.mp3.sample $AUDIOFOLDERSPATH/ZZZ-MP3-StartUpSound/startupsound.mp3

# ZZZ MP3 Whitespace StartUpSound (dir)
# * startupsound.mp3 (file)

mkdir $AUDIOFOLDERSPATH/ZZZ\ MP3\ Whitespace\ StartUpSound
cp ../../misc/sampleconfigs/startupsound.mp3.sample $AUDIOFOLDERSPATH/ZZZ\ MP3\ Whitespace\ StartUpSound/startupsound.mp3

# ZZZ-AudioFormatsTest (dir)
# * startupsound.mp3 (file)

mkdir $AUDIOFOLDERSPATH/ZZZ-AudioFormatsTest
cp ../../misc/audiofiletype* $AUDIOFOLDERSPATH/ZZZ-AudioFormatsTest/

# Now doing the same with nested subfolders
mkdir $AUDIOFOLDERSPATH/ZZZ-SubMaster
cp ../../misc/sampleconfigs/startupsound.mp3.sample $AUDIOFOLDERSPATH/ZZZ-SubMaster/startupsound.mp3

mkdir $AUDIOFOLDERSPATH/ZZZ-SubMaster/1-LiveStream-Bayern2
echo "http://br-br2-nord.cast.addradio.de/br/br2/nord/mp3/56/stream.mp3" > $AUDIOFOLDERSPATH/ZZZ-SubMaster/1-LiveStream-Bayern2/livestream.txt

mkdir $AUDIOFOLDERSPATH/ZZZ-SubMaster/WDR-Hörspielspeicher\ Podcast
echo "https://www1.wdr.de/mediathek/audio/hoerspiel-speicher/wdr_hoerspielspeicher150.podcast" > $AUDIOFOLDERSPATH/ZZZ-SubMaster/WDR-Hörspielspeicher\ Podcast/podcast.txt

mkdir $AUDIOFOLDERSPATH/ZZZ-SubMaster/100-MP3-StartUpSound
cp ../../misc/sampleconfigs/startupsound.mp3.sample $AUDIOFOLDERSPATH/ZZZ-SubMaster/100-MP3-StartUpSound/startupsound.mp3

mkdir $AUDIOFOLDERSPATH/ZZZ-SubMaster/AAA\ MP3\ Whitespace\ StartUpSound
cp ../../misc/sampleconfigs/startupsound.mp3.sample $AUDIOFOLDERSPATH/ZZZ-SubMaster/AAA\ MP3\ Whitespace\ StartUpSound/startupsound.mp3

mkdir $AUDIOFOLDERSPATH/ZZZ-SubMaster/bbb-AudioFormatsTest
cp ../../misc/audiofiletype* $AUDIOFOLDERSPATH/ZZZ-SubMaster/bbb-AudioFormatsTest/

mkdir $AUDIOFOLDERSPATH/ZZZ-SubMaster/CCC-Podcast-Kakadu
echo "http://www.kakadu.de/podcast-kakadu.2730.de.podcast.xml" > $AUDIOFOLDERSPATH/ZZZ-SubMaster/CCC-Podcast-Kakadu/podcast.txt

mkdir $AUDIOFOLDERSPATH/ZZZ-SubMaster/Podcast\ DLF\ Kinderhoerspiele
echo "http://www.kakadu.de/podcast-kinderhoerspiel.3420.de.podcast.xml" > $AUDIOFOLDERSPATH/ZZZ-SubMaster/Podcast\ DLF\ Kinderhoerspiele/podcast.txt

mkdir $AUDIOFOLDERSPATH/001-SubSub
cp -R $AUDIOFOLDERSPATH/ZZZ-SubMaster/* $AUDIOFOLDERSPATH/001-SubSub/
mv $AUDIOFOLDERSPATH/001-SubSub/ $AUDIOFOLDERSPATH/ZZZ-SubMaster/

mkdir $AUDIOFOLDERSPATH/ZZZ\ SubMaster\ Whitespaces
cp -R $AUDIOFOLDERSPATH/ZZZ-SubMaster/* $AUDIOFOLDERSPATH/ZZZ\ SubMaster\ Whitespaces/
