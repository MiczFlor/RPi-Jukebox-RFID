#!/bin/bash

# Runs a number of tests on command line level.
# In the terminal, you will see what you should be hearing
# as the script goes on.

# To create the matching sample content needed, run this script first:
# RPi-Jukebox-RFID/scripts/helperscripts/CreateSampleAudiofoldersStreams.sh

# Then you are set to run this.

# The absolute path to this folder
PATHDATA="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
# path to audio folders
AUDIOFOLDERSPATH=`cat $PATHDATA/../settings/Audio_Folders_Path`

# move to this directory to make sure relative paths work
cd $PATHDATA

echo ";;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;"
echo "; 1. direct play script:"
echo "; rfid_trigger_play.sh"
echo ";;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;"

echo "; 1.1 Play startup sound from folder ZZZ/MP3-StartUpSound"
echo "; Trying both ways to pass on data: -d and --dir"
echo "; /scripts/rfid_trigger_play.sh -d='ZZZ/MP3-StartUpSound'"
#$PATHDATA/../scripts/rfid_trigger_play.sh -d='ZZZ/MP3-StartUpSound'
echo "; /scripts/rfid_trigger_play.sh --dir='ZZZ/MP3-StartUpSound'"
#$PATHDATA/../scripts/rfid_trigger_play.sh --dir='ZZZ/MP3-StartUpSound'
echo ";;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;"

echo "; 1.2 Play startup sound from folder RFID shortcut ID"
echo "; Trying both ways to pass on data: -i and --cardid"
# Creating shortcut 'ZZZ_MP3-StartUpSound' to link to that folder
echo "ZZZ/MP3-StartUpSound" > $PATHDATA/../shared/shortcuts/ZZZ_MP3-StartUpSound
echo "; /scripts/rfid_trigger_play.sh -i='ZZZ_MP3-StartUpSound'"
#$PATHDATA/../scripts/rfid_trigger_play.sh -i='ZZZ_MP3-StartUpSound'
echo "; /scripts/rfid_trigger_play.sh --cardid='ZZZ_MP3-StartUpSound'"
#$PATHDATA/../scripts/rfid_trigger_play.sh --cardid='ZZZ_MP3-StartUpSound'
echo ";;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;"

echo "; 1.3 Whitespaces in folder name"
echo "; Play startup sound from folder 'ZZZ/MP3 Whitespace StartUpSound'"
echo "; /scripts/rfid_trigger_play.sh -d='ZZZ/MP3 Whitespace StartUpSound'"
#$PATHDATA/../scripts/rfid_trigger_play.sh -d='ZZZ/MP3 Whitespace StartUpSound'
echo ";;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;"

echo "; 1.4 Recursive play of sub folders"
echo "; Playing the following files:"
echo "; * ZZZ/SubMaster/fff-threeSubs/startupsound.mp3"
echo "; * ZZZ/SubMaster/fff-threeSubs/twoSubs/startupsound.mp3"
echo "; * ZZZ/SubMaster/fff-threeSubs/twoSubs/oneSub/startupsound.mp3"

echo "; Play startup sound from folder 'ZZZ/SubMaster/fff-threeSubs'"
echo "; /scripts/rfid_trigger_play.sh -d='ZZZ/SubMaster/fff-threeSubs' -v=recursive"
$PATHDATA/../scripts/rfid_trigger_play.sh -d='ZZZ/SubMaster/fff-threeSubs' -v=recursive
echo ";;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;"

echo "; 1.5 Test different audio formats on playout"
echo "; .mp3  .wav .aac .flac .ac3 .ogg .m4a .aiff .wma"
echo "; Play AudioFormatsTest-files in folder 'ZZZ/AudioFormatsTest'"
echo "; /scripts/rfid_trigger_play.sh -d='ZZZ/AudioFormatsTest'"
#$PATHDATA/../scripts/rfid_trigger_play.sh -d='ZZZ/AudioFormatsTest'
echo ";;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;"
# sleep long enough to listen to all of them: 28s
#sleep 28

echo
echo ";;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;"
echo "; 2. playout controls:"
echo "; playout_controls.sh"
echo ";;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;"

echo "; 2.1 Stop playlist after 2 seconds"
echo "; /scripts/playout_controls.sh -c=playerstop"
#$PATHDATA/../scripts/rfid_trigger_play.sh -d='ZZZ/ABC'
#echo "1 "; sleep 1; echo "2 "; sleep 1; echo "STOP"
#$PATHDATA/../scripts/playout_controls.sh -c=playerstop
echo ";;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;"

echo "; 2.2 Pause playlist after 2 seconds for 2 seconds"
echo "; /scripts/playout_controls.sh -c=playerpause"
#$PATHDATA/../scripts/rfid_trigger_play.sh -d='ZZZ/AudioFormatsTest'
#echo -n "1 "; sleep 1; echo -n "2 "; sleep 1; echo "PAUSE"
#$PATHDATA/../scripts/playout_controls.sh -c=playerpause
#echo -n "1 "; sleep 1; echo -n "2 "; sleep 1; echo "PLAY"
#$PATHDATA/../scripts/playout_controls.sh -c=playerpause
#echo -n "1 "; sleep 1; echo -n "2 "; sleep 1; echo "STOP"
#$PATHDATA/../scripts/playout_controls.sh -c=playerstop
echo ";;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;"

echo
echo ";;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;"
echo "; 3. shuffle playlist switch:"
echo "; shuffle_play.sh"
echo ";;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;"

