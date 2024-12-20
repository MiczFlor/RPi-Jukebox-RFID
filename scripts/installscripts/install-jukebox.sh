#!/usr/bin/env bash
#
# see https://github.com/MiczFlor/RPi-Jukebox-RFID for details
#
# NOTE: Running automated install (without interaction):
# Each install creates a file called PhonieboxInstall.conf
# in you $HOME directory
# You can install the Phoniebox using such a config file
# which means you don't need to run the interactive install:
#
# 1. download the install file from github
#    https://github.com/MiczFlor/RPi-Jukebox-RFID/tree/master/scripts/installscripts
# 2. make the file executable: chmod +x
# 3. place the PhonieboxInstall.conf in the folder $HOME
# 4. run the installscript with option -a like this:
#    install-jukebox.sh -a

# The absolute path to the folder which contains this script
PATHDATA="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
GIT_BRANCH=${GIT_BRANCH:-master}
GIT_URL=${GIT_URL:-https://github.com/MiczFlor/RPi-Jukebox-RFID.git}

DATETIME=$(date +"%Y%m%d_%H%M%S")

SCRIPTNAME="$(basename $0)"
JOB="${SCRIPTNAME}"

CURRENT_USER="${SUDO_USER:-$(whoami)}"
HOME_DIR=$(getent passwd "$CURRENT_USER" | cut -d: -f6)


JUKEBOX_HOME_DIR="${HOME_DIR}/RPi-Jukebox-RFID"
LOGDIR="${HOME_DIR}"/phoniebox_logs
JUKEBOX_BACKUP_DIR="${HOME_DIR}/BACKUP"

# Get the Raspberry Pi OS codename (e.g. buster, bullseye, ...)
OS_CODENAME="$( . /etc/os-release; printf '%s\n' "$VERSION_CODENAME"; )"

WIFI_INTERFACE="wlan0"

INTERACTIVE=true

usage() {
    printf "Usage: ${SCRIPTNAME} [-a] [-h]\n"
    printf " -a\tautomatic/non-interactive mode\n"
    printf " -h\thelp\n"
    exit 0
}

while getopts ":ah" opt;
do
  case ${opt} in
    a ) INTERACTIVE=false
      ;;
    h ) usage
      ;;
    \? ) usage
      ;;
  esac
done


# Setup logger functions
# Input from http://www.ludovicocaldara.net/dba/bash-tips-5-output-logfile/
log_open() {
    [[ -d "${LOGDIR}" ]] || mkdir -p "${LOGDIR}"
    PIPE="${LOGDIR}"/"${JOB}"_"${DATETIME}".pipe
    mkfifo -m 700 "${PIPE}"
    LOGFILE="${LOGDIR}"/"${JOB}"_"${DATETIME}".log
    exec 3>&1
    tee "${LOGFILE}" <"${PIPE}" >&3 &
    TEEPID=$!
    exec 1>"${PIPE}" 2>&1
    PIPE_OPENED=1
}

log_close() {
    if [ "${PIPE_OPENED}" ]; then
        exec 1<&3
        sleep 0.2
        ps --pid "${TEEPID}" >/dev/null
        if [ $? -eq 0 ] ; then
            # a wait ${TEEPID} whould be better but some
            # commands leave file descriptors open
            sleep 1
            kill  "${TEEPID}"
        fi
        rm "${PIPE}"
        unset PIPE_OPENED
    fi
}

# local function as it is needed before the repo is checked out!
_escape_for_shell() {
	local escaped="${1//\"/\\\"}"
	escaped="${escaped//\`/\\\`}"
    escaped="${escaped//\$/\\\$}"
	echo "$escaped"
}

checkPrerequisite() {
    #currently the user 'pi' is mandatory
    #https://github.com/MiczFlor/RPi-Jukebox-RFID/issues/1785
    if [ "${CURRENT_USER}" != "pi" ]; then
        echo
        echo "ERROR: User must be 'pi'!"
        echo "       Other usernames are currently not supported."
        echo "       Please check the wiki for further information"
        exit 2
    fi

    if [ "${HOME_DIR}" != "/home/pi" ]; then
        echo
        echo "ERROR: HomeDir must be '/home/pi'!"
        echo "       Other usernames are currently not supported."
        echo "       Please check the wiki for further information"
        exit 2
    fi

    if [ ! -d "${HOME_DIR}" ]; then
        echo
        echo "Warning: HomeDir ${HOME_DIR} does not exist."
        echo "         Please create it and start again."
        exit 2
    fi
}

welcome() {
    clear
    echo "#####################################################
#    ___  __ ______  _  __________ ____   __  _  _  #
#   / _ \/ // / __ \/ |/ /  _/ __/(  _ \ /  \( \/ ) #
#  / ___/ _  / /_/ /    // // _/   ) _ ((  O ))  (  #
# /_/  /_//_/\____/_/|_/___/____/ (____/ \__/(_/\_) #
#                                                   #
#####################################################

You are turning your Raspberry Pi into a Phoniebox. Good choice.
This INTERACTIVE INSTALL script requires you to be online and
will guide you through the configuration.

If you want to run the AUTOMATED INSTALL (non-interactive) from
an existing configuration file, do the following:
1. exit this install script (press n)
2. place your PhonieboxInstall.conf in the folder ${HOME_DIR}
3. run the installscript with option -a. For example like this:
   ${HOME_DIR}/install-jukebox.sh -a
   "
    read -rp "Continue interactive installation? [Y/n] " response
    case "$response" in
        [nN][oO]|[nN])
            exit
            ;;
        *)
            echo "Installation continues..."
            ;;
    esac
}

reset_install_config_file() {
    #####################################################
    # CONFIG FILE
    # This file will contain all the data given in the
    # following dialogue
    # At a later stage, the install should also be done
    # from such a config file with no user input.

    # Remove existing config file
    #rm "${HOME_DIR}/PhonieboxInstall.conf"
    # Create empty config file
    #touch "${HOME_DIR}/PhonieboxInstall.conf"
    #echo "# Phoniebox config" > "${HOME_DIR}/PhonieboxInstall.conf"
    echo "# Phoniebox config"
}

config_wifi() {
    #####################################################
    # Ask if wifi config

    clear

    echo "#####################################################
#
# CONFIGURE WIFI
#
# Requires SSID, WiFi password and the static IP you want
# to assign to your Phoniebox.
# (Note: can be done manually later, if you are unsure.)
"
read -rp "Do you want to configure your WiFi? [y/N] " response
echo ""
case "$response" in
    [yY][eE][sS]|[yY])
        WIFIconfig=YES
        #Ask for SSID
        read -rp "* Type SSID name: " WIFIssid
        #Ask for wifi country code
        read -rp "* WiFi Country Code (e.g. DE, GB, CZ or US): " WIFIcountryCode
        #Ask for password
        read -rp "* Type password: " WIFIpass
        #Ask for IP
        read -rp "* Static IP (e.g. 192.168.1.199): " WIFIip
        #Ask for Router IP
        read -rp "* Router IP (e.g. 192.168.1.1): " WIFIipRouter
        echo ""
        echo "Your WiFi config:"
        echo "SSID              : $WIFIssid"
        echo "WiFi Country Code : $WIFIcountryCode"
        echo "Password          : $WIFIpass"
        echo "Static IP         : $WIFIip"
        echo "Router IP         : $WIFIipRouter"
        read -rp "Are these values correct? [Y/n] " response
        echo ""
        case "$response" in
            [nN][oO]|[nN])
                echo "The values are incorrect."
                read -rp "Hit ENTER to exit and start over." INPUT; exit
                ;;
            *)
                # append variables to config file
                {
                    echo "WIFIconfig=\"$(_escape_for_shell "$WIFIconfig")\"";
                    echo "WIFIcountryCode=\"$(_escape_for_shell "$WIFIcountryCode")\"";
                    echo "WIFIssid=\"$(_escape_for_shell "$WIFIssid")\"";
                    echo "WIFIpass=\"$(_escape_for_shell "$WIFIpass")\"";
                    echo "WIFIip=\"$(_escape_for_shell "$WIFIip")\"";
                    echo "WIFIipRouter=\"$(_escape_for_shell "$WIFIipRouter")\"";
                } >> "${HOME_DIR}/PhonieboxInstall.conf"
                ;;
        esac
        ;;
    *)
        WIFIconfig=NO
        echo "You want to configure WiFi later."
        # append variables to config file
        echo "WIFIconfig=\"$(_escape_for_shell "$WIFIconfig")\"" >> "${HOME_DIR}/PhonieboxInstall.conf"
        # make a fallback for WiFi Country Code, because we need that even without WiFi config
        echo "WIFIcountryCode=\"$(_escape_for_shell "DE")\"" >> "${HOME_DIR}/PhonieboxInstall.conf"
        ;;
