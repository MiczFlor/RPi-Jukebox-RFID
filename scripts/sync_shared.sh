#!/bin/bash

# Description

# Set the date and time of now
NOW=`date +%Y-%m-%d.%H:%M:%S`

# USAGE EXAMPLES:
#
# syn shortcuts:
# ./sync_shared.sh -c=shortcuts -i=xxx
#
# syn audiofolders:
# ./sync_shared.sh -c=audiofolders -d=xxx
#
#
# VALID COMMANDS:
# shortcuts (with -i)
# audiofolders (with -d)

# The absolute path to the folder which contains all the scripts.
# Unless you are working with symlinks, leave the following line untouched.
PATHDATA="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
SHORTCUTSPATH="$PATHDATA/../shared/shortcuts"

# Edit 
REMOTESERVER="test.schiller-dev.de"
REMOTEPORT=22322
#REMOTESYNCPATH="/home/pi/test/Phoniebox/"
REMOTESYNCPATH="/mnt/station-phoniebox/"

# Common
SYNCSHORTCUTSPATH="${REMOTESYNCPATH}shortcuts/"
SYNCSAUDIOFILESPATH="${REMOTESYNCPATH}audiofolders/"

#############################################################
# $DEBUG TRUE|FALSE
# Read debug logging configuration file
. ${PATHDATA}/../settings/debugLogging.conf

if [ "${DEBUG_sync_shared_sh}" == "TRUE" ]; then echo "########### SCRIPT sync_shared.sh ($NOW) ##" >> ${PATHDATA}/../logs/debug.log; fi

###########################################################
# Read global configuration file (and create if not exists)
# create the global configuration file from single files - if it does not exist
if [ ! -f ${PATHDATA}/../settings/global.conf ]; then
    . ${PATHDATA}/inc.writeGlobalConfig.sh
fi
. ${PATHDATA}/../settings/global.conf
###########################################################

#############################################################
# Get args from command line (see Usage above)
# Read the args passed on by the command line
# see following file for details:
. ${PATHDATA}/inc.readArgsFromCommandLine.sh

if [ "${DEBUG_sync_shared_sh}" == "TRUE" ]; then echo "VAR COMMAND: ${COMMAND}" >> ${PATHDATA}/../logs/debug.log; fi
if [ "${DEBUG_sync_shared_sh}" == "TRUE" ]; then echo "VAR CARDID: ${CARDID}" >> ${PATHDATA}/../logs/debug.log; fi
if [ "${DEBUG_sync_shared_sh}" == "TRUE" ]; then echo "VAR FOLDER: ${FOLDER}" >> ${PATHDATA}/../logs/debug.log; fi
if [ "${DEBUG_sync_shared_sh}" == "TRUE" ]; then echo "VAR VALUE: ${VALUE}" >> ${PATHDATA}/../logs/debug.log; fi


