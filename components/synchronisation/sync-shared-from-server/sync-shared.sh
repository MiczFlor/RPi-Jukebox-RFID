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
PROJROOTPATH="$PATHDATA/../../.."
SHORTCUTSPATH="$PROJROOTPATH/shared/shortcuts"

#############################################################
# $DEBUG TRUE|FALSE
# Read debug logging configuration file
. ${PROJROOTPATH}/settings/debugLogging.conf

if [ "${DEBUG_sync_shared_sh}" == "TRUE" ]; then echo "########### SCRIPT sync_shared.sh ($NOW) ##" >> ${PROJROOTPATH}/logs/debug.log; fi

#######################
# Activation status of component sync-shared-from-server
SYNCSHAREDENABLED="FALSE"
if [ -f ${PROJROOTPATH}/settings/Sync_Shared_Enabled ]; then
    SYNCSHAREDENABLED=`cat ${PROJROOTPATH}/settings/Sync_Shared_Enabled`
fi


if [ "${SYNCSHAREDENABLED}" != "TRUE" ]; then
	if [ "${DEBUG_sync_shared_sh}" == "TRUE" ]; then echo "Sync: disabled" >> ${PROJROOTPATH}/logs/debug.log; fi
			
else
	if [ "${DEBUG_sync_shared_sh}" == "TRUE" ]; then echo "Sync: enabled" >> ${PROJROOTPATH}/logs/debug.log; fi

	#############################################################
	# Read global configuration file (and create if not exists)
	# create the global configuration file from single files - if it does not exist
	if [ ! -f ${PROJROOTPATH}/settings/global.conf ]; then
		. ${PROJROOTPATH}/scripts/inc.writeGlobalConfig.sh
	fi
	. ${PROJROOTPATH}/settings/global.conf

	#############################################################
	# Read configuration file
	# create the configuration file from sample - if it does not exist
	if [ ! -f ${PROJROOTPATH}/settings/sync_shared.conf ]; then
		echo "sync_shared.conf not present"
		if [ "${DEBUG_sync_shared_sh}" == "TRUE" ]; then echo "Sync: Conf not present. Write from sample" >> ${PROJROOTPATH}/logs/debug.log; fi
		cp ${PATHDATA}/settings/sync_shared.conf.sample ${PROJROOTPATH}/settings/sync_shared.conf
		# change the read/write so that later this might also be editable through the web app
		sudo chown -R pi:www-data ${PROJROOTPATH}/settings/sync_shared.conf
		sudo chmod -R 775 ${PROJROOTPATH}/settings/sync_shared.conf
	fi

	. ${PROJROOTPATH}/settings/sync_shared.conf

	
	# Set local vars
	SYNCSHORTCUTSPATH="${SYNCSHAREDREMOTEPATH}shortcuts/"
	SYNCAUDIOFOLDERSPATH="${SYNCSHAREDREMOTEPATH}audiofolders/"

	#############################################################
	# Get args from command line (see Usage above)
	# Read the args passed on by the command line
	# see following file for details:
	. ${PROJROOTPATH}/scripts/inc.readArgsFromCommandLine.sh

	if [ "${DEBUG_sync_shared_sh}" == "TRUE" ]; then echo "VAR COMMAND: ${COMMAND}" >> ${PROJROOTPATH}/logs/debug.log; fi
	if [ "${DEBUG_sync_shared_sh}" == "TRUE" ]; then echo "VAR CARDID: ${CARDID}" >> ${PROJROOTPATH}/logs/debug.log; fi
	if [ "${DEBUG_sync_shared_sh}" == "TRUE" ]; then echo "VAR FOLDER: ${FOLDER}" >> ${PROJROOTPATH}/logs/debug.log; fi
	if [ "${DEBUG_sync_shared_sh}" == "TRUE" ]; then echo "VAR VALUE: ${VALUE}" >> ${PROJROOTPATH}/logs/debug.log; fi


	case $COMMAND in
		shortcuts)
			if nc -z $SYNCSHAREDREMOTESERVER -w 1 $SYNCSHAREDREMOTEPORT ; then
			
				if [ ! -d "${SYNCSHORTCUTSPATH}" ]; then
					mkdir "${SYNCSHORTCUTSPATH}"
					if [ "${DEBUG_sync_shared_sh}" == "TRUE" ]; then echo "Sync: Folder ${SYNCSHORTCUTSPATH} does not exist. created" >> ${PROJROOTPATH}/logs/debug.log; fi
				fi
			
				if [ -f "${SYNCSHORTCUTSPATH}${CARDID}" ]; then
					RSYNCSHORTCUTSCMD=$(rsync -azui --no-o --no-g --no-times "${SYNCSHORTCUTSPATH}${CARDID}" "${SHORTCUTSPATH}")
					
					if [ $? -eq 0 -a -n "${RSYNCSHORTCUTSCMD}" ]; then
						if [ "${DEBUG_sync_shared_sh}" == "TRUE" ]; then echo "Sync: executed rsync ${RSYNCSHORTCUTSCMD}" >> ${PROJROOTPATH}/logs/debug.log; fi
						if [ "${DEBUG_sync_shared_sh}" == "TRUE" ]; then echo "Sync: files copied. setting rights" >> ${PROJROOTPATH}/logs/debug.log; fi
						
						sudo chown pi:www-data "${SHORTCUTSPATH}/${CARDID}"
						sudo chmod -R 775 "${SHORTCUTSPATH}/${CARDID}"
						
					else
						if [ "${DEBUG_sync_shared_sh}" == "TRUE" ]; then echo "Sync: nothing changed" >> ${PROJROOTPATH}/logs/debug.log; fi
					fi
					
				else 
					if [ "${DEBUG_sync_shared_sh}" == "TRUE" ]; then echo "Sync: Shortcut for $CARDID not found in REMOTE $SYNCSHORTCUTSPATH" >> ${PROJROOTPATH}/logs/debug.log; fi
				fi
				
			else 
				if [ "${DEBUG_sync_shared_sh}" == "TRUE" ]; then echo "Sync: Server is NOT reachable" >> ${PROJROOTPATH}/logs/debug.log; fi
			fi
			;;
		audiofolders)
			if nc -z $SYNCSHAREDREMOTESERVER -w 1 $SYNCSHAREDREMOTEPORT ; then
			
				if [ ! -d "${SYNCAUDIOFOLDERSPATH}" ]; then
					mkdir "${SYNCAUDIOFOLDERSPATH}"
					if [ "${DEBUG_sync_shared_sh}" == "TRUE" ]; then echo "Sync: Folder ${SYNCAUDIOFOLDERSPATH} does not exist. created" >> ${PROJROOTPATH}/logs/debug.log; fi
				fi
			
				if [ -d "${SYNCAUDIOFOLDERSPATH}${FOLDER}" ]; then
					RSYNCSAUDIOFILES=$(rsync -azui --no-o --no-g --no-perms --no-times --delete --exclude="folder.conf" "${SYNCAUDIOFOLDERSPATH}${FOLDER}/" "${AUDIOFOLDERSPATH}/${FOLDER}/")
					
					if [ $? -eq 0 -a -n "${RSYNCSAUDIOFILES}" ]; then
						if [ "${DEBUG_sync_shared_sh}" == "TRUE" ]; then echo "Sync: executed rsync ${RSYNCSAUDIOFILES}" >> ${PROJROOTPATH}/logs/debug.log; fi
						if [ "${DEBUG_sync_shared_sh}" == "TRUE" ]; then echo "Sync: files copied. setting rights and update database" >> ${PROJROOTPATH}/logs/debug.log; fi
						
						sudo chown -R pi:www-data "${AUDIOFOLDERSPATH}/${FOLDER}"
						sudo chmod -R 775 "${AUDIOFOLDERSPATH}/${FOLDER}"
						sudo mpc update --wait "${AUDIOFOLDERSPATH}/${FOLDER}" > /dev/null 2>&1
						
					else
						if [ "${DEBUG_sync_shared_sh}" == "TRUE" ]; then echo "Sync: nothing changed" >> ${PROJROOTPATH}/logs/debug.log; fi
					fi
					
				else 
					if [ "${DEBUG_sync_shared_sh}" == "TRUE" ]; then echo "Sync: Folder $FOLDER not found in REMOTE $SYNCAUDIOFOLDERSPATH" >> ${PROJROOTPATH}/logs/debug.log; fi
				fi
				
			else 
				if [ "${DEBUG_sync_shared_sh}" == "TRUE" ]; then echo "Sync: Server is NOT reachable" >> ${PROJROOTPATH}/logs/debug.log; fi
			fi
			;;
		*)
			echo Unknown COMMAND $COMMAND
			if [ "${DEBUG_sync_shared_sh}" == "TRUE" ]; then echo "Unknown COMMAND ${COMMAND} CARDID ${CARDID} FOLDER ${FOLDER} VALUE ${VALUE}" >> ${PROJROOTPATH}/logs/debug.log; fi
			;;
	esac

fi
if [ "${DEBUG_sync_shared_sh}" == "TRUE" ]; then echo "########### SCRIPT sync_shared.sh ##" >> ${PROJROOTPATH}/logs/debug.log; fi