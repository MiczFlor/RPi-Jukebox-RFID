#!/bin/bash

# this file is called inside
# - resume_play.sh
# - rfid_trigger_play.sh
# - playout_controls.sh
# - inc.writeFolderConfig.sh
# ... and possibly more by the time you read this.
# It is meant to unify the variables which can be
# passed on to a script via the command line.

#############################################################
# Set the date and time of now
NOW=`date +%Y-%m-%d.%H:%M:%S`

for i in "$@"
do
    case $i in
        -i=*|--cardid=*)
        CARDID="${i#*=}"
        ;;
        -c=*|--command=*)
        COMMAND="${i#*=}"
        ;;
        -d=*|--dir=*)
        FOLDER="${i#*=}"
        ;;
        -v=*|--value=*)
        VALUE="${i#*=}"
        ;;
    esac
done

if [ $DEBUG == "true" ]; then echo "  ######### SCRIPT inc.readArgsFromCommandLine.sh ($NOW) ##" >> $PATHDATA/../logs/debug.log; fi
if [ $DEBUG == "true" ]; then echo "  # VAR CARDID: $CARDID" >> $PATHDATA/../logs/debug.log; fi
if [ $DEBUG == "true" ]; then echo "  # VAR COMMAND: $COMMAND" >> $PATHDATA/../logs/debug.log; fi
if [ $DEBUG == "true" ]; then echo "  # VAR FOLDER: $FOLDER" >> $PATHDATA/../logs/debug.log; fi
if [ $DEBUG == "true" ]; then echo "  # VAR VALUE: $VALUE" >> $PATHDATA/../logs/debug.log; fi