esac
read -rp "Hit ENTER to proceed to the next step." INPUT
}

config_autohotspot() {
    #####################################################
    # Ask if an autohotspot should be created if no known network is found.

    clear

    echo "#####################################################
#
# CONFIGURE AUTOHOTSPOT
#
# Automatically sets up a wifi hotspot if no known network is found.
# This enables you to directly connect to your phoniebox
# and change configuration (e.g. while you travel).
# (Note: can be done manually later, if you are unsure.)
"
read -rp "Do you want to configure autohotspot? [y/N] " response
echo ""
case "$response" in
    [yY][eE][sS]|[yY])
        AUTOHOTSPOTconfig=YES
        AUTOHOTSPOTssid="phoniebox"
        AUTOHOTSPOTcountryCode="DE"
        AUTOHOTSPOTpass="PlayItLoud"
        AUTOHOTSPOTip="10.0.0.5"
        echo ""
        echo "The autohotspot configuration uses this default values:"
        echo "SSID              : $AUTOHOTSPOTssid"
        echo "WiFi Country Code : $AUTOHOTSPOTcountryCode"
        echo "Password          : $AUTOHOTSPOTpass"
        echo "Static IP         : $AUTOHOTSPOTip"
        read -rp "Do you want to use this default values? [Y/n] " response
        echo ""
        case "$response" in
            [nN][oO]|[nN])
                #Ask for SSID
                read -rp "* Type SSID name: " AUTOHOTSPOTssid
                #Ask for wifi country code
                read -rp "* Type WiFi Country Code (e.g. DE, GB, CZ or US): " AUTOHOTSPOTcountryCode
                #Ask for password
                read -rp "* Type password (8 characters at least. max 63 characters): " AUTOHOTSPOTpass
                #Ask for IP
                read -rp "* Type Static IP (e.g. 10.0.0.5, 192.168.1.199): " AUTOHOTSPOTip
                echo ""
                echo "Your Autohotspot config:"
                echo "SSID              : $AUTOHOTSPOTssid"
                echo "WiFi Country Code : $AUTOHOTSPOTcountryCode"
                echo "Password          : $AUTOHOTSPOTpass"
                echo "Static IP         : $AUTOHOTSPOTip"
                read -rp "Are these values correct? [Y/n] " response
                echo ""
                case "$response" in
                    [nN][oO]|[nN])
                        echo "The values are incorrect."
                        read -rp "Hit ENTER to exit and start over." INPUT; exit
                        ;;
                    *)
                        # step out and continue
                        ;;
                esac
                ;;
            *)
                # step out and continue
                ;;
        esac
        # append variables to config file
        {
            echo "AUTOHOTSPOTconfig=\"$(_escape_for_shell "$AUTOHOTSPOTconfig")\"";
            echo "AUTOHOTSPOTssid=\"$(_escape_for_shell "$AUTOHOTSPOTssid")\"";
            echo "AUTOHOTSPOTcountryCode=\"$(_escape_for_shell "$AUTOHOTSPOTcountryCode")\"";
            echo "AUTOHOTSPOTpass=\"$(_escape_for_shell "$AUTOHOTSPOTpass")\"";
            echo "AUTOHOTSPOTip=\"$(_escape_for_shell "$AUTOHOTSPOTip")\"";
        } >> "${HOME_DIR}/PhonieboxInstall.conf"
        ;;
    *)
        AUTOHOTSPOTconfig=NO
        echo "You don't want to configure Autohotspot."
        # append variables to config file
        echo "AUTOHOTSPOTconfig=\"$(_escape_for_shell "$AUTOHOTSPOTconfig")\"" >> "${HOME_DIR}/PhonieboxInstall.conf"
        ;;

esac
read -rp "Hit ENTER to proceed to the next step." INPUT
}