case $COMMAND in
    shortcuts)
		if [ ! -f "${SHORTCUTSPATH}/${CARDID}" ]; then
			if [ "${DEBUG_sync_shared_sh}" == "TRUE" ]; then echo "Sync: Shortcut for $CARDID does not exist in $SHORTCUTSPATH -> syncing" >> $PATHDATA/../logs/debug.log; fi
			
			if nc -z $REMOTESERVER -w 1 $REMOTEPORT ; then
			
				if [ -f "${SYNCSHORTCUTSPATH}${CARDID}" ]; then
					RSYNCSHORTCUTSCMD=$(rsync -azi --no-o --no-g "${SYNCSHORTCUTSPATH}${CARDID}" "${SHORTCUTSPATH}")
					
					if [ $? -eq 0 -a -n "${RSYNCSHORTCUTSCMD}" ]; then
						if [ "${DEBUG_sync_shared_sh}" == "TRUE" ]; then echo "Sync: executed rsync ${RSYNCSHORTCUTSCMD}" >> ${PATHDATA}/../logs/debug.log; fi
						if [ "${DEBUG_sync_shared_sh}" == "TRUE" ]; then echo "Sync: files copied. setting rights" >> ${PATHDATA}/../logs/debug.log; fi
						
						sudo chown pi:www-data "${SHORTCUTSPATH}/${CARDID}"
						sudo chmod -R 777 "${SHORTCUTSPATH}/${CARDID}"
						
					else
						if [ "${DEBUG_sync_shared_sh}" == "TRUE" ]; then echo "Sync: nothing changed" >> ${PATHDATA}/../logs/debug.log; fi
					fi
					
				else 
					if [ "${DEBUG_sync_shared_sh}" == "TRUE" ]; then echo "Sync: Shortcut for $CARDID not found in REMOTE $SYNCSHORTCUTSPATH" >> ${PATHDATA}/../logs/debug.log; fi
				fi
				
			else 
				if [ "${DEBUG_sync_shared_sh}" == "TRUE" ]; then echo "Sync: Server is NOT reachable" >> ${PATHDATA}/../logs/debug.log; fi
			fi
			
		else 
			if [ "${DEBUG_sync_shared_sh}" == "TRUE" ]; then echo "Sync: Shortcut for $CARDID does exist in $SHORTCUTSPATH -> not syncing" >> $PATHDATA/../logs/debug.log; fi
		fi
        ;;
	audiofolders)
		if [ ! -d "${AUDIOFOLDERSPATH}/${FOLDER}" ]; then
			if [ "${DEBUG_sync_shared_sh}" == "TRUE" ]; then echo "Sync: Folder $FOLDER does not exist in $AUDIOFOLDERSPATH -> syncing" >> $PATHDATA/../logs/debug.log; fi
			
			if nc -z $REMOTESERVER -w 1 $REMOTEPORT ; then
			
				if [ -d "${SYNCSAUDIOFILESPATH}${FOLDER}" ]; then
					RSYNCSAUDIOFILES=$(rsync -azi --no-o --no-g "${SYNCSAUDIOFILESPATH}${FOLDER}/" "${AUDIOFOLDERSPATH}/${FOLDER}/")
					
					if [ $? -eq 0 -a -n "${RSYNCSAUDIOFILES}" ]; then
						if [ "${DEBUG_sync_shared_sh}" == "TRUE" ]; then echo "Sync: executed rsync ${RSYNCSAUDIOFILES}" >> ${PATHDATA}/../logs/debug.log; fi
						if [ "${DEBUG_sync_shared_sh}" == "TRUE" ]; then echo "Sync: files copied. setting rights and update database" >> ${PATHDATA}/../logs/debug.log; fi
						
						sudo chown pi:www-data "${AUDIOFOLDERSPATH}/${FOLDER}"
						sudo chmod -R 777 "${AUDIOFOLDERSPATH}/${FOLDER}"
						sudo mpc update --wait "${AUDIOFOLDERSPATH}/${FOLDER}" > /dev/null 2>&1
						
					else
						if [ "${DEBUG_sync_shared_sh}" == "TRUE" ]; then echo "Sync: nothing changed" >> ${PATHDATA}/../logs/debug.log; fi
					fi
					
				else 
					if [ "${DEBUG_sync_shared_sh}" == "TRUE" ]; then echo "Sync: Folder $FOLDER not found in REMOTE $SYNCSAUDIOFILESPATH" >> ${PATHDATA}/../logs/debug.log; fi
				fi
				
			else 
				if [ "${DEBUG_sync_shared_sh}" == "TRUE" ]; then echo "Sync: Server is NOT reachable" >> ${PATHDATA}/../logs/debug.log; fi
			fi
			
		else
			if [ "${DEBUG_sync_shared_sh}" == "TRUE" ]; then echo "Sync: Folder $FOLDER does exist in $AUDIOFOLDERSPATH -> not syncing" >> $PATHDATA/../logs/debug.log; fi
		fi
        ;;
	*)
        echo Unknown COMMAND $COMMAND
        if [ "${DEBUG_sync_shared_sh}" == "TRUE" ]; then echo "Unknown COMMAND ${COMMAND} CARDID ${CARDID} FOLDER ${FOLDER} VALUE ${VALUE}" >> ${PATHDATA}/../logs/debug.log; fi
        ;;
esac
