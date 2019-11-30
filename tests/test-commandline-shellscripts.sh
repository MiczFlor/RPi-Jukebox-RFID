#!/bin/bash

# Runs a number of tests on command line level.
# In the terminal, you will see what you should be hearing
# as the script goes on.

# To create the matching sample content needed, run this script first:
# RPi-Jukebox-RFID/scripts/helperscripts/CreateSampleAudiofoldersStreams.sh

# Then you are set to run this.

PATHDATA="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"

# move to this directory to make sure relative paths work
cd $PATHDATA

