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
PROJROOTPATH="${PATHDATA}/../../.."

#############################################################
# $DEBUG TRUE|FALSE
# Read debug logging configuration file
. "${PROJROOTPATH}"/settings/debugLogging.conf

if [ "${DEBUG_sync_shared_sh}" == "TRUE" ]; then echo "########### SCRIPT sync_shared.sh (${NOW}) ##" >> "${PROJROOTPATH}"/logs/debug.log; fi

#######################
# Activation status of component sync-shared-from-server
SYNCSHAREDENABLED="FALSE"
if [ -f "${PROJROOTPATH}/settings/Sync_Shared_Enabled" ]; then
    SYNCSHAREDENABLED=`cat "${PROJROOTPATH}/settings/Sync_Shared_Enabled"`
fi


if [ "$SYNCSHAREDENABLED" != "TRUE" ]; then
	if [ "${DEBUG_sync_shared_sh}" == "TRUE" ]; then echo "Sync: disabled" >> "${PROJROOTPATH}"/logs/debug.log; fi
			
else
	if [ "${DEBUG_sync_shared_sh}" == "TRUE" ]; then echo "Sync: enabled" >> "${PROJROOTPATH}"/logs/debug.log; fi
	
	#############################################################
	# Read global configuration file (and create if not exists)
	if [ ! -f "${PROJROOTPATH}/settings/global.conf" ]; then
		echo "Global settingsfile does not exist. Please call the script from a defined entrypoint"
		if [ "${DEBUG_sync_shared_sh}" == "TRUE" ]; then echo "Sync: Global settingsfile does not exist. Please call the script from a defined entrypoint" >> "${PROJROOTPATH}"/logs/debug.log; fi
		exit
	fi
	. "${PROJROOTPATH}"/settings/global.conf

	#############################################################
	# Read configuration file
	if [ ! -f "${PROJROOTPATH}/settings/sync_shared.conf" ]; then
		echo "Settingsfile does not exist. Please read ${PATHDATA}/README.md to set configuration"
		if [ "${DEBUG_sync_shared_sh}" == "TRUE" ]; then echo "Sync: Settingsfile does not exist. Please read ${PATHDATA}/README.md to set configuration" >> "${PROJROOTPATH}"/logs/debug.log; fi
		exit
	fi
	. "${PROJROOTPATH}"/settings/sync_shared.conf
	
	#############################################################
	# Get args from command line (see Usage above)
	# Read the args passed on by the command line
	# see following file for details:
	. "${PROJROOTPATH}"/scripts/inc.readArgsFromCommandLine.sh
	
	if [ "${DEBUG_sync_shared_sh}" == "TRUE" ]; then echo "VAR COMMAND: ${COMMAND}" >> "${PROJROOTPATH}"/logs/debug.log; fi
	if [ "${DEBUG_sync_shared_sh}" == "TRUE" ]; then echo "VAR CARDID: ${CARDID}" >> "${PROJROOTPATH}"/logs/debug.log; fi
	if [ "${DEBUG_sync_shared_sh}" == "TRUE" ]; then echo "VAR FOLDER: ${FOLDER}" >> "${PROJROOTPATH}"/logs/debug.log; fi
	if [ "${DEBUG_sync_shared_sh}" == "TRUE" ]; then echo "VAR VALUE: ${VALUE}" >> "${PROJROOTPATH}"/logs/debug.log; fi
	
	#############################################################
	# Set local vars after confs are read
	# Make sure paths dont have a trailing slash ({VAR%/})
	SYNCSHAREDREMOTEPATH="${SYNCSHAREDREMOTEPATH%/}"
	SYNCSHORTCUTSPATH="${SYNCSHAREDREMOTEPATH}/shortcuts"
	SYNCAUDIOFOLDERSPATH="${SYNCSHAREDREMOTEPATH}/audiofolders"
	
	LOCAL_SHORTCUTSPATH="${PROJROOTPATH}/shared/shortcuts"
	LOCAL_AUDIOFOLDERSPATH="${AUDIOFOLDERSPATH%/}"

	#############################################################
	#############################################################
	# Functions
	
	# Check if the sync mode is SSH
	is_mode_ssh() {
		[ "$SYNCSHAREDMODE" == "SSH" ]
	}
	
	# Executes the command for the current mode
	exec_for_mode() {
		if is_mode_ssh ; then
			# Quote every param to deal with whitespaces in paths
			local quotedparams
			for var in "$@"
			do
				quotedparams="${quotedparams} \"${var}\""
			done
			
			# Execute remote via SSH
			ssh "$SYNCSHAREDREMOTESSHUSER"@"$SYNCSHAREDREMOTESERVER" -p "$SYNCSHAREDREMOTEPORT" "$quotedparams"
		else
			# Execute local on mount
			"$@"
		fi
	}
	
	# Check if server is reachable on port
	is_server_reachable() {
		return `nc -z "$SYNCSHAREDREMOTESERVER" -w "$SYNCSHAREDREMOTETIMOUT" "$SYNCSHAREDREMOTEPORT"`
	}
	
	# Sync all files from source to destination
	# Some special options are needed as the 'folder.conf' file will be generated on playback.
	# Explanation for rsync options:
	# "--itemize-changes" print a summary of copied files. Used for determination if files where changed (empty if no syncing performed). Useful for debug.log
	# "--safe-links" ignore symlinks that point outside the tree
	# "--times" preserve modification times from source. Recommended option to efficiently identify unchanged files
	# "--omit-dir-times" ignore modification time on dirs (see --times). Needed to ignore the creation of 'folder.conf' which alters the modification time of dirs
	# "--delete" delete files that no longer exist in source
	# "--prune-empty-dirs" delete empty dirs (incl. subdirs)
	# "--filter='-rp folder.conf' exclude (option '-') 'folder.conf' file from deletion on receiving side (option 'r'). Delete anyway if folder will be deleted (option 'p' (perishable)).
	# "--exclude='placeholder' exclude 'placeholder' file from syncing, especially deletion
	# "--exclude='.*/' exclude special 'hidden' folders from syncing
	# "--exclude='@*/' exclude special folders from syncing
	sync_from_server() {
		local src_path="$1"
		local dst_path="$2"
		local update_mpc="$3"
		
		if is_mode_ssh ; then
			local ssh_port=(-e "ssh -p ${SYNCSHAREDREMOTEPORT}")
			local ssh_conn="${SYNCSHAREDREMOTESSHUSER}@${SYNCSHAREDREMOTESERVER}:"
		fi

		rsync_changes=$(rsync --compress --recursive --itemize-changes --safe-links --times --omit-dir-times --delete --prune-empty-dirs --filter='-rp folder.conf' --exclude='placeholder' --exclude='.*/' --exclude='@*/' "${ssh_port[@]}" "${ssh_conn}""${src_path}" "${dst_path}")

		if [ $? -eq 0 -a -n "$rsync_changes" ]; then
			if [ "${DEBUG_sync_shared_sh}" == "TRUE" ]; then echo -e "Sync: executed rsync \n${rsync_changes}" >> "${PROJROOTPATH}"/logs/debug.log; fi
			
			if [ "${DEBUG_sync_shared_sh}" == "TRUE" ]; then echo "Sync: files copied. change access of files" >> "${PROJROOTPATH}"/logs/debug.log; fi
			change_access "$dst_path" "www-data" "775"
			
			if [ ! -z "$update_mpc" ]; then
				if [ "${DEBUG_sync_shared_sh}" == "TRUE" ]; then echo "Sync: update database" >> "${PROJROOTPATH}"/logs/debug.log; fi
				sudo mpc update --wait "$dst_path" > /dev/null 2>&1
			fi
			
		else
			if [ "${DEBUG_sync_shared_sh}" == "TRUE" ]; then echo "Sync: nothing changed" >> "${PROJROOTPATH}"/logs/debug.log; fi
		fi
	}
	
	# Sync shortcut CARDID
	handle_shortcuts() {
		if [ "$SYNCSHAREDONRFIDSCAN" == "TRUE" ]; then 
			if is_server_reachable ; then
						
				if exec_for_mode [ ! -d "$SYNCSHORTCUTSPATH" ] ; then
					exec_for_mode mkdir "$SYNCSHORTCUTSPATH"
					if [ "${DEBUG_sync_shared_sh}" == "TRUE" ]; then echo "Sync: Folder ${SYNCSHORTCUTSPATH} does not exist. created" >> "${PROJROOTPATH}"/logs/debug.log; fi
				
				elif exec_for_mode [ -f "${SYNCSHORTCUTSPATH}/${CARDID}" ] ; then
					sync_from_server "${SYNCSHORTCUTSPATH}/${CARDID}" "${LOCAL_SHORTCUTSPATH}/${CARDID}"
					
				else 
					if [ "${DEBUG_sync_shared_sh}" == "TRUE" ]; then echo "Sync: Shortcut for $CARDID not found in REMOTE $SYNCSHORTCUTSPATH" >> "${PROJROOTPATH}"/logs/debug.log; fi
				fi
				
			else 
				if [ "${DEBUG_sync_shared_sh}" == "TRUE" ]; then echo "Sync: Server is NOT reachable" >> "${PROJROOTPATH}"/logs/debug.log; fi
			fi
			
		else 
			if [ "${DEBUG_sync_shared_sh}" == "TRUE" ]; then echo "Sync: Sync on RFID scan deactivated" >> "${PROJROOTPATH}"/logs/debug.log; fi
		fi
	}
	
	# Sync audiofolder FOLDER
	handle_audiofolders() {
		if [ "$SYNCSHAREDONRFIDSCAN" == "TRUE" ]; then 
			if is_server_reachable ; then
			
				if exec_for_mode [ ! -d "$SYNCAUDIOFOLDERSPATH" ] ; then
					exec_for_mode mkdir "$SYNCAUDIOFOLDERSPATH"
					if [ "${DEBUG_sync_shared_sh}" == "TRUE" ]; then echo "Sync: Folder ${SYNCAUDIOFOLDERSPATH} does not exist. created" >> "${PROJROOTPATH}"/logs/debug.log; fi
				
				elif exec_for_mode [ -d "${SYNCAUDIOFOLDERSPATH}/${FOLDER}" ] ; then
					sync_from_server "${SYNCAUDIOFOLDERSPATH}/${FOLDER}/" "${LOCAL_AUDIOFOLDERSPATH}/${FOLDER}/" "UpdateMPC"
					
				else 
					if [ "${DEBUG_sync_shared_sh}" == "TRUE" ]; then echo "Sync: Folder $FOLDER not found in REMOTE $SYNCAUDIOFOLDERSPATH" >> "${PROJROOTPATH}"/logs/debug.log; fi
				fi
				
			else 
				if [ "${DEBUG_sync_shared_sh}" == "TRUE" ]; then echo "Sync: Server is NOT reachable" >> "${PROJROOTPATH}"/logs/debug.log; fi
			fi
						
		else 
			if [ "${DEBUG_sync_shared_sh}" == "TRUE" ]; then echo "Sync: Sync on RFID scan deactivated" >> "${PROJROOTPATH}"/logs/debug.log; fi
		fi
	}
	
	# Sync full (shortcuts and audiofolders)
	handle_full() {
		if is_server_reachable ; then
		
			if exec_for_mode [ ! -d "$SYNCSHORTCUTSPATH" ] ; then
				exec_for_mode mkdir "$SYNCSHORTCUTSPATH"
				if [ "${DEBUG_sync_shared_sh}" == "TRUE" ]; then echo "Sync: Folder ${SYNCSHORTCUTSPATH} does not exist. created" >> "${PROJROOTPATH}"/logs/debug.log; fi
			else
				if [ "${DEBUG_sync_shared_sh}" == "TRUE" ]; then echo "Sync: Folder ${SYNCSHORTCUTSPATH}" >> "${PROJROOTPATH}"/logs/debug.log; fi
				sync_from_server "${SYNCSHORTCUTSPATH}/" "${LOCAL_SHORTCUTSPATH}/"

			fi
				
			if exec_for_mode [ ! -d "$SYNCAUDIOFOLDERSPATH" ] ; then
				exec_for_mode mkdir "$SYNCAUDIOFOLDERSPATH"
				if [ "${DEBUG_sync_shared_sh}" == "TRUE" ]; then echo "Sync: Folder ${SYNCAUDIOFOLDERSPATH} does not exist. created" >> "${PROJROOTPATH}"/logs/debug.log; fi
			else
				if [ "${DEBUG_sync_shared_sh}" == "TRUE" ]; then echo "Sync: Folder ${SYNCAUDIOFOLDERSPATH}" >> "${PROJROOTPATH}"/logs/debug.log; fi
				sync_from_server "${SYNCAUDIOFOLDERSPATH}/" "${LOCAL_AUDIOFOLDERSPATH}/" "UpdateMPC"
				
			fi
			
		else 
			if [ "${DEBUG_sync_shared_sh}" == "TRUE" ]; then echo "Sync: Server is NOT reachable" >> "${PROJROOTPATH}"/logs/debug.log; fi
		fi
	}
	
	# Change setting for Sync on RFID scan
	handle_changeOnRfidScan() {
		case "$VALUE" in
			on)
				SYNCSHAREDONRFIDSCAN_NEW="TRUE"
				;;
			off)
				SYNCSHAREDONRFIDSCAN_NEW="FALSE"
				;;
			toggle)
				if [ "$SYNCSHAREDONRFIDSCAN" == "TRUE" ]; then 
					SYNCSHAREDONRFIDSCAN_NEW="FALSE"
				else 
					SYNCSHAREDONRFIDSCAN_NEW="TRUE"
				fi
				;;
			*)	
				echo "Unknown VALUE ${VALUE} for COMMAND ${COMMAND}"
				if [ "${DEBUG_sync_shared_sh}" == "TRUE" ]; then echo "Unknown VALUE ${VALUE} for COMMAND ${COMMAND}" >> "${PROJROOTPATH}"/logs/debug.log; fi
				;;
		esac

		if [ ! -z "${SYNCSHAREDONRFIDSCAN_NEW}" ]; then 
			if [ "${DEBUG_sync_shared_sh}" == "TRUE" ]; then echo "Sync: Set SYNCSHAREDONRFIDSCAN to ${SYNCSHAREDONRFIDSCAN_NEW}" >> "${PROJROOTPATH}"/logs/debug.log; fi
			sed -i "s|^SYNCSHAREDONRFIDSCAN=.*|SYNCSHAREDONRFIDSCAN=\"${SYNCSHAREDONRFIDSCAN_NEW}\"|g" "${PROJROOTPATH}"/settings/sync_shared.conf
		fi
	}
	
	# Change access of file or dir
	change_access() {
		local file_or_dir="$1"
		local group="$2"
		local mod="$3"
		
		sudo chgrp -R "$group" "$file_or_dir"
		sudo chmod -R "$mod" "$file_or_dir"
	}
	
	#############################################################
	#############################################################
	
	#############################################################
	
	case "$COMMAND" in
		shortcuts)
			handle_shortcuts
			;;
		audiofolders)
			handle_audiofolders
			;;
		full)
			handle_full
			;;
		changeOnRfidScan)
			handle_changeOnRfidScan
			;;
		*)
			echo "Unknown COMMAND {$COMMAND}"
			if [ "${DEBUG_sync_shared_sh}" == "TRUE" ]; then echo "Unknown COMMAND ${COMMAND} CARDID ${CARDID} FOLDER ${FOLDER} VALUE ${VALUE}" >> "${PROJROOTPATH}"/logs/debug.log; fi
			;;
	esac

fi
if [ "${DEBUG_sync_shared_sh}" == "TRUE" ]; then echo "########### SCRIPT sync_shared.sh ##" >> "${PROJROOTPATH}"/logs/debug.log; fi