check_existing() {
    local jukebox_dir="$1"
    local backup_dir="$2"
    local local_home_dir="$3"

    #####################################################
    # Check for existing Phoniebox
    #
    # In case there is no existing install,
    # set the var now for later use:
    EXISTINGuse=NO

    # The install will be in the home dir of user pi
    # Move to home directory now to check
    cd "${local_home_dir}"
    if [ -d "${jukebox_dir}" ]; then
        # Houston, we found something!
        clear
        echo "#####################################################
#
# . . . * alert * alert * alert * alert * . . .
#
# WARNING: an existing Phoniebox installation was found.
#
"
        # check if we find the version number
        if [ -f "${jukebox_dir}"/settings/version ]; then
            #echo "The version of your installation is: $(cat ${jukebox_dir}/settings/version)"

            # get the current short commit hash of the repo
            CURRENT_REMOTE_COMMIT="$(git ls-remote ${GIT_URL} ${GIT_BRANCH} | cut -c1-7)"
        fi
        echo "IMPORTANT: you can use the existing content and configuration"
        echo "files for your new install."
        echo "Whatever you chose to keep will be moved to the new install."
        echo "Everything else will remain in a folder called 'BACKUP'.
        "

        ###
        # See if we find the PhonieboxInstall.conf file
        # We need to do this first, because if we re-use the .conf file, we need to append
        # the variables regarding the found content to the also found configuration file.
        # That way, reading the configuration file for the (potentially) non-interactive
        # install procedure will:
        # a) overwrite whatever variables regarding re-cycling existing content which might
        #    be stored in the config file
        # b) if there are no variables for dealing with re-cycled context, we will append
        #    them - to have them for this install
        if [ -f "${jukebox_dir}"/settings/PhonieboxInstall.conf ]; then
            # ask for re-using the found configuration file
            echo "The configuration of your last Phoniebox install was found."
            read -rp "Use existing configuration for this installation? [Y/n] " response
            case "$response" in
                [nN][oO]|[nN])
                    EXISTINGusePhonieboxInstall=NO
                    ;;
                *)
                    EXISTINGusePhonieboxInstall=YES
                    # Copy PhonieboxInstall.conf configuration file to settings folder
                    sudo cp "${jukebox_dir}"/settings/PhonieboxInstall.conf "${local_home_dir}"/PhonieboxInstall.conf
                    sudo chown pi:www-data "${local_home_dir}"/PhonieboxInstall.conf
                    sudo chmod 775 "${local_home_dir}"/PhonieboxInstall.conf
                    echo "The existing configuration will be used."
                    echo "Just a few more questions to answer."
                    read -rp "Hit ENTER to proceed to the next step." INPUT
                    clear
                    ;;
            esac
        fi

        # Delete or use existing installation?
        read -rp "Re-use config, audio and RFID codes for the new install? [Y/n] " response
        case "$response" in
            [nN][oO]|[nN])
                EXISTINGuse=NO
                echo "Phoniebox will be a fresh install. The existing version will be dropped."
                sudo rm -rf "${jukebox_dir}"
                read -rp "Hit ENTER to proceed to the next step." INPUT
                ;;
            *)
                EXISTINGuse=YES
                # CREATE BACKUP
                # delete existing BACKUP dir if exists
                if [ -d "${backup_dir}" ]; then
                    sudo rm -r "${backup_dir}"
                fi
                # move install to BACKUP dir
                mv "${jukebox_dir}" "${backup_dir}"
                # delete .git dir
                if [ -d "${backup_dir}"/.git ]; then
                    sudo rm -r "${backup_dir}"/.git
                fi
                # delete placeholder files so moving the folder content back later will not create git pull conflicts
                rm "${backup_dir}"/shared/audiofolders/placeholder
                rm "${backup_dir}"/shared/shortcuts/placeholder

                # ask for things to use
                echo "Ok. You want to use stuff from the existing installation."
                echo "What would you want to keep? Answer now."
                read -rp "RFID config for system control (e.g. 'volume up' etc.)? [Y/n] " response
                case "$response" in
                    [nN][oO]|[nN])
                        EXISTINGuseRfidConf=NO
                        ;;
                    *)
                        EXISTINGuseRfidConf=YES
                        ;;
                esac
                # append variables to config file
                echo "EXISTINGuseRfidConf=\"$(_escape_for_shell "$EXISTINGuseRfidConf")\"" >> "${local_home_dir}/PhonieboxInstall.conf"

                read -rp "RFID shortcuts to play audio folders? [Y/n] " response
                case "$response" in
                    [nN][oO]|[nN])
                        EXISTINGuseRfidLinks=NO
                        ;;
                    *)
                        EXISTINGuseRfidLinks=YES
                        ;;
                esac
                # append variables to config file
                echo "EXISTINGuseRfidLinks=\"$(_escape_for_shell "$EXISTINGuseRfidLinks")\"" >> "${local_home_dir}/PhonieboxInstall.conf"

                read -rp "Audio folders: use existing? [Y/n] " response
                case "$response" in
                    [nN][oO]|[nN])
                        EXISTINGuseAudio=NO
                        ;;
                    *)
                        EXISTINGuseAudio=YES
                        ;;
                esac
                # append variables to config file
                echo "EXISTINGuseAudio=\"$(_escape_for_shell "$EXISTINGuseAudio")\"" >> "${local_home_dir}/PhonieboxInstall.conf"

                read -rp "Sound effects: use existing startup / shutdown sounds? [Y/n] " response
                case "$response" in
                    [nN][oO]|[nN])
                        EXISTINGuseSounds=NO
                        ;;
                    *)
                        EXISTINGuseSounds=YES
                        ;;
                esac
                # append variables to config file
                echo "EXISTINGuseSounds=\"$(_escape_for_shell "$EXISTINGuseSounds")\"" >> "${local_home_dir}/PhonieboxInstall.conf"

                if [ "$(printf '%s\n' "2.1" "$(cat ${local_home_dir}/BACKUP/settings/version-number)" | sort -V | head -n1)" = "2.1" ]; then
                    read -rp "GPIO: use existing file? [Y/n] " response
                        case "$response" in
                            [nN][oO]|[nN])
                                EXISTINGuseGpio=NO
                                ;;
                            *)
                                EXISTINGuseGpio=YES
                                ;;
                        esac
                else
                    echo ""
                    echo "Warning!
The configuration of GPIO-Devices has changed in the new version
and needs to be reconfigured. For further info check out the wiki:
https://github.com/MiczFlor/RPi-Jukebox-RFID/wiki/Using-GPIO-hardware-buttons"
                    read -rp "Hit ENTER to proceed to the next step." INPUT
                    config_gpio
                fi
                # append variables to config file
                echo "EXISTINGuseGpio=\"$(_escape_for_shell "$EXISTINGuseGpio")\"" >> "${local_home_dir}/PhonieboxInstall.conf"

                read -rp "Button USB Encoder: use existing device and button mapping? [Y/n] " response
                case "$response" in
                    [nN][oO]|[nN])
                        EXISTINGuseButtonUSBEncoder=NO
                        ;;
                    *)
                        EXISTINGuseButtonUSBEncoder=YES
                        ;;
                esac
                # append variables to config file
                echo "EXISTINGuseButtonUSBEncoder=\"$(_escape_for_shell "$EXISTINGuseButtonUSBEncoder")\"" >> "${local_home_dir}/PhonieboxInstall.conf"

                echo "Thanks. Got it."
                echo "The existing install can be found in the BACKUP directory."
                read -rp "Hit ENTER to proceed to the next step." INPUT
                ;;
        esac
    fi
    # append variables to config file
    echo "EXISTINGuse=\"$(_escape_for_shell "$EXISTINGuse")\"" >> "${local_home_dir}/PhonieboxInstall.conf"

    # Check if we found a Phoniebox install configuration earlier and ask if to run this now
    if [ "${EXISTINGusePhonieboxInstall}" == "YES" ]; then
        clear
        echo "Using the existing configuration, you can run a non-interactive install."
        echo "This will re-cycle found content (specified just now) as well as the"
        echo "system information from last time (wifi, audio interface, spotify, etc.)."
        read -rp "Do you want to run a non-interactive installation? [Y/n] " response
        case "$response" in
            [nN][oO]|[nN])
                ;;
            *)
                cd "${local_home_dir}"
                clear
                ./install-jukebox.sh -a
                exit
                ;;
        esac
    fi
}

config_audio_interface() {
    #####################################################
    # Audio iFace

    clear

    local amixer_scontrols=$(sudo amixer scontrols)
    local audio_interfaces=$(echo "${amixer_scontrols}" | sed "s|.*'\(.*\)'.*|\1|g")
    local first_audio_interface=$(echo "${audio_interfaces}" | head -1)
    local default_audio_interface="${first_audio_interface:-PCM}"

    echo "#####################################################
#
# CONFIGURE AUDIO INTERFACE (iFace)
#
# The default RPi audio interface is '${default_audio_interface}'.
# But this does not work for every setup.
# Here a list of available iFace names:

${audio_interfaces}
"

    echo " "
    read -rp "Use '${default_audio_interface}' as iFace? [Y/n] " response
    case "$response" in
        [nN][oO]|[nN])
            read -rp "Type the iFace name you want to use:" AUDIOiFace
            ;;
        *)
            AUDIOiFace="${default_audio_interface}"
            ;;
    esac
    # append variables to config file
    echo "AUDIOiFace=\"$(_escape_for_shell "$AUDIOiFace")\"" >> "${HOME_DIR}/PhonieboxInstall.conf"
    echo "Your iFace is called '$AUDIOiFace'"
    read -rp "Hit ENTER to proceed to the next step." INPUT
}

config_spotify() {
    #####################################################
    # Configure spotify

    clear

    echo "#####################################################
#
# OPTIONAL: INCLUDE SPOTIFY
#
# Note: if this is your first time installing a phoniebox
# it might be best to do a test install without Spotify
# to make sure all your hardware works.
#
# If you want to include Spotify, MUST have your
# credentials ready:
#
# * username
# * password
# * client_id
# * client_secret

"
    read -rp "Do you want to enable Spotify? [y/N] " response
    case "$response" in
        [yY][eE][sS]|[yY])
            SPOTinstall=YES
            clear
            echo "#####################################################
