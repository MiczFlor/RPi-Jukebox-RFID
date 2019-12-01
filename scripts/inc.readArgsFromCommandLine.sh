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

# The absolute path to the folder whjch contains all the scripts.
# Unless you are working with symlinks, leave the following line untouched.
PATHDATA="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"

#############################################################
# $DEBUG TRUE|FALSE
# Read debug logging configuration file
. $PATHDATA/../settings/debugLogging.conf

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

if [ "${DEBUG_inc_readArgsFromCommandLine_sh}" == "TRUE" ]; then echo "  ######### SCRIPT inc.readArgsFromCommandLine.sh ($NOW) ##" >> $PATHDATA/../logs/debug.log; fi
if [ "${DEBUG_inc_readArgsFromCommandLine_sh}" == "TRUE" ]; then echo "  # VAR CARDID: $CARDID" >> $PATHDATA/../logs/debug.log; fi
if [ "${DEBUG_inc_readArgsFromCommandLine_sh}" == "TRUE" ]; then echo "  # VAR COMMAND: $COMMAND" >> $PATHDATA/../logs/debug.log; fi
if [ "${DEBUG_inc_readArgsFromCommandLine_sh}" == "TRUE" ]; then echo "  # VAR FOLDER: $FOLDER" >> $PATHDATA/../logs/debug.log; fi
if [ "${DEBUG_inc_readArgsFromCommandLine_sh}" == "TRUE" ]; then echo "  # VAR VALUE: $VALUE" >> $PATHDATA/../logs/debug.log; fi
