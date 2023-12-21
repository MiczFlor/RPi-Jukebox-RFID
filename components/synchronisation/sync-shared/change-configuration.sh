#!/bin/bash

PATHDATA="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
PROJROOTPATH="${PATHDATA}/../../.."
STATEFILE="${PROJROOTPATH}/settings/sync-shared-enabled"
CONFFILE="${PROJROOTPATH}/settings/sync-shared.conf"
SKIP_INITIAL_CHECK="$1"


#############################################################
# Functions

set_activation() {
    local SETTINGVALUE="$1"

    local SETTINGSTATE="activated"
    if [ "$SETTINGVALUE" != "TRUE" ]; then
        SETTINGSTATE="deactivated"
    fi

    # Let global controls know this feature is enabled
    echo -e "\nLet global controls know this feature is ${SETTINGSTATE}. (sync-shared-enabled -> ${SETTINGVALUE})"

    echo "$SETTINGVALUE" > "$STATEFILE"
    sudo chgrp www-data "$STATEFILE"
    sudo chmod 775 "$STATEFILE"
}

init_settings() {
    # Init config from sample if not present
    if [ ! -f "$CONFFILE" ]; then
        cp "${PATHDATA}/settings/sync-shared.conf.sample" "$CONFFILE"
        # change the read/write so that later this might also be editable through the web app
        sudo chgrp www-data "$CONFFILE"
        sudo chmod 775 "$CONFFILE"
    fi
    . "$CONFFILE"
}

set_setting() {
    local SETTINGNAME="$1"
    local SETTINGVALUE="$2"

    # check if value is set and not equal to the current settings value
    if [ ! -z "$SETTINGVALUE" -a "${!SETTINGNAME}" != "$SETTINGVALUE" ]; then
        sed -i "s|^${SETTINGNAME}=.*|${SETTINGNAME}=\"${SETTINGVALUE}\"|g" "$CONFFILE"
        echo "New value: \"${SETTINGVALUE}\""
    fi
}

read_setting() {
    local SETTINGNAME="$1"
    local TEXT="$2"

    local READ_PROMPT=$'\n'"${TEXT} Leave blank for no change."
    READ_PROMPT="${READ_PROMPT}"$'\n'"Current value = \"${SETTINGNAME}\""$'\n'

    read -rp "$READ_PROMPT" response
}

read_all_settings() {

    read_setting "$SYNCSHAREDMODE" "Choose synchronisation mode to access the server (m[ount]/s[sh])."
    case "$response" in
        [mM][oO][uU][nN][tT]|[mM][nN][tT]|[mM])
            response="MOUNT"
            ;;
        [sS][sS][hH]|[sS])
            response="SSH"
            ;;
        *)
            # no change
            ;;
    esac
    set_setting "SYNCSHAREDMODE" "$response"

    if [ "$response" == "SSH" ]; then
        read_setting "$SYNCSHAREDREMOTESSHUSER" "Please enter SSH user."
        set_setting "SYNCSHAREDREMOTESSHUSER" "$response"
    fi

    read_setting "$SYNCSHAREDREMOTESERVER" "Please enter your servers adresse (IP/Hostname)."
    set_setting "SYNCSHAREDREMOTESERVER" "$response"

    read_setting "$SYNCSHAREDREMOTEPORT" "Please enter your servers port."
    set_setting "SYNCSHAREDREMOTEPORT" "$response"

    read_setting "$SYNCSHAREDREMOTETIMOUT" "Please enter the timeout to try to reach the server (in seconds)."
    set_setting "SYNCSHAREDREMOTETIMOUT" "$response"

    read_setting "$SYNCSHAREDREMOTEPATH" "Please enter the path to the shared files to sync (without trailing slash)."
    # Make sure paths dont have a trailing slash ({VAR%/})
    set_setting "SYNCSHAREDREMOTEPATH" "${response%/}"

    read_setting "$SYNCSHAREDONRFIDSCAN" "Do you want to activate the syncronisation on RFID scan (y[es]/n[o])."
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
