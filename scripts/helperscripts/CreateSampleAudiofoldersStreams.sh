#!/bin/bash

# Creates sample folders with files and streams 
# inside the $AUDIOFOLDERSPATH directory

PATHDATA="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"

# move to this directory to make sure relative paths work
cd $PATHDATA

# ZZZ-Podcast-DLF-Kinderhoerspiele (dir)
# * podcast.txt (file)
# * http://www.kakadu.de/podcast-kinderhoerspiel.3420.de.podcast.xml (content)

AUDIOFOLDERSPATH=`cat ../../settings/Audio_Folders_Path`

mkdir $AUDIOFOLDERSPATH/ZZZ/

mkdir $AUDIOFOLDERSPATH/ZZZ/Podcast-DLF-Kinderhoerspiele
echo "http://www.kakadu.de/podcast-kinderhoerspiel.3420.de.podcast.xml" > $AUDIOFOLDERSPATH/ZZZ/Podcast-DLF-Kinderhoerspiele/podcast.txt

#mkdir $AUDIOFOLDERSPATH/ZZZ/Podcast-Kakadu
#echo "http://www.kakadu.de/podcast-kakadu.2730.de.podcast.xml" > $AUDIOFOLDERSPATH/ZZZ/Podcast-Kakadu/podcast.txt

#mkdir $AUDIOFOLDERSPATH/ZZZ/Podcast-WDR-Hörspielspeicher
#echo "https://www1.wdr.de/mediathek/audio/hoerspiel-speicher/wdr_hoerspielspeicher150.podcast" > $AUDIOFOLDERSPATH/ZZZ/Podcast-WDR-Hörspielspeicher/podcast.txt

mkdir $AUDIOFOLDERSPATH/ZZZ/This\ American\ Life\ Podcast
echo "http://feed.thisamericanlife.org/talpodcast" > $AUDIOFOLDERSPATH/ZZZ/This\ American\ Life\ Podcast/podcast.txt

# ZZZ-LiveStream-Bayern2 (dir)
# * livestream.txt (file)
# * http://br-br2-nord.cast.addradio.de/br/br2/nord/mp3/56/stream.mp3 (content)

mkdir $AUDIOFOLDERSPATH/ZZZ/LiveStream-Bayern2
echo "http://br-br2-nord.cast.addradio.de/br/br2/nord/mp3/56/stream.mp3" > $AUDIOFOLDERSPATH/ZZZ/LiveStream-Bayern2/livestream.txt

# ZZZ-MP3-StartUpSound (dir)
# * startupsound.mp3 (file)

mkdir $AUDIOFOLDERSPATH/ZZZ/MP3-StartUpSound
cp $PATHDATA/../../misc/sampleconfigs/startupsound.mp3.sample $AUDIOFOLDERSPATH/ZZZ/MP3-StartUpSound/startupsound.mp3

# ZZZ MP3 Whitespace StartUpSound (dir)
# * startupsound.mp3 (file)

mkdir $AUDIOFOLDERSPATH/ZZZ/MP3\ Whitespace\ StartUpSound
cp $PATHDATA/../../misc/sampleconfigs/startupsound.mp3.sample $AUDIOFOLDERSPATH/ZZZ/MP3\ Whitespace\ StartUpSound/startupsound.mp3

# ZZZ-AudioFormatsTest (dir)
# * startupsound.mp3 (file)

mkdir $AUDIOFOLDERSPATH/ZZZ/Counting/
cp $PATHDATA/../../misc/number* $AUDIOFOLDERSPATH/ZZZ/Counting/

mkdir $AUDIOFOLDERSPATH/ZZZ/ABC/
cp $PATHDATA/../../misc/alphabet* $AUDIOFOLDERSPATH/ZZZ/ABC/

mkdir $AUDIOFOLDERSPATH/ZZZ/AudioFormatsTest
cp $PATHDATA/../../misc/audiofiletype* $AUDIOFOLDERSPATH/ZZZ/AudioFormatsTest/

###########################################
# Now doing the same with nested subfolders
mkdir $AUDIOFOLDERSPATH/ZZZ/SubMaster
cp $PATHDATA/../../misc/sampleconfigs/startupsound.mp3.sample $AUDIOFOLDERSPATH/ZZZ/SubMaster/startupsound.mp3

# start nested with jump back two levels
mkdir $AUDIOFOLDERSPATH/ZZZ/SubMaster/fff-threeSubs
cp $PATHDATA/../../misc/sampleconfigs/startupsound.mp3.sample $AUDIOFOLDERSPATH/ZZZ/SubMaster/fff-threeSubs/startupsound.mp3
mkdir $AUDIOFOLDERSPATH/ZZZ/SubMaster/fff-threeSubs/twoSubs
cp $PATHDATA/../../misc/sampleconfigs/startupsound.mp3.sample $AUDIOFOLDERSPATH/ZZZ/SubMaster/fff-threeSubs/twoSubs/startupsound.mp3
mkdir $AUDIOFOLDERSPATH/ZZZ/SubMaster/fff-threeSubs/twoSubs/oneSub
cp $PATHDATA/../../misc/sampleconfigs/startupsound.mp3.sample $AUDIOFOLDERSPATH/ZZZ/SubMaster/fff-threeSubs/twoSubs/oneSub/startupsound.mp3

mkdir $AUDIOFOLDERSPATH/ZZZ/SubMaster/1-LiveStream-Bayern2
echo "http://br-br2-nord.cast.addradio.de/br/br2/nord/mp3/56/stream.mp3" > $AUDIOFOLDERSPATH/ZZZ/SubMaster/1-LiveStream-Bayern2/livestream.txt

mkdir $AUDIOFOLDERSPATH/ZZZ/SubMaster/This\ American\ Life\ Podcast
echo "http://feed.thisamericanlife.org/talpodcast" > $AUDIOFOLDERSPATH/ZZZ/SubMaster/This\ American\ Life\ Podcast/podcast.txt

mkdir $AUDIOFOLDERSPATH/ZZZ/SubMaster/100-MP3-StartUpSound
cp $PATHDATA/../../misc/sampleconfigs/startupsound.mp3.sample $AUDIOFOLDERSPATH/ZZZ/SubMaster/100-MP3-StartUpSound/startupsound.mp3

mkdir $AUDIOFOLDERSPATH/ZZZ/SubMaster/AAA\ MP3\ Whitespace\ StartUpSound
cp $PATHDATA/../../misc/sampleconfigs/startupsound.mp3.sample $AUDIOFOLDERSPATH/ZZZ/SubMaster/AAA\ MP3\ Whitespace\ StartUpSound/startupsound.mp3

mkdir $AUDIOFOLDERSPATH/ZZZ/SubMaster/bbb-AudioFormatsTest
cp $PATHDATA/../../misc/audiofiletype* $AUDIOFOLDERSPATH/ZZZ/SubMaster/bbb-AudioFormatsTest/

mkdir $AUDIOFOLDERSPATH/ZZZ/SubMaster\ Whitespaces
cp -R $AUDIOFOLDERSPATH/ZZZ/SubMaster/* $AUDIOFOLDERSPATH/ZZZ/SubMaster\ Whitespaces/

# chmod chown
sudo chown -R :www-data $AUDIOFOLDERSPATH/ZZZ*
sudo chmod -R 777 $AUDIOFOLDERSPATH/ZZZ*
