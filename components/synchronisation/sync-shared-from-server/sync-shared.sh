#!/bin/bash

# Description

# Set the date and time of now
NOW=`date +%Y-%m-%d.%H:%M:%S`

# USAGE EXAMPLES:
#
# sync shortcuts:
# ./sync_shared.sh -c=shortcuts -i=xxx
#
# sync audiofolders:
# ./sync_shared.sh -c=audiofolders -d=xxx
# 
# sync full:
# ./sync_shared.sh -c=full
# 
# sync toggle SyncOnRfidScan:
# ./sync_shared.sh -c=changeOnRfidScan -v=toggle

#
#
# VALID COMMANDS:
# shortcuts (with -i)
# audiofolders (with -d)
# full
# changeOnRfidScan(with -v=on | off | toogle)

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
	if [ ! -f ${PROJROOTPATH}/settings/global.conf ]; then
		echo "Global settingsfile does not exist. Please call the script from an defined entrypoint"
		exit
	fi
	. ${PROJROOTPATH}/settings/global.conf

	#############################################################
	# Read configuration file
	if [ ! -f ${PROJROOTPATH}/settings/sync_shared.conf ]; then
		echo "Settingsfile does not exist. Please read ${PATHDATA}/README.md to set configuration"
		exit
	fi
	. ${PROJROOTPATH}/settings/sync_shared.conf
	
	#############################################################
	# Get args from command line (see Usage above)
	# Read the args passed on by the command line
	# see following file for details:
	. ${PROJROOTPATH}/scripts/inc.readArgsFromCommandLine.sh
	
	if [ "${DEBUG_sync_shared_sh}" == "TRUE" ]; then echo "VAR COMMAND: ${COMMAND}" >> ${PROJROOTPATH}/logs/debug.log; fi
	if [ "${DEBUG_sync_shared_sh}" == "TRUE" ]; then echo "VAR CARDID: ${CARDID}" >> ${PROJROOTPATH}/logs/debug.log; fi
	if [ "${DEBUG_sync_shared_sh}" == "TRUE" ]; then echo "VAR FOLDER: ${FOLDER}" >> ${PROJROOTPATH}/logs/debug.log; fi
	if [ "${DEBUG_sync_shared_sh}" == "TRUE" ]; then echo "VAR VALUE: ${VALUE}" >> ${PROJROOTPATH}/logs/debug.log; fi
	
	#############################################################
	# Set local vars after sync_shared.conf is read
	SYNCSHORTCUTSPATH="${SYNCSHAREDREMOTEPATH}/shortcuts"
	SYNCAUDIOFOLDERSPATH="${SYNCSHAREDREMOTEPATH}/audiofolders"
	

	#############################################################
	#############################################################
	# Functions
	function handle_changeOnRfidScan {
		case $VALUE in
			on)
				SYNCSHAREDONRFIDSCAN_NEW="TRUE"
				;;
			off)
				SYNCSHAREDONRFIDSCAN_NEW="FALSE"
				;;
			toggle)
				if [ "${SYNCSHAREDONRFIDSCAN}" == "TRUE" ]; then 
					SYNCSHAREDONRFIDSCAN_NEW="FALSE"
				else 
					SYNCSHAREDONRFIDSCAN_NEW="TRUE"
				fi
				;;
			*)	
				echo "Unknown VALUE $VALUE for COMMAND $COMMAND"
				if [ "${DEBUG_sync_shared_sh}" == "TRUE" ]; then echo "Unknown VALUE $VALUE for COMMAND $COMMAND" >> ${PROJROOTPATH}/logs/debug.log; fi
				;;
		esac

		if [ ! -z "${SYNCSHAREDONRFIDSCAN_NEW}" ]; then 
			if [ "${DEBUG_sync_shared_sh}" == "TRUE" ]; then echo "Sync: Set SYNCSHAREDONRFIDSCAN to $VALUE" >> ${PROJROOTPATH}/logs/debug.log; fi
			sed -i "s|^SYNCSHAREDONRFIDSCAN=.*|SYNCSHAREDONRFIDSCAN=\"$SYNCSHAREDONRFIDSCAN_NEW\"|g" ${PROJROOTPATH}/settings/sync_shared.conf
		fi
	}
	
	function change_access {
		local file_or_dir="$1"
		local group="$2"
		local mod="$3"
		
		sudo chgrp -R "${group}" "${file_or_dir}"
		sudo chmod -R "${mod}" "${file_or_dir}"
	}
	
	#############################################################
	#############################################################
	
	#############################################################
	# Sync all files for the specific command. 
	# Some special options are needed as the 'folder.conf' file will be generated on playback.
	# Explanation for rsync options:
	# "--itemize-changes" print a summary of copied files. Used for determination if files where changed (empty if no syncing performed). Useful for debug.log
	# "--safe-links" ignore symlinks that point outside the tree
	# "--times" preserve modification times from source. Recommended option to efficiently identify unchanged files
	# "--omit-dir-times" ignore modification time on dirs (see --times). Needed to ignore the creation of 'folder.conf' which alters the modification time of dirs
	# "--update" ignore newer files on destination. Lower traffic and runtime
	# "--delete" delete files that no longer exist in source
	# "--prune-empty-dirs" delete empty dirs (incl. subdirs)
	# "--filter="-rp folder.conf" exclude (option '-') 'folder.conf' file from deletion on receiving side (option 'r'). Delete anyway if folder will be deleted (option 'p' (perishable)).
	# "--exclude="placeholder" exclude 'placeholder' file from syncing, especially deletion
	case $COMMAND in
		shortcuts)
			if [ "${SYNCSHAREDONRFIDSCAN}" == "TRUE" ]; then 
				if nc -z $SYNCSHAREDREMOTESERVER -w $SYNCSHAREDREMOTETIMOUT $SYNCSHAREDREMOTEPORT ; then
				
					if [ ! -d "${SYNCSHORTCUTSPATH}" ]; then
						mkdir "${SYNCSHORTCUTSPATH}"
						if [ "${DEBUG_sync_shared_sh}" == "TRUE" ]; then echo "Sync: Folder ${SYNCSHORTCUTSPATH} does not exist. created" >> ${PROJROOTPATH}/logs/debug.log; fi
					
					elif [ -f "${SYNCSHORTCUTSPATH}/${CARDID}" ]; then
						RSYNCSHORTCUTSCMD=$(rsync --compress --recursive --itemize-changes --safe-links --times --omit-dir-times "${SYNCSHORTCUTSPATH}/${CARDID}" "${SHORTCUTSPATH}/")
						
						if [ $? -eq 0 -a -n "${RSYNCSHORTCUTSCMD}" ]; then
							if [ "${DEBUG_sync_shared_sh}" == "TRUE" ]; then echo "Sync: executed rsync ${RSYNCSHORTCUTSCMD}" >> ${PROJROOTPATH}/logs/debug.log; fi
							if [ "${DEBUG_sync_shared_sh}" == "TRUE" ]; then echo "Sync: files copied. setting rights" >> ${PROJROOTPATH}/logs/debug.log; fi
							
							change_access "${SHORTCUTSPATH}/${CARDID}" "www-data" "775"
							
						else
							if [ "${DEBUG_sync_shared_sh}" == "TRUE" ]; then echo "Sync: nothing changed" >> ${PROJROOTPATH}/logs/debug.log; fi
						fi
						
					else 
						if [ "${DEBUG_sync_shared_sh}" == "TRUE" ]; then echo "Sync: Shortcut for $CARDID not found in REMOTE $SYNCSHORTCUTSPATH" >> ${PROJROOTPATH}/logs/debug.log; fi
					fi
					
				else 
					if [ "${DEBUG_sync_shared_sh}" == "TRUE" ]; then echo "Sync: Server is NOT reachable" >> ${PROJROOTPATH}/logs/debug.log; fi
				fi
				
			else 
				if [ "${DEBUG_sync_shared_sh}" == "TRUE" ]; then echo "Sync: Sync on RFID scan deactivated" >> ${PROJROOTPATH}/logs/debug.log; fi
			fi
			;;
		audiofolders)
			if [ "${SYNCSHAREDONRFIDSCAN}" == "TRUE" ]; then 
				if nc -z $SYNCSHAREDREMOTESERVER -w $SYNCSHAREDREMOTETIMOUT $SYNCSHAREDREMOTEPORT ; then
				
					if [ ! -d "${SYNCAUDIOFOLDERSPATH}" ]; then
						mkdir "${SYNCAUDIOFOLDERSPATH}"
						if [ "${DEBUG_sync_shared_sh}" == "TRUE" ]; then echo "Sync: Folder ${SYNCAUDIOFOLDERSPATH} does not exist. created" >> ${PROJROOTPATH}/logs/debug.log; fi
					
					elif [ -d "${SYNCAUDIOFOLDERSPATH}/${FOLDER}" ]; then
						RSYNCSAUDIOFILES=$(rsync --compress --recursive --itemize-changes --safe-links --times --omit-dir-times --update --delete --prune-empty-dirs --filter="-rp folder.conf" "${SYNCAUDIOFOLDERSPATH}/${FOLDER}/" "${AUDIOFOLDERSPATH}/${FOLDER}/")
						
						if [ $? -eq 0 -a -n "${RSYNCSAUDIOFILES}" ]; then
							if [ "${DEBUG_sync_shared_sh}" == "TRUE" ]; then echo "Sync: executed rsync ${RSYNCSAUDIOFILES}" >> ${PROJROOTPATH}/logs/debug.log; fi
							if [ "${DEBUG_sync_shared_sh}" == "TRUE" ]; then echo "Sync: files copied. setting rights and update database" >> ${PROJROOTPATH}/logs/debug.log; fi
							
							change_access "${AUDIOFOLDERSPATH}/${FOLDER}" "www-data" "775"
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
							
			else 
				if [ "${DEBUG_sync_shared_sh}" == "TRUE" ]; then echo "Sync: Sync on RFID scan deactivated" >> ${PROJROOTPATH}/logs/debug.log; fi
			fi
			;;
		full)
			if nc -z $SYNCSHAREDREMOTESERVER -w $SYNCSHAREDREMOTETIMOUT $SYNCSHAREDREMOTEPORT ; then
			
				if [ ! -d "${SYNCSHORTCUTSPATH}" ]; then
					mkdir "${SYNCSHORTCUTSPATH}"
					if [ "${DEBUG_sync_shared_sh}" == "TRUE" ]; then echo "Sync: Folder ${SYNCSHORTCUTSPATH} does not exist. created" >> ${PROJROOTPATH}/logs/debug.log; fi
				else
					if [ "${DEBUG_sync_shared_sh}" == "TRUE" ]; then echo "Sync: Folder ${SYNCSHORTCUTSPATH}" >> ${PROJROOTPATH}/logs/debug.log; fi
					RSYNCSHORTCUTSCMD=$(rsync --compress --recursive --itemize-changes --safe-links --times --omit-dir-times --delete --prune-empty-dirs --exclude="placeholder" "${SYNCSHORTCUTSPATH}/" "${SHORTCUTSPATH}/")
					
					if [ $? -eq 0 -a -n "${RSYNCSHORTCUTSCMD}" ]; then
						if [ "${DEBUG_sync_shared_sh}" == "TRUE" ]; then echo "Sync: executed rsync ${RSYNCSHORTCUTSCMD}" >> ${PROJROOTPATH}/logs/debug.log; fi
						if [ "${DEBUG_sync_shared_sh}" == "TRUE" ]; then echo "Sync: files copied. setting rights" >> ${PROJROOTPATH}/logs/debug.log; fi
						
						change_access "${SHORTCUTSPATH}" "www-data" "775"
						
					else
						if [ "${DEBUG_sync_shared_sh}" == "TRUE" ]; then echo "Sync: nothing changed" >> ${PROJROOTPATH}/logs/debug.log; fi
					fi

				fi
					
				if [ ! -d "${SYNCAUDIOFOLDERSPATH}" ]; then
					mkdir "${SYNCAUDIOFOLDERSPATH}"
					if [ "${DEBUG_sync_shared_sh}" == "TRUE" ]; then echo "Sync: Folder ${SYNCAUDIOFOLDERSPATH} does not exist. created" >> ${PROJROOTPATH}/logs/debug.log; fi
				else
					if [ "${DEBUG_sync_shared_sh}" == "TRUE" ]; then echo "Sync: Folder ${SYNCAUDIOFOLDERSPATH}" >> ${PROJROOTPATH}/logs/debug.log; fi
					RSYNCSAUDIOFILES=$(rsync --compress --recursive --itemize-changes --safe-links --times --omit-dir-times --update --delete --prune-empty-dirs --filter="-rp folder.conf" --exclude="placeholder" "${SYNCAUDIOFOLDERSPATH}/" "${AUDIOFOLDERSPATH}/")
					
					if [ $? -eq 0 -a -n "${RSYNCSAUDIOFILES}" ]; then
						if [ "${DEBUG_sync_shared_sh}" == "TRUE" ]; then echo "Sync: executed rsync ${RSYNCSAUDIOFILES}" >> ${PROJROOTPATH}/logs/debug.log; fi
						if [ "${DEBUG_sync_shared_sh}" == "TRUE" ]; then echo "Sync: files copied. setting rights and update database" >> ${PROJROOTPATH}/logs/debug.log; fi
						
						change_access "${AUDIOFOLDERSPATH}" "www-data" "775"
						sudo mpc update --wait "${AUDIOFOLDERSPATH}" > /dev/null 2>&1
						
					else
						if [ "${DEBUG_sync_shared_sh}" == "TRUE" ]; then echo "Sync: nothing changed" >> ${PROJROOTPATH}/logs/debug.log; fi
					fi
					
				fi
				
			else 
				if [ "${DEBUG_sync_shared_sh}" == "TRUE" ]; then echo "Sync: Server is NOT reachable" >> ${PROJROOTPATH}/logs/debug.log; fi
			fi
			;;
		changeOnRfidScan)
			handle_changeOnRfidScan
			;;
		*)
			echo Unknown COMMAND $COMMAND
			if [ "${DEBUG_sync_shared_sh}" == "TRUE" ]; then echo "Unknown COMMAND ${COMMAND} CARDID ${CARDID} FOLDER ${FOLDER} VALUE ${VALUE}" >> ${PROJROOTPATH}/logs/debug.log; fi
			;;
	esac

fi
if [ "${DEBUG_sync_shared_sh}" == "TRUE" ]; then echo "########### SCRIPT sync_shared.sh ##" >> ${PROJROOTPATH}/logs/debug.log; fi