echo "; 3.1 Read shuffle status from folder.conf"
echo "; Using folder 'ZZZ/AudioFormatsTest'"
echo "; Currently set to:"
TEMPFOLDER='ZZZ/AudioFormatsTest'
cat "$AUDIOFOLDERSPATH/$TEMPFOLDER/folder.conf" | grep SHUFFLE
echo ";;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;"

echo "; 3.2 Set shuffle status ON"
echo "; ... then play playlist for 5 seconds"
echo "; /scripts/shuffle_play.sh -c=enableshuffle -d='ZZZ/AudioFormatsTest'"
$PATHDATA/../scripts/shuffle_play.sh -c=enableshuffle -d="$TEMPFOLDER"
cat "$AUDIOFOLDERSPATH/$TEMPFOLDER/folder.conf" | grep SHUFFLE
#$PATHDATA/../scripts/rfid_trigger_play.sh -d="$TEMPFOLDER"
echo ";;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;"
#sleep 5; $PATHDATA/../scripts/playout_controls.sh -c=playerstop

echo "; 3.3 Set shuffle status OFF then play playlist"
echo "; ... then play playlist for 5 seconds"
echo "; /scripts/shuffle_play.sh -c=disableshuffle -d='ZZZ/AudioFormatsTest'"
$PATHDATA/../scripts/shuffle_play.sh -c=disableshuffle -d="$TEMPFOLDER"
cat "$AUDIOFOLDERSPATH/$TEMPFOLDER/folder.conf" | grep SHUFFLE
#$PATHDATA/../scripts/rfid_trigger_play.sh -d="$TEMPFOLDER"
echo ";;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;"
#sleep 5; $PATHDATA/../scripts/playout_controls.sh -c=playerstop

echo "; 3.4 Check shuffle status"
echo "; /scripts/shuffle_play.sh -c=shuffle_check"
#$PATHDATA/../scripts/shuffle_play.sh -c=shuffle_check -d="$TEMPFOLDER"
echo ";;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;"
cat "$AUDIOFOLDERSPATH/$TEMPFOLDER/folder.conf" | grep SHUFFLE

echo
echo ";;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;"
echo "; 4. Resume position (meaning save on stop):"
echo "; resume_play.sh"
echo ";;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;"

echo "; 4.1 Read shuffle status from folder.conf"
echo "; Using folder 'ZZZ/AudioFormatsTest'"
echo -n "; Currently set to:"
TEMPFOLDER='ZZZ/AudioFormatsTest'
cat "$AUDIOFOLDERSPATH/$TEMPFOLDER/folder.conf" | grep RESUME
echo ";;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;"

echo "; 3.2 Set resume status ON"
echo "; ... then play playlist for 3 seconds"
echo "; ... stop and wait for 2 seconds"
echo "; ... then start playlist (== resume)"
echo "; /scripts/resume_play.sh -c=enableresume -d='ZZZ/AudioFormatsTest'"
$PATHDATA/../scripts/resume_play.sh -c=enableresume -d="$TEMPFOLDER"
echo -n "; Currently set to:"
cat "$AUDIOFOLDERSPATH/$TEMPFOLDER/folder.conf" | grep RESUME
echo -n "; Current file last played:"
cat "$AUDIOFOLDERSPATH/$TEMPFOLDER/folder.conf" | grep CURRENTFILENAME
echo -n "; Current ELAPSED time:"
cat "$AUDIOFOLDERSPATH/$TEMPFOLDER/folder.conf" | grep ELAPSED
#$PATHDATA/../scripts/rfid_trigger_play.sh -d="$TEMPFOLDER"
echo ";;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;"
#sleep 3; $PATHDATA/../scripts/playout_controls.sh -c=playerstop
#sleep 2; $PATHDATA/../scripts/rfid_trigger_play.sh -d="$TEMPFOLDER"
#sleep 2; $PATHDATA/../scripts/playout_controls.sh -c=playerstop

echo "; 3.2 Set resume status OFF"
echo "; ... then play playlist for 3 seconds"
echo "; ... stop and wait for 2 seconds"
echo "; ... then start playlist (== resume)"
echo "; /scripts/resume_play.sh -c=enableresume -d='ZZZ/AudioFormatsTest'"
#$PATHDATA/../scripts/resume_play.sh -c=disableresume -d="$TEMPFOLDER"
echo -n "; Currently set to:"
cat "$AUDIOFOLDERSPATH/$TEMPFOLDER/folder.conf" | grep RESUME
echo -n "; Current file last played:"
cat "$AUDIOFOLDERSPATH/$TEMPFOLDER/folder.conf" | grep CURRENTFILENAME
echo -n "; Current ELAPSED time:"
cat "$AUDIOFOLDERSPATH/$TEMPFOLDER/folder.conf" | grep ELAPSED
#$PATHDATA/../scripts/rfid_trigger_play.sh -d="$TEMPFOLDER"
echo ";;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;"
#sleep 3; $PATHDATA/../scripts/playout_controls.sh -c=playerstop
#sleep 2; $PATHDATA/../scripts/rfid_trigger_play.sh -d="$TEMPFOLDER"
#sleep 2; $PATHDATA/../scripts/playout_controls.sh -c=playerstop


# single play

# save second swipe to rewrite later
# test second swipe start from top
# test second swipe do nothing
# test second swipe skip next
# test second swipe pause










