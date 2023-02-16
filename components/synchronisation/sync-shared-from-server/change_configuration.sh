#!/bin/bash

PATHDATA="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
PROJROOTPATH="${PATHDATA}/../../.."
CONFFILE="${PROJROOTPATH}/settings/Sync_Shared_Enabled"
SKIP_INITIAL_CHECK="$1"


#############################################################
# Functions

function set_activation {
	local SETTINGVALUE="$1"
	
	local SETTINGSTATE="activated"
	if [ "$SETTINGVALUE" != "TRUE" ]; then
		SETTINGSTATE="deactivated"
	fi
	
	# Let global controls know this feature is enabled
	echo -e "\nLet global controls know this feature is $SETTINGSTATE. (Sync_Shared_Enabled -> $SETTINGVALUE)"
	
	echo "$SETTINGVALUE" > ${CONFFILE}
	chmod ugo+rw ${CONFFILE}
}

function init_settings {
	# Init config from sample if not present
	if [ ! -f ${PROJROOTPATH}/settings/sync_shared.conf ]; then
		cp ${PATHDATA}/settings/sync_shared.conf.sample ${PROJROOTPATH}/settings/sync_shared.conf
		# change the read/write so that later this might also be editable through the web app
		sudo chown -R pi:www-data ${PROJROOTPATH}/settings/sync_shared.conf
		sudo chmod -R ugo+rw ${PROJROOTPATH}/settings/sync_shared.conf
	fi
	. ${PROJROOTPATH}/settings/sync_shared.conf
}

function set_setting {
	local SETTINGNAME="$1"
	local SETTINGVALUE="$2"

	if [ ! -z "$SETTINGVALUE" -a "${!SETTINGNAME}" != "$SETTINGVALUE" ]; then
		sed -i "s;^$SETTINGNAME=.*;$SETTINGNAME=\"$SETTINGVALUE\";" ${PROJROOTPATH}/settings/sync_shared.conf
		echo "New value: \"$SETTINGVALUE\""
	fi
}

function read_setting {
	local SETTINGNAME="$1"
	local TEXT="$2"
	local SKIP_LEAVE_BLANK="$3"
	
	local READ_PROMPT=$'\n'"$TEXT"
	if [ -z "$SKIP_LEAVE_BLANK" ]; then
		READ_PROMPT="$READ_PROMPT Leave blank for no change."
	fi
	READ_PROMPT="$READ_PROMPT"$'\n'"Current value = \"$SETTINGNAME\""$'\n'

	read -rp "$READ_PROMPT" response
}

function read_all_settings {
	read_setting "$SYNCSHAREDREMOTESERVER" "Please enter your servers adresse (IP/Hostname)."
	set_setting "SYNCSHAREDREMOTESERVER" "$response"

	read_setting "$SYNCSHAREDREMOTEPORT" "Please enter your servers port."
	set_setting "SYNCSHAREDREMOTEPORT" "$response"

	read_setting "$SYNCSHAREDREMOTEPATH" "Please enter your servers folder name or path."
	set_setting "SYNCSHAREDREMOTEPATH" "$response"

	read_setting "$SYNCSHAREDREMOTETIMOUT" "Please enter the timeout to try to reach the server (in seconds)."
	set_setting "SYNCSHAREDREMOTETIMOUT" "$response"

	read_setting "$SYNCSHAREDONRFIDSCAN" "Do you want to activate the syncronisation on RFID scan (y/N)."
	case "$response" in
		[yY][eE][sS]|[yY])
			response="TRUE"
			;;
		[nN][oO]|[nN])
			response="FALSE"
			;;
		*)
			;;
	esac
	set_setting "SYNCSHAREDONRFIDSCAN" "$response"
}

#############################################################

# If intial check is skipped, asume the component shall be activated
if [ -z "$SKIP_INITIAL_CHECK" ]; then
	read -rp "Do you want to activate the sync-shared component? [Y/n] " response
else 
	response="yes"
fi

case "$response" in
	[nN][oO]|[nN])
		set_activation "FALSE"
		;;
	*)
		set_activation "TRUE"
		
		# Ensure start was intended
		read -rp "Do you want to change the configuration? [Y/n] " response
		case "$response" in
			[nN][oO]|[nN])
				exit
				;;
			*)
				;;
		esac
		init_settings
		read_all_settings
		;;
esac

echo -e "\nConfiguration finished"