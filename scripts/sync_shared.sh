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


#############################################################
# $DEBUG TRUE|FALSE
# Read debug logging configuration file
. ${PATHDATA}/../settings/debugLogging.conf

if [ "${DEBUG_sync_shared_sh}" == "TRUE" ]; then echo "########### SCRIPT sync_shared.sh ($NOW) ##" >> ${PATHDATA}/../logs/debug.log; fi

#############################################################
# Read global configuration file (and create if not exists)
# create the global configuration file from single files - if it does not exist
if [ ! -f ${PATHDATA}/../settings/global.conf ]; then
    . ${PATHDATA}/inc.writeGlobalConfig.sh
fi
. ${PATHDATA}/../settings/global.conf

#############################################################
# Read configuration file
# create the configuration file from sample - if it does not exist
if [ ! -f ${PATHDATA}/../settings/sync_shared.conf ]; then
	echo "sync_shared.conf not present"
	if [ "${DEBUG_sync_shared_sh}" == "TRUE" ]; then echo "Sync: Conf not present. Write from sample" >> ${PATHDATA}/../logs/debug.log; fi
    cp ${PATHDATA}/../settings/sync_shared.conf.sample ${PATHDATA}/../settings/sync_shared.conf
    # change the read/write so that later this might also be editable through the web app
    sudo chown -R pi:www-data ${PATHDATA}/../settings/sync_shared.conf
    sudo chmod -R 775 ${PATHDATA}/../settings/sync_shared.conf
fi

. ${PATHDATA}/../settings/sync_shared.conf


if [ "${SYNCSHAREDENABLED}" != "TRUE" ]; then
	if [ "${DEBUG_sync_shared_sh}" == "TRUE" ]; then echo "Sync: disabled" >> ${PATHDATA}/../logs/debug.log; fi
			
else
	if [ "${DEBUG_sync_shared_sh}" == "TRUE" ]; then echo "Sync: enabled" >> ${PATHDATA}/../logs/debug.log; fi
	
	# Set local vars
	SYNCSHORTCUTSPATH="${SYNCSHAREDREMOTEPATH}shortcuts/"
	SYNCAUDIOFOLDERSPATH="${SYNCSHAREDREMOTEPATH}audiofolders/"

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
			if nc -z $SYNCSHAREDREMOTESERVER -w 1 $SYNCSHAREDREMOTEPORT ; then
			
				if [ ! -d "${SYNCSHORTCUTSPATH}" ]; then
					mkdir "${SYNCSHORTCUTSPATH}"
					if [ "${DEBUG_sync_shared_sh}" == "TRUE" ]; then echo "Sync: Folder ${SYNCSHORTCUTSPATH} does not exist. created" >> ${PATHDATA}/../logs/debug.log; fi
				fi
			
				if [ -f "${SYNCSHORTCUTSPATH}${CARDID}" ]; then
					RSYNCSHORTCUTSCMD=$(rsync -azui --no-o --no-g --no-times "${SYNCSHORTCUTSPATH}${CARDID}" "${SHORTCUTSPATH}")
					
					if [ $? -eq 0 -a -n "${RSYNCSHORTCUTSCMD}" ]; then
						if [ "${DEBUG_sync_shared_sh}" == "TRUE" ]; then echo "Sync: executed rsync ${RSYNCSHORTCUTSCMD}" >> ${PATHDATA}/../logs/debug.log; fi
						if [ "${DEBUG_sync_shared_sh}" == "TRUE" ]; then echo "Sync: files copied. setting rights" >> ${PATHDATA}/../logs/debug.log; fi
						
						sudo chown pi:www-data "${SHORTCUTSPATH}/${CARDID}"
						sudo chmod -R 775 "${SHORTCUTSPATH}/${CARDID}"
						
					else
						if [ "${DEBUG_sync_shared_sh}" == "TRUE" ]; then echo "Sync: nothing changed" >> ${PATHDATA}/../logs/debug.log; fi
					fi
					
				else 
					if [ "${DEBUG_sync_shared_sh}" == "TRUE" ]; then echo "Sync: Shortcut for $CARDID not found in REMOTE $SYNCSHORTCUTSPATH" >> ${PATHDATA}/../logs/debug.log; fi
				fi
				
			else 
				if [ "${DEBUG_sync_shared_sh}" == "TRUE" ]; then echo "Sync: Server is NOT reachable" >> ${PATHDATA}/../logs/debug.log; fi
			fi
			;;
		audiofolders)
			if nc -z $SYNCSHAREDREMOTESERVER -w 1 $SYNCSHAREDREMOTEPORT ; then
			
				if [ ! -d "${SYNCAUDIOFOLDERSPATH}" ]; then
					mkdir "${SYNCAUDIOFOLDERSPATH}"
					if [ "${DEBUG_sync_shared_sh}" == "TRUE" ]; then echo "Sync: Folder ${SYNCAUDIOFOLDERSPATH} does not exist. created" >> ${PATHDATA}/../logs/debug.log; fi
				fi
			
				if [ -d "${SYNCAUDIOFOLDERSPATH}${FOLDER}" ]; then
					RSYNCSAUDIOFILES=$(rsync -azui --no-o --no-g --no-perms --no-times --delete --exclude="folder.conf" "${SYNCAUDIOFOLDERSPATH}${FOLDER}/" "${AUDIOFOLDERSPATH}/${FOLDER}/")
					
					if [ $? -eq 0 -a -n "${RSYNCSAUDIOFILES}" ]; then
						if [ "${DEBUG_sync_shared_sh}" == "TRUE" ]; then echo "Sync: executed rsync ${RSYNCSAUDIOFILES}" >> ${PATHDATA}/../logs/debug.log; fi
						if [ "${DEBUG_sync_shared_sh}" == "TRUE" ]; then echo "Sync: files copied. setting rights and update database" >> ${PATHDATA}/../logs/debug.log; fi
						
						sudo chown -R pi:www-data "${AUDIOFOLDERSPATH}/${FOLDER}"
						sudo chmod -R 775 "${AUDIOFOLDERSPATH}/${FOLDER}"
						sudo mpc update --wait "${AUDIOFOLDERSPATH}/${FOLDER}" > /dev/null 2>&1
						
					else
						if [ "${DEBUG_sync_shared_sh}" == "TRUE" ]; then echo "Sync: nothing changed" >> ${PATHDATA}/../logs/debug.log; fi
					fi
					
				else 
					if [ "${DEBUG_sync_shared_sh}" == "TRUE" ]; then echo "Sync: Folder $FOLDER not found in REMOTE $SYNCAUDIOFOLDERSPATH" >> ${PATHDATA}/../logs/debug.log; fi
				fi
				
			else 
				if [ "${DEBUG_sync_shared_sh}" == "TRUE" ]; then echo "Sync: Server is NOT reachable" >> ${PATHDATA}/../logs/debug.log; fi
			fi
			;;
		*)
			echo Unknown COMMAND $COMMAND
			if [ "${DEBUG_sync_shared_sh}" == "TRUE" ]; then echo "Unknown COMMAND ${COMMAND} CARDID ${CARDID} FOLDER ${FOLDER} VALUE ${VALUE}" >> ${PATHDATA}/../logs/debug.log; fi
			;;
	esac

fi