#
# CREDENTIALS for Spotify
#
# Requires Spotify username, password, client_id and client_secret
# to get connection to Spotify.
#
# (Note: You need a device with browser to generate ID and SECRET)
#
# Please go to this website:
# https://www.mopidy.com/authenticate/
# and follow the instructions.
#
# Your credential will appear on the site below the login button.
# Please note your client_id and client_secret!
#
"
            read -rp "Type your client_id: " SPOTIclientid
            read -rp "Type your client_secret: " SPOTIclientsecret
            ;;
        *)
            SPOTinstall=NO
            echo "You don't want spotify support."
            ;;
    esac
    # append variables to config file
    {
        echo "SPOTinstall=\"$(_escape_for_shell "$SPOTinstall")\"";
        echo "SPOTIclientid=\"$(_escape_for_shell "$SPOTIclientid")\"";
        echo "SPOTIclientsecret=\"$(_escape_for_shell "$SPOTIclientsecret")\""
    } >> "${HOME_DIR}/PhonieboxInstall.conf"
    read -rp "Hit ENTER to proceed to the next step." INPUT
}

config_audio_folder() {
    local jukebox_dir="$1"

    #####################################################
    # Folder path for audio files
    # default: $HOME/RPi-Jukebox-RFID/shared/audiofolders

    clear

    echo "#####################################################
#
# FOLDER CONTAINING AUDIO FILES
#
# The default location for folders containing audio files:
# ${jukebox_dir}/shared/audiofolders
#
# If unsure, keep it like this. If your files are somewhere
# else, you can specify the folder in the next step.
# IMPORTANT: the folder will not be created, only the path
# will be remembered. If you use a custom folder, you must
# create it.
"

    read -rp "Do you want to use the default location? [Y/n] " response
    case "$response" in
        [nN][oO]|[nN])
            echo "Please type the absolute path here (no trailing slash)."
            echo "Default would be for example: ${jukebox_dir}/shared/audiofolders"
            read -r DIRaudioFolders
            ;;
        *)
            DIRaudioFolders="${jukebox_dir}/shared/audiofolders"
            ;;
    esac
    # append variables to config file
    echo "DIRaudioFolders=\"$(_escape_for_shell "$DIRaudioFolders")\"" >> "${HOME_DIR}/PhonieboxInstall.conf"
    echo "Your audio folders live in this dir:"
    echo "${DIRaudioFolders}"
    read -rp "Hit ENTER to proceed to the next step." INPUT
}

check_variable() {
  local variable=${1}
  # check if variable exist and if it's empty
  test -z "${!variable+x}" && echo "ERROR: \$${variable} is missing!" && fail=true && return
  test "${!variable}" == "" && echo "ERROR: \$${variable} is empty!" && fail=true
}

config_gpio() {
    #####################################################
    # Configure GPIO

    clear

    echo "#####################################################
#
# ACTIVATE GPIO-Control
#
# Activation of the GPIO-Control-Service, which mangages Buttons
# or a Rotary Encoder for Volume and/or Track control.
# To configure the controls please consult the wiki:
# https://github.com/MiczFlor/RPi-Jukebox-RFID/wiki/Using-GPIO-hardware-buttons
# It's also possible to activate the service later (see wiki).
"
    read -rp "Do you want to activate the GPIO-Control-Service? [Y/n] " response
    case "$response" in
        [nN][oO]|[nN])
            GPIOconfig=NO
            echo "You don't want to activate GPIO-Controls now."
            ;;
        *)
            GPIOconfig=YES
            echo "GPIO-Control-Service will be activated and set to default values."
            ;;
    esac
    # append variables to config file
    echo "GPIOconfig=\"$(_escape_for_shell "$GPIOconfig")\"" >> "${HOME_DIR}/PhonieboxInstall.conf"
    echo ""
    read -rp "Hit ENTER to proceed to the next step." INPUT
}

check_config_file() {
    local install_conf="${HOME_DIR}/PhonieboxInstall.conf"
    echo "Checking PhonieboxInstall.conf..."
    # check that PhonieboxInstall.conf exists and is not empty

    # check if config file exists
    if [[ -f "${install_conf}" ]]; then
        # Source config file
        source "${install_conf}"
        cat "${install_conf}"
        echo ""
    else
        echo "ERROR: ${install_conf} does not exist!"
        exit 1
    fi

    fail=false
    if [[ -z "${WIFIconfig+x}" ]]; then
        echo "ERROR: \$WIFIconfig is missing or not set!" && fail=true
    else
        if [[ "$WIFIconfig" == "YES" ]]; then
            check_variable "WIFIcountryCode"
            check_variable "WIFIssid"
            check_variable "WIFIpass"
            check_variable "WIFIip"
            check_variable "WIFIipRouter"
        fi
    fi

    check_variable "EXISTINGuse"
    check_variable "AUDIOiFace"

    if [[ -z "${SPOTinstall+x}" ]]; then
        echo "ERROR: \$SPOTinstall is missing or not set!" && fail=true
    else
        if [ "$SPOTinstall" == "YES" ]; then
            check_variable "SPOTIclientid"
            check_variable "SPOTIclientsecret"
        fi
    fi
    check_variable "DIRaudioFolders"
    check_variable "GPIOconfig"

    # Feature optional. if config not present, defaults to NO
    if [[ -z "${AUTOHOTSPOTconfig}" ]]; then
        echo "INFO: \$AUTOHOTSPOTconfig is missing or not set"
    else
        if [[ "$AUTOHOTSPOTconfig" == "YES" ]]; then
            check_variable "AUTOHOTSPOTssid"
            check_variable "AUTOHOTSPOTcountryCode"
            check_variable "AUTOHOTSPOTpass"
            check_variable "AUTOHOTSPOTip"
        fi
    fi

    if [ "${fail}" == "true" ]; then
      exit 1
    fi

    echo ""
}

samba_config() {
    local smb_conf="/etc/samba/smb.conf"
    echo "Configuring Samba..."
    # Samba configuration settings
    # -rw-r--r-- 1 root root 9416 Apr 30 09:02 /etc/samba/smb.conf
    sudo cp "${jukebox_dir}"/misc/sampleconfigs/smb.conf-default.sample ${smb_conf}
    sudo chown root:root "${smb_conf}"
    sudo chmod 644 "${smb_conf}"
    # for $DIRaudioFolders using | as alternate regex delimiter because of the folder path slash
    sudo sed -i 's|%DIRaudioFolders%|'"$(escape_for_sed "$DIRaudioFolders")"'|' "${smb_conf}"
    # Samba: create user 'pi' with password 'raspberry'
    # ToDo: use current user with a default password
    (echo "raspberry"; echo "raspberry") | sudo smbpasswd -s -a pi
}

web_server_config() {
    local lighthttpd_conf="/etc/lighttpd/lighttpd.conf"
    local fastcgi_php_conf="/etc/lighttpd/conf-available/15-fastcgi-php.conf"
    local php_ini="/etc/php/$(ls -1 /etc/php)/cgi/php.ini"

    echo "Configuring web server..."
    # make sure lighttp can access the home directory of the user
    sudo chmod o+x ${HOME_DIR}
    # Web server configuration settings
    # -rw-r--r-- 1 root root 1040 Apr 30 09:19 /etc/lighttpd/lighttpd.conf
    sudo cp "${jukebox_dir}"/misc/sampleconfigs/lighttpd.conf-default.sample "${lighthttpd_conf}"
    sudo chown root:root "${lighthttpd_conf}"
    sudo chmod 644 "${lighthttpd_conf}"

    # Web server PHP7 fastcgi conf
    # -rw-r--r-- 1 root root 398 Apr 30 09:35 /etc/lighttpd/conf-available/15-fastcgi-php.conf
    sudo cp "${jukebox_dir}"/misc/sampleconfigs/15-fastcgi-php.conf-default.sample ${fastcgi_php_conf}
    sudo chown root:root "${fastcgi_php_conf}"
    sudo chmod 644 "${fastcgi_php_conf}"

    # settings for php.ini to support upload
    # -rw-r--r-- 1 root root 70999 Jun 14 13:50 /etc/php/7.3/cgi/php.ini
    sudo cp "${jukebox_dir}"/misc/sampleconfigs/php.ini-default.sample ${php_ini}
    sudo chown root:root "${php_ini}"
    sudo chmod 644 "${php_ini}"

    # SUDO users (adding web server here)
    local sudoers_wwwdata="/etc/sudoers.d/www-data"
    echo "www-data ALL=(ALL) NOPASSWD: ALL" | sudo tee "${sudoers_wwwdata}" > /dev/null
    sudo chown root:root "${sudoers_wwwdata}"
    sudo chmod 440 "${sudoers_wwwdata}"
}

install_main() {
    local jukebox_dir="$1"
    local apt_get="sudo apt-get -qq --yes"
    local allow_downgrades="--allow-downgrades --allow-remove-essential --allow-change-held-packages"
    local pip_install="sudo python3 -m pip install --upgrade --force-reinstall -q"

    clear

    echo "#####################################################
#
# START INSTALLATION
#
# Good news: you completed the input.
# Let the install begin.
#
# Get yourself a cup of something. The install takes
# between 15 minutes to half an hour, depending on
# your Raspberry Pi and Internet connectivity.
#
# You will be prompted later to complete the installation.
"

    if [[ ${INTERACTIVE} == "true" ]]; then
        read -rp "Do you want to start the installation? [Y/n] " response
        case "$response" in
            [nN][oO]|[nN])
                echo "Exiting the installation."
                echo "Your configuration data was saved in this file:"
                echo "${HOME_DIR}/PhonieboxInstall.conf"
                echo
                exit
                ;;
        esac
    fi

    # Start logging here
    log_open

    echo "################################################"
    echo "Interactive mode: ${INTERACTIVE}"
    echo "GIT_BRANCH ${GIT_BRANCH}"
    echo "GIT_URL ${GIT_URL}"
    echo "Current User: ${CURRENT_USER}"
    echo "User home dir: ${HOME_DIR}"
    echo "Used Raspberry Pi OS: ${OS_CODENAME}"

    # Add conffile into logfile for better debugging
    echo "################################################"
    grep -v -e "SPOTI" -e "WIFIpass" "${HOME_DIR}/PhonieboxInstall.conf"
    echo "################################################"

    #####################################################
    # INSTALLATION

    # Read install config as written so far
    . "${HOME_DIR}/PhonieboxInstall.conf"

    # power management of wifi: switch off to avoid disconnecting
    sudo iwconfig "$WIFI_INTERFACE" power off

    # in the docker test env fiddling with resolv.conf causes issues, see https://stackoverflow.com/a/60576223
    if [ "$DOCKER_RUNNING" != "true" ]; then
        # create backup of /etc/resolv.conf
        sudo cp /etc/resolv.conf /etc/resolv.conf.orig
    fi

    # Generate locales
    sudo locale-gen "${LANG}"

    # Install required packages
    sudo mkdir -p /etc/apt/keyrings

    ${apt_get} update
    ${apt_get} upgrade

    # Get github code. git must be installed before, even if defined in packages.txt!
    ${apt_get} install git
    cd "${HOME_DIR}"
    git clone ${GIT_URL} --branch "${GIT_BRANCH}"

    source "${jukebox_dir}"/scripts/helperscripts/inc.helper.sh
    source "${jukebox_dir}"/scripts/helperscripts/inc.networkHelper.sh


    # some packages are only available on raspberry pi's but not on test docker containers running on x86_64 machines
    if [[ $(uname -m) =~ ^armv.+$ ]]; then
        call_with_args_from_file "${jukebox_dir}"/packages-raspberrypi.txt ${apt_get} ${allow_downgrades} install
    fi

    call_with_args_from_file "${jukebox_dir}"/packages.txt ${apt_get} ${allow_downgrades} install

    # in the docker test env fiddling with resolv.conf causes issues, see https://stackoverflow.com/a/60576223
    if [ "$DOCKER_RUNNING" != "true" ]; then
        # restore backup of /etc/resolv.conf in case installation of resolvconf cleared it
        sudo cp /etc/resolv.conf.orig /etc/resolv.conf
    fi

    # use python3 as default
    sudo update-alternatives --install /usr/bin/python python /usr/bin/python3 1
    # make compatible for Bookworm, which implements PEP 668
    sudo python3 -m pip config set global.break-system-packages true

    # VERSION of installation

    # Get version number
    VERSION_NO=`cat ${jukebox_dir}/settings/version-number`

    # add used git branch and commit hash to version file
    USED_BRANCH="$(git --git-dir=${jukebox_dir}/.git rev-parse --abbrev-ref HEAD)"

    # add git commit hash to version file
    COMMIT_NO="$(git --git-dir=${jukebox_dir}/.git describe --always)"

    echo "${VERSION_NO} - ${COMMIT_NO} - ${USED_BRANCH}" > ${jukebox_dir}/settings/version
    chmod 777 ${jukebox_dir}/settings/version

    # Install required spotify packages
    if [ "${SPOTinstall}" == "YES" ]; then
        echo "Installing dependencies for Spotify support..."
        # keep major verson 3 of mopidy
        echo -e "Package: mopidy\nPin: version 3.*\nPin-Priority: 1001" | sudo tee /etc/apt/preferences.d/mopidy

        sudo wget -q -O /etc/apt/keyrings/mopidy-archive-keyring.gpg https://apt.mopidy.com/mopidy.gpg
        sudo wget -q -O /etc/apt/sources.list.d/mopidy.list https://apt.mopidy.com/${OS_CODENAME}.list

        ${apt_get} update
        ${apt_get} upgrade
        call_with_args_from_file "${jukebox_dir}"/packages-spotify.txt ${apt_get} ${allow_downgrades} install

        # not yet available on apt.mopidy.com, so install manually
        local arch=$(dpkg --print-architecture)
        local gst_plugin_spotify_name="gst-plugin-spotify_0.14.0.alpha.1-1_${arch}.deb"
        wget -q https://github.com/kingosticks/gst-plugins-rs-build/releases/download/gst-plugin-spotify_0.14.0-alpha.1-1/${gst_plugin_spotify_name}
        ${apt_get} install ./${gst_plugin_spotify_name}
        sudo rm -f ${gst_plugin_spotify_name}

        # Install necessary Python packages
        ${pip_install} -r "${jukebox_dir}"/requirements-spotify.txt

        local sudoers_mopidy="/etc/sudoers.d/mopidy"
        # Include 'python' in the command to make testing later on easier. If this command fails it will not be included in the file.
        local python_version=$(python -c 'import sys; print("python{}.{}".format(sys.version_info.major, sys.version_info.minor))')
        echo "mopidy ALL=NOPASSWD: /usr/local/lib/${python_version}/dist-packages/mopidy_iris/system.sh" | sudo tee "${sudoers_mopidy}" > /dev/null
        sudo chown root:root "${sudoers_mopidy}"
        sudo chmod 440 "${sudoers_mopidy}"
    fi

    # Install more required packages
    echo "Installing additional Python packages..."
    ${pip_install} -r "${jukebox_dir}"/requirements.txt

    samba_config

    web_server_config

    # copy shell script for player
    cp "${jukebox_dir}"/settings/rfid_trigger_play.conf.sample "${jukebox_dir}"/settings/rfid_trigger_play.conf

    # creating files containing editable values for configuration
    echo "$AUDIOiFace" > "${jukebox_dir}"/settings/Audio_iFace_Name
    echo "$DIRaudioFolders" > "${jukebox_dir}"/settings/Audio_Folders_Path
    echo "3" > "${jukebox_dir}"/settings/Audio_Volume_Change_Step
    echo "100" > "${jukebox_dir}"/settings/Max_Volume_Limit
    echo "0" > "${jukebox_dir}"/settings/Idle_Time_Before_Shutdown
    echo "RESTART" > "${jukebox_dir}"/settings/Second_Swipe
    echo "${jukebox_dir}/playlists" > "${jukebox_dir}"/settings/Playlists_Folders_Path
    echo "ON" > "${jukebox_dir}"/settings/ShowCover

    # sample file for debugging with all options set to FALSE
    sudo cp "${jukebox_dir}"/settings/debugLogging.conf.sample "${jukebox_dir}"/settings/debugLogging.conf
    sudo chmod 777 "${jukebox_dir}"/settings/debugLogging.conf

    # The new way of making the bash daemon is using the helperscripts
    # creating the shortcuts and script from a CSV file.
    # see scripts/helperscripts/AssignIDs4Shortcuts.php

    # create config file for web app from sample
    sudo cp "${jukebox_dir}"/htdocs/config.php.sample "${jukebox_dir}"/htdocs/config.php

    # Starting web server and php7
    sudo lighttpd-enable-mod fastcgi
    sudo lighttpd-enable-mod fastcgi-php
    sudo service lighttpd force-reload

    # make sure bash scripts have the right settings
    sudo chown pi:www-data "${jukebox_dir}"/scripts/*.sh
    sudo chmod +x "${jukebox_dir}"/scripts/*.sh
    sudo chown pi:www-data "${jukebox_dir}"/scripts/*.py
    sudo chmod +x "${jukebox_dir}"/scripts/*.py

    # services to launch after boot using systemd
    # -rw-r--r-- 1 root root  304 Apr 30 10:07 phoniebox-rfid-reader.service
    # 1. delete old services (this is legacy, might throw errors but is necessary. Valid for versions < 1.1.8-beta)
    local systemd_dir="/etc/systemd/system"
    echo "### Deleting older versions of service daemons. This might throw errors, ignore them"
    sudo systemctl disable idle-watchdog
    sudo systemctl disable rfid-reader
    sudo systemctl disable phoniebox-startup-sound
    sudo systemctl disable gpio-buttons
    sudo systemctl disable phoniebox-rotary-encoder
    sudo systemctl disable phoniebox-gpio-buttons.service
    sudo rm "${systemd_dir}"/rfid-reader.service
    sudo rm "${systemd_dir}"/phoniebox-startup-sound.service
    sudo rm "${systemd_dir}"/gpio-buttons.service
    sudo rm "${systemd_dir}"/idle-watchdog.service
    sudo rm "${systemd_dir}"/phoniebox-rotary-encoder.service
    sudo rm "${systemd_dir}"/phoniebox-gpio-buttons.service
    echo "### Done with erasing old daemons. Stop ignoring errors!"

    # 2. install new ones - this is version > 1.1.8-beta
    RFID_READER_SERVICE="${systemd_dir}/phoniebox-rfid-reader.service"
    sudo cp "${jukebox_dir}"/misc/sampleconfigs/phoniebox-rfid-reader.service-default.sample "${RFID_READER_SERVICE}"

    STARTUP_SCRIPT_SERVICE="${systemd_dir}/phoniebox-startup-scripts.service"
    sudo cp "${jukebox_dir}"/misc/sampleconfigs/phoniebox-startup-scripts.service-default.sample "${STARTUP_SCRIPT_SERVICE}"

    IDLE_WATCHDOG_SERVICE="${systemd_dir}/phoniebox-idle-watchdog.service"
    sudo cp "${jukebox_dir}"/misc/sampleconfigs/phoniebox-idle-watchdog.service.sample "${IDLE_WATCHDOG_SERVICE}"

    if [[ "${GPIOconfig}" == "YES" ]]; then
        GPIO_CONTROL_SERVICE="${systemd_dir}/phoniebox-gpio-control.service"
        sudo cp "${jukebox_dir}"/misc/sampleconfigs/phoniebox-gpio-control.service.sample "${GPIO_CONTROL_SERVICE}"
    fi

    sudo chown root:root "${systemd_dir}"/phoniebox-*.service
    sudo chmod 644 "${systemd_dir}"/phoniebox-*.service
    # enable the services needed
    sudo systemctl enable phoniebox-idle-watchdog
    sudo systemctl enable phoniebox-rfid-reader
    sudo systemctl enable phoniebox-startup-scripts
    # copy mp3s for startup and shutdown sound to the right folder
    cp "${jukebox_dir}"/misc/sampleconfigs/startupsound.mp3.sample "${jukebox_dir}"/shared/startupsound.mp3
    cp "${jukebox_dir}"/misc/sampleconfigs/shutdownsound.mp3.sample "${jukebox_dir}"/shared/shutdownsound.mp3


    echo "Configuring MPD..."
    local mpd_conf="/etc/mpd.conf"
    sudo systemctl enable mpd
    sudo systemctl stop mpd
    # MPD configuration
    # -rw-r----- 1 mpd audio 14043 Jul 17 20:16 /etc/mpd.conf
    sudo cp "${jukebox_dir}"/misc/sampleconfigs/mpd.conf.sample ${mpd_conf}
    # Change vars to match install config
    sudo sed -i 's|%AUDIOiFace%|'"$(escape_for_sed "$AUDIOiFace")"'|' "${mpd_conf}"
    # for $DIRaudioFolders using | as alternate regex delimiter because of the folder path slash
    sudo sed -i 's|%DIRaudioFolders%|'"$(escape_for_sed "$DIRaudioFolders")"'|' "${mpd_conf}"
    sudo chown mpd:audio "${mpd_conf}"
    sudo chmod 640 "${mpd_conf}"


    # Spotify config
    if [ "${SPOTinstall}" == "YES" ]; then
        echo "Configuring Spotify support..."
        local mopidy_conf="/etc/mopidy/mopidy.conf"
        sudo systemctl disable mpd
        sudo systemctl stop mpd
        sudo systemctl enable mopidy
        sudo systemctl stop mopidy
        # Install Config Files
        sudo cp "${jukebox_dir}"/misc/sampleconfigs/locale.gen.sample /etc/locale.gen
        sudo cp "${jukebox_dir}"/misc/sampleconfigs/locale.sample /etc/default/locale
        sudo locale-gen
        sudo cp "${jukebox_dir}"/misc/sampleconfigs/mopidy.conf.sample "${mopidy_conf}"
        # Change vars to match install config
        sudo sed -i 's|%spotify_client_id%|'"$(escape_for_sed "$SPOTIclientid")"'|' "${mopidy_conf}"
        sudo sed -i 's|%spotify_client_secret%|'"$(escape_for_sed "$SPOTIclientsecret")"'|' "${mopidy_conf}"
        # for $DIRaudioFolders using | as alternate regex delimiter because of the folder path slash
        sudo sed -i 's|%DIRaudioFolders%|'"$(escape_for_sed "$DIRaudioFolders")"'|' "${mopidy_conf}"
    fi

    # GPIO-Control
    if [[ "${GPIOconfig}" == "YES" ]]; then
        ${pip_install} -r "${jukebox_dir}"/requirements-GPIO.txt
        sudo systemctl enable phoniebox-gpio-control.service
        if [[ ! -f "${jukebox_dir}"/settings/gpio_settings.ini ]]; then
            cp "${jukebox_dir}"/misc/sampleconfigs/gpio_settings.ini.sample "${jukebox_dir}"/settings/gpio_settings.ini
        fi
    fi

    # set which version has been installed
    if [ "${SPOTinstall}" == "YES" ]; then
        echo "plusSpotify" > "${jukebox_dir}"/settings/edition
    else
        echo "classic" > "${jukebox_dir}"/settings/edition
    fi

    wifi_settings "${jukebox_dir}"
    autohotspot "${jukebox_dir}"

    # / INSTALLATION
    #####################################################
}

wifi_settings() {
    local jukebox_dir="$1"
    local wifiExtDNS="8.8.8.8"

    ###############################
    # WiFi settings (SSID password)
    #
    # https://www.raspberrypi.org/documentation/configuration/wireless/wireless-cli.md
    #
    # $WIFIssid
    # $WIFIpass
    # $WIFIip
    # $WIFIipRouter
    if [ "${WIFIconfig}" == "YES" ]; then
        echo "Setting up wifi..."

        if [[ $(is_dhcpcd_enabled) == true ]]; then
            echo "... for dhcpcd"

            local wpa_supplicant_conf="/etc/wpa_supplicant/wpa_supplicant.conf"
            # -rw-rw-r-- 1 root netdev 137 Jul 16 08:53 /etc/wpa_supplicant/wpa_supplicant.conf
            sudo cp "${jukebox_dir}"/misc/sampleconfigs/wpa_supplicant.conf.sample "${wpa_supplicant_conf}"
            sudo sed -i 's|%WIFIcountryCode%|'"$(escape_for_sed "$WIFIcountryCode")"'|' "${wpa_supplicant_conf}"
            sudo chown root:netdev "${wpa_supplicant_conf}"
            sudo chmod 664 "${wpa_supplicant_conf}"

            # add network with high priority
            add_wireless_network "$WIFI_INTERFACE" "$WIFIssid" "$WIFIpass" 99

            # DHCP configuration settings
            local dhcpcd_conf="/etc/dhcpcd.conf"
            #-rw-rw-r-- 1 root netdev 0 Apr 17 11:25 /etc/dhcpcd.conf
            sudo cp "${jukebox_dir}"/misc/sampleconfigs/dhcpcd.conf-default-noHotspot.sample "${dhcpcd_conf}"
            # Change IP for router and Phoniebox
            sudo sed -i 's|%WIFIinterface%|'"$(escape_for_sed "$WIFI_INTERFACE")"'|' "${dhcpcd_conf}"
            sudo sed -i 's|%WIFIip%|'"$(escape_for_sed "$WIFIip")"'|' "${dhcpcd_conf}"
            sudo sed -i 's|%WIFIipRouter%|'"$(escape_for_sed "$WIFIipRouter")"'|' "${dhcpcd_conf}"
            sudo sed -i 's|%WIFIipExtDNS%|'"$(escape_for_sed "$wifiExtDNS")"'|' "${dhcpcd_conf}"
            sudo sed -i 's|%WIFIcountryCode%|'"$(escape_for_sed "$WIFIcountryCode")"'|' "${dhcpcd_conf}"
            # Change user:group and access mod
            sudo chown root:netdev "${dhcpcd_conf}"
            sudo chmod 664 "${dhcpcd_conf}"
        fi

        if [[ $(is_NetworkManager_enabled) == true ]]; then
            echo "... for NetworkManager"
            # add network with high priority
            add_wireless_network "$WIFI_INTERFACE" "$WIFIssid" "$WIFIpass" 99

            sudo nmcli connection modify "$WIFIssid" ipv4.method manual ipv4.address "$WIFIip"/24 ipv4.gateway "$WIFIipRouter" ipv4.dns "$WIFIipRouter $wifiExtDNS"
        fi
    fi
    # / WiFi settings (SSID password)
    ###############################
}

existing_assets() {
    local jukebox_dir="$1"
    local backup_dir="$2"

    #####################################################
    # EXISTING ASSETS TO USE FROM EXISTING INSTALL

    if [ "${EXISTINGuse}" == "YES" ]; then
        # RFID config for system control
        if [ "${EXISTINGuseRfidConf}" == "YES" ]; then
            # read old values and write them into new file (copied above already)
            # do not overwrite but use 'sed' in case there are new vars in new version installed

            # Read the existing RFID config file line by line and use
            # only lines which are separated (IFS) by '='.
            while IFS='=' read -r key val ; do
                # $var should be stripped of possible leading or trailing "
                val=${val%\"}
                val=${val#\"}
                key=${key}
                # Additional error check: key should not start with a hash and not be empty.
                if [ ! "${key:0:1}" == '#' ] && [ -n "$key" ]; then
                    # Replace the matching value in the newly created conf file
                    sed -i 's|%'"$key"'%|'"$val"'|' "${jukebox_dir}"/settings/rfid_trigger_play.conf
                fi
            done <"${backup_dir}"/settings/rfid_trigger_play.conf
        fi

        # RFID shortcuts for audio folders
        if [ "${EXISTINGuseRfidLinks}" == "YES" ]; then
            # copy from backup to new install
            cp -R "${backup_dir}"/shared/shortcuts/* "${jukebox_dir}"/shared/shortcuts/
        fi

        # Audio folders: use existing
        if [ "${EXISTINGuseAudio}" == "YES" ]; then
            # copy from backup to new install
            cp -R "${backup_dir}"/shared/audiofolders/* "$DIRaudioFolders/"
        fi

        # GPIO: use existing file
        if [ "${EXISTINGuseGpio}" == "YES" ]; then
            # copy from backup to new install
            cp "${backup_dir}"/settings/gpio_settings.ini "${jukebox_dir}"/settings/gpio_settings.ini
        fi

        # Button USB Encoder: use existing file
        if [ "${EXISTINGuseButtonUSBEncoder}" == "YES" ]; then
            # copy from backup to new install
            cp "${backup_dir}"/components/controls/buttons_usb_encoder/deviceName.txt "${jukebox_dir}"/components/controls/buttons_usb_encoder/deviceName.txt
            cp "${backup_dir}"/components/controls/buttons_usb_encoder/buttonMap.json "${jukebox_dir}"/components/controls/buttons_usb_encoder/buttonMap.json
            # make buttons_usb_encoder.py ready to be use from phoniebox-buttons-usb-encoder service
            sudo chmod +x "${jukebox_dir}"/components/controls/buttons_usb_encoder/buttons_usb_encoder.py
            # make sure service is still enabled by registering again
            USB_BUTTONS_SERVICE="/etc/systemd/system/phoniebox-buttons-usb-encoder.service"
            sudo cp -v "${jukebox_dir}"/components/controls/buttons_usb_encoder/phoniebox-buttons-usb-encoder.service.sample "${USB_BUTTONS_SERVICE}"
            sudo systemctl start phoniebox-buttons-usb-encoder.service
            sudo systemctl enable phoniebox-buttons-usb-encoder.service
        fi

        # Sound effects: use existing startup / shutdown sounds
        if [ "${EXISTINGuseSounds}" == "YES" ]; then
            # copy from backup to new install
            cp "${backup_dir}"/shared/startupsound.mp3 "${jukebox_dir}"/shared/startupsound.mp3
            cp "${backup_dir}"/shared/shutdownsound.mp3 "${jukebox_dir}"/shared/shutdownsound.mp3
        fi

    fi

    # / EXISTING ASSETS TO USE FROM EXISTING INSTALL
    ################################################
}


folder_access() {
    local jukebox_dir="$1"
    local user_group="$2"
    local mod="$3"

    #####################################################
    # Folders and Access Settings

    echo "Setting owner and permissions for directories..."

    # create playlists folder
    mkdir -p "${jukebox_dir}"/playlists
    sudo chown -R "${user_group}" "${jukebox_dir}"/playlists
    sudo chmod -R "${mod}" "${jukebox_dir}"/playlists

    # make sure the shared folder is accessible by the web server
    sudo chown -R "${user_group}" "${jukebox_dir}"/shared
    sudo chmod -R "${mod}" "${jukebox_dir}"/shared

    # make sure the htdocs folder can be changed by the web server
    sudo chown -R "${user_group}" "${jukebox_dir}"/htdocs
    sudo chmod -R "${mod}" "${jukebox_dir}"/htdocs

    sudo chown -R "${user_group}" "${jukebox_dir}"/settings
    sudo chmod -R "${mod}" "${jukebox_dir}"/settings

    # logs dir accessible by pi and www-data
    sudo chown "${user_group}" "${jukebox_dir}"/logs
    sudo chmod "${mod}" "${jukebox_dir}"/logs

    # audio folders might be somewhere else, so treat them separately
    sudo chown "${user_group}" "${DIRaudioFolders}"
    sudo chmod "${mod}" "${DIRaudioFolders}"

    # make sure bash scripts have the right settings
    sudo chown "${user_group}" "${jukebox_dir}"/scripts/*.sh
    sudo chmod +x "${jukebox_dir}"/scripts/*.sh
    sudo chown "${user_group}" "${jukebox_dir}"/scripts/*.py
    sudo chmod +x "${jukebox_dir}"/scripts/*.py

    # set audio volume to 100%
    # see: https://github.com/MiczFlor/RPi-Jukebox-RFID/issues/54
    sudo amixer cset numid=1 100%

    # delete the global.conf file, in case somebody manually copied stuff back and forth
    # this will be created the first time the Phoniebox is put to use by web app or RFID
    GLOBAL_CONF="${jukebox_dir}"/settings/global.conf
    if [ -f "${GLOBAL_CONF}" ]; then
        echo "global.conf needs to be deleted."
        rm "${GLOBAL_CONF}"
    fi

    # / Access settings
    #####################################################
}

autohotspot() {
    local jukebox_dir="$1"

    # Behave the same as other steps and only add configuration if selected and dont remove
    if [ "${AUTOHOTSPOTconfig}" == "YES" ]; then
        local setup_script="${jukebox_dir}/scripts/helperscripts/setup_autohotspot.sh"
        sudo chmod +x "${setup_script}"
        "${setup_script}" "${jukebox_dir}" "NO" # Uninstall present old versions first
        "${setup_script}" "${jukebox_dir}" "${AUTOHOTSPOTconfig}" "${AUTOHOTSPOTssid}" "${AUTOHOTSPOTcountryCode}" "${AUTOHOTSPOTpass}" "${AUTOHOTSPOTip}"
    fi
}

finished() {
    echo "
#
# INSTALLATION FINISHED
#
#####################################################

Let the sounds begin.
Find more information and documentation on the github account:
https://github.com/MiczFlor/RPi-Jukebox-RFID/wiki/

"
}

register_rfid_reader() {
    local jukebox_dir="$1"

    echo ""
    echo "-----------------------------------------------------"
    echo "Register RFID reader"
    echo "-----------------------------------------------------"

    if [[ ${INTERACTIVE} == "true" ]]; then
        echo "If you are using an RFID reader, connect it to your RPi."
        echo "(In case your RFID reader required soldering, consult the manual.)"
        # Use -e to display response of user in the logfile
        read -e -r -p "Have you connected your RFID reader? [Y/n] " response
        case "$response" in
            [nN][oO]|[nN])
                ;;
            *)
                echo  'Please select the RFID reader you want to use'
                options=("USB-Reader (e.g. Neuftech)" "RC522" "PN532" "Manual configuration" "Multiple RFID reader")
                select opt in "${options[@]}"; do
                    case $opt in
                        "USB-Reader (e.g. Neuftech)")
                            cd "${jukebox_dir}"/scripts/ || exit
                            python3 RegisterDevice.py
                            sudo chown pi:www-data "${jukebox_dir}"/scripts/deviceName.txt
                            sudo chmod 644 "${jukebox_dir}"/scripts/deviceName.txt
                            break
                            ;;
                        "RC522")
                            bash "${jukebox_dir}"/components/rfid-reader/RC522/setup_rc522.sh
                            break
                            ;;
                        "PN532")
                            bash "${jukebox_dir}"/components/rfid-reader/PN532/setup_pn532.sh
                            break
                            ;;
                        "Manual configuration")
                            echo "Please configure your reader manually."
                            break
                            ;;
                        "Multiple RFID reader")
                            cd "${jukebox_dir}"/scripts/ || exit
                            sudo python3 RegisterDevice.py.Multi
                            break
                            ;;
                        *)
                            echo "This is not a number"
                            ;;
                    esac
                done
        esac
    else
        echo "Skipping RFID reader setup..."
        echo "For manual registration of an RFID reader type:"
        echo "python3 ${JUKEBOX_HOME_DIR}/scripts/RegisterDevice.py"
    fi
}

cleanup_and_reboot() {

    echo ""
    echo "-----------------------------------------------------"
    echo "A reboot is required to activate all settings!"
    local do_shutdown=false
    if [[ ${INTERACTIVE} == "true" ]]; then
        # Use -e to display response of user in the logfile
        read -e -r -p "Would you like to reboot now? [Y/n] " response
        case "$response" in
            [nN][oO]|[nN])
                ;;
            *)
                do_shutdown=true
                ;;
        esac
    fi

    # Close logging
    log_close
    if [[ ${do_shutdown} == "true" ]]; then
        sudo shutdown -r now
    fi
}

########
# Main #
########
main() {
    checkPrerequisite

    # Skip interactive Samba WINS config dialog
    echo "samba-common samba-common/dhcp boolean false" | sudo debconf-set-selections

    if [[ ${INTERACTIVE} == "true" ]]; then
        welcome
        #reset_install_config_file
        config_wifi
        check_existing "${JUKEBOX_HOME_DIR}" "${JUKEBOX_BACKUP_DIR}" "${HOME_DIR}"
        config_autohotspot
        config_audio_interface
        config_spotify
        config_audio_folder "${JUKEBOX_HOME_DIR}"
        config_gpio
    else
        echo "Non-interactive installation!"
        check_config_file
    fi
    install_main "${JUKEBOX_HOME_DIR}"

    existing_assets "${JUKEBOX_HOME_DIR}" "${JUKEBOX_BACKUP_DIR}"
    folder_access "${JUKEBOX_HOME_DIR}" "pi:www-data" 775

    # Copy PhonieboxInstall.conf configuration file to settings folder
    sudo cp "${HOME_DIR}/PhonieboxInstall.conf" "${JUKEBOX_HOME_DIR}/settings/"
    sudo chown pi:www-data "${JUKEBOX_HOME_DIR}/settings/PhonieboxInstall.conf"
    sudo chmod 775 "${JUKEBOX_HOME_DIR}/settings/PhonieboxInstall.conf"

    finished

    register_rfid_reader "${JUKEBOX_HOME_DIR}"
    cleanup_and_reboot
}

start=$(date +%s)

main

end=$(date +%s)
runtime=$((end-start))
((h=${runtime}/3600))
((m=(${runtime}%3600)/60))
((s=${runtime}%60))
echo "Done (in ${h}h ${m}m ${s}s)."

#####################################################
# notes for things to do

# CLEANUP
## remove dir BACKUP (possibly not, because we do this at the beginning after user confirms for latest config)
#####################################################
