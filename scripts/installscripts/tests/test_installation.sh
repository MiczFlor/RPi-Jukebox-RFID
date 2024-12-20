#!/usr/bin/env bash

# Test to verify that the installation script works as expected.
# This script needs to be adapted, if new packages, etc are added to the install script

# The absolute path to the folder which contains this script
INSTALLATION_EXITCODE="${1:-0}"

PATHDATA="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
USER_NAME="$(whoami)"
HOME_DIR=$(getent passwd "$USER_NAME" | cut -d: -f6)

JUKEBOX_HOME_DIR="${HOME_DIR}/RPi-Jukebox-RFID"

tests=0
failed_tests=0

# Tool functions
source "${JUKEBOX_HOME_DIR}"/scripts/helperscripts/inc.networkHelper.sh

check_chmod_chown() {
    local mod_expected=$1
    local user_expected=$2
    local group_expected=$3
    local dir=$4
    local files=$5

    for file in ${files};
    do
        local fail=false
        mod_actual=$(stat --format '%a' "${dir}/${file}")
        user_actual=$(stat -c '%U' "${dir}/${file}")
        group_actual=$(stat -c '%G' "${dir}/${file}")
        test ! "${mod_expected}" -eq "${mod_actual}" && echo "  ERROR: ${file} actual mod (${mod_actual}) differs from expected (${mod_expected})!" && fail=true
        test ! "${user_expected}" == "${user_actual}" && echo "  ERROR: ${file} actual owner (${user_actual}) differs from expected (${user_expected})!" && fail=true
        test ! "${group_expected}" == "${group_actual}" && echo "  ERROR: ${file} actual group (${group_actual}) differs from expected (${group_expected})!" && fail=true
        if [ $fail == true ]; then
            ((failed_tests++))
        fi
        ((tests++))
    done
}

check_file_exists() {
    local file="$1"

    if [[ ! -f "${file}" ]]; then
        echo "  ERROR: '${file}' does not exists or is not a file!"
        ((failed_tests++))
    fi
    ((tests++))
}

check_file_contains_string() {
    local string="$1"
    local file="$2"
    local allowPartCheck="$3"

    local grep_option="w"
    if [ -v allowPartCheck ]; then
        grep_option=""
    fi

    # sudo is required for checking /etc/mopidy/mopidy.conf
    if [[ ! $(sudo grep -iF"${grep_option}" "${string}" "${file}") ]]; then
        echo "  ERROR: '${string}' not found in ${file}"
        ((failed_tests++))
    fi
    ((tests++))
}

check_file_contains_string_regex() {
    local string="$1"
    local file="$2"
    local allowPartCheck="$3"

    local grep_option="w"
    if [ -v allowPartCheck ]; then
        grep_option=""
    fi

    # sudo is required for checking /etc/mopidy/mopidy.conf
    if [[ ! $(sudo grep -i"${grep_option}" "${string}" "${file}") ]]; then
        echo "  ERROR: '${string}' not found in ${file}"
        ((failed_tests++))
    fi
    ((tests++))
}

check_service_state() {
    local service="$1"
    local desired_state="$2"

    local actual_state=$(systemctl show -p ActiveState --value "${service}")
    if [[ ! "${actual_state}" == "${desired_state}" ]]; then
        echo "  ERROR: service ${service} is not ${desired_state} (state: ${actual_state})."
        ((failed_tests++))
    fi
    ((tests++))
}

check_service_enablement() {
    local service="$1"
    local desired_enablement="$2"

    local actual_enablement=$(systemctl is-enabled "${service}")
    if [[ ! "${actual_enablement}" == "${desired_enablement}" ]]; then
        echo "  ERROR: service ${service} is not ${desired_enablement} (state: ${actual_enablement})."
        ((failed_tests++))
    fi
    ((tests++))
}

check_variable() {
  local variable=${1}
  # check if variable exist and if it's empty
  test -z "${!variable+x}" && echo "ERROR: \$${variable} is missing!" && fail=true && return
  test "${!variable}" == "" && echo "ERROR: \$${variable} is empty!" && fail=true
}

# Verify functions
verify_installation_exitcode() {
    if [ "${INSTALLATION_EXITCODE}" -eq 0 ]; then
        echo "Installation successfull."
        echo "Performing further checks..."
    elif [ "${INSTALLATION_EXITCODE}" -eq 2 ]; then
        echo "ABORT: Installation aborted due to prerequisite."
        echo "Further checks skipped."
        exit 0
    else
        echo "ERROR: Installation exited with errorcode '${INSTALLATION_EXITCODE}'"
        exit 1
    fi
}

verify_conf_file() {
    local install_conf="${HOME_DIR}/PhonieboxInstall.conf"
    printf "\nTESTING PhonieboxInstall.conf file...\n\n"
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
        echo "  ERROR: \$WIFIconfig is missing or not set!" && fail=true
    else
        echo "\$WIFIconfig is set to '$WIFIconfig'"
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
        echo "  ERROR: \$SPOTinstall is missing or not set!" && fail=true
    else
        echo "\$SPOTinstall is set to '$SPOTinstall'"
        if [ "$SPOTinstall" == "YES" ]; then
            check_variable "SPOTIclientid"
            check_variable "SPOTIclientsecret"
        fi
    fi
    check_variable "DIRaudioFolders"
    check_variable "GPIOconfig"

    # Feature optional. if config not present, defaults to NO
    if [[ -n "${AUTOHOTSPOTconfig}" ]]; then
        echo "\$AUTOHOTSPOTconfig is set to '$AUTOHOTSPOTconfig'"
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

verify_wifi_settings() {
    if [[ "$WIFIconfig" == "YES" ]]; then
        if [[ $(is_dhcpcd_enabled) == true ]]; then
            printf "\nTESTING WiFi settings (dhcpcd)...\n"
            local dhcpcd_conf="/etc/dhcpcd.conf"
            local wpa_supplicant_conf="/etc/wpa_supplicant/wpa_supplicant.conf"

            # check conf files
            check_file_contains_string "static ip_address=${WIFIip}/24" "${dhcpcd_conf}"
            check_file_contains_string "static routers=${WIFIipRouter}" "${dhcpcd_conf}"
            check_file_contains_string "static domain_name_servers=${WIFIipRouter} 8.8.8.8" "${dhcpcd_conf}"

            check_file_contains_string "country=${WIFIcountryCode}" "${wpa_supplicant_conf}"
            check_file_contains_string "ssid=\"${WIFIssid}\"" "${wpa_supplicant_conf}"
            local _pass=$(_get_passphrase_for_config "$WIFIssid" "$WIFIpass")
            check_file_contains_string "psk=${_pass}" "${wpa_supplicant_conf}"
            check_file_contains_string "priority=99" "${wpa_supplicant_conf}"

            # check owner and permissions
            check_chmod_chown 664 root netdev "/etc" "dhcpcd.conf"
            check_chmod_chown 664 root netdev "/etc/wpa_supplicant" "wpa_supplicant.conf"
        fi

        if [[ $(is_NetworkManager_enabled) == true ]]; then
            printf "\nTESTING WiFi settings (NetworkManager)...\n"
            local active_profile_path="/etc/NetworkManager/system-connections/${WIFIssid}.nmconnection"

            check_file_exists "${active_profile_path}"
            check_file_contains_string "ssid=${WIFIssid}" "${active_profile_path}"
            local _pass=$(_get_passphrase_for_config "$WIFIssid" "$WIFIpass")
            check_file_contains_string "psk=${_pass}" "${active_profile_path}"
            check_file_contains_string "address1=${WIFIip}" "${active_profile_path}"
            check_file_contains_string "gateway=${WIFIipRouter}" "${active_profile_path}"
            check_file_contains_string "dns=${WIFIipRouter}" "${active_profile_path}"
            check_file_contains_string "autoconnect-priority=99" "${active_profile_path}"
        fi
    fi
}

verify_autohotspot_settings() {
    if [[ "$AUTOHOTSPOTconfig" == "YES" ]]; then
        printf "\nTESTING autohotspot settings...\n\n"

        local systemd_dir="/etc/systemd/system"
        local interfaces_conf_file="/etc/network/interfaces"

        local autohotspot_script="/usr/bin/autohotspot"
        local autohotspot_service_daemon="autohotspot-daemon.service"
        local autohotspot_service_daemon_path="${systemd_dir}/${autohotspot_service_daemon}"
        local autohotspot_service="autohotspot.service"
        local autohotspot_service_path="${systemd_dir}/${autohotspot_service}"
        local autohotspot_timer="autohotspot.timer"
        local autohotspot_timer_path="${systemd_dir}/${autohotspot_timer}"

        local autohotspot_wifi_interface=wlan0
        local ip_without_last_segment=$(echo $AUTOHOTSPOTip | cut -d'.' -f1-3)
        local autohotspot_profile="Phoniebox_Hotspot"

        if [[ $(is_dhcpcd_enabled) == true ]]; then
            local dnsmasq_conf=/etc/dnsmasq.conf
            local hostapd_conf=/etc/hostapd/hostapd.conf
            local hostapd_deamon=/etc/default/hostapd
            local dhcpcd_conf=/etc/dhcpcd.conf

            check_file_exists "${interfaces_conf_file}"

            check_file_contains_string "interface=${autohotspot_wifi_interface}" "${dnsmasq_conf}"
            check_file_contains_string "dhcp-range=${ip_without_last_segment}.100,${ip_without_last_segment}.200,12h" "${dnsmasq_conf}"
            check_file_contains_string "interface=${autohotspot_wifi_interface}" "${hostapd_conf}"
            check_file_contains_string "ssid=${AUTOHOTSPOTssid}" "${hostapd_conf}"
            check_file_contains_string "wpa_passphrase=${AUTOHOTSPOTpass}" "${hostapd_conf}"
            check_file_contains_string "country_code=${AUTOHOTSPOTcountryCode}" "${hostapd_conf}"
            check_file_contains_string "DAEMON_CONF=\"${hostapd_conf}\"" "${hostapd_deamon}"
            check_file_contains_string "nohook wpa_supplicant" "${dhcpcd_conf}"

            check_file_exists "${autohotspot_script}"
            check_file_contains_string "wifidev=\"${autohotspot_wifi_interface}\"" "${autohotspot_script}"
            check_file_contains_string "hotspot_ip=${AUTOHOTSPOTip}" "${autohotspot_script}"
            check_file_contains_string "daemon_service=\"${autohotspot_service_daemon}\"" "${autohotspot_script}"

            check_file_exists "${autohotspot_service_daemon_path}"
            check_file_contains_string "ExecStart=wpa_supplicant -i \"${autohotspot_wifi_interface}\"" "${autohotspot_service_daemon_path}"

            check_file_exists "${autohotspot_service_path}"
            check_file_contains_string "ExecStart=${autohotspot_script}" "${autohotspot_service_path}"

            check_file_exists "${autohotspot_timer_path}"
            check_file_contains_string "Unit=${autohotspot_service}" "${autohotspot_timer_path}"

            # check owner and permissions
            check_chmod_chown 644 root root "/etc" "dnsmasq.conf hostapd/hostapd.conf default/hostapd"
            check_chmod_chown 664 root netdev "/etc" "dhcpcd.conf"
            check_chmod_chown 644 root root "${systemd_dir}" "${autohotspot_service_daemon} ${autohotspot_service} ${autohotspot_timer}"

            # check the services state
            check_service_enablement "${autohotspot_service_daemon}" enabled
            check_service_enablement "${autohotspot_service}" disabled
            check_service_enablement "${autohotspot_timer}" enabled
            check_service_enablement hostapd disabled
            check_service_enablement dnsmasq disabled
        fi

        if [[ $(is_NetworkManager_enabled) == true ]]; then
            check_file_exists "${interfaces_conf_file}"

            check_file_exists "${autohotspot_script}"
            check_file_contains_string "wdev0='${autohotspot_wifi_interface}'" "${autohotspot_script}"
            check_file_contains_string "ap_profile_name='${autohotspot_profile}'" "${autohotspot_script}"
            check_file_contains_string "ap_ssid='${AUTOHOTSPOTssid}'" "${autohotspot_script}"
            check_file_contains_string "ap_pw='${AUTOHOTSPOTpass}'" "${autohotspot_script}"
            check_file_contains_string "ap_ip='${AUTOHOTSPOTip}" "${autohotspot_script}" #intentional "open end"
            check_file_contains_string "ap_gate='${ip_without_last_segment}" "${autohotspot_script}" #intentional "open end"
            check_file_contains_string "timer_service_name='${autohotspot_timer}'" "${autohotspot_script}"

            check_file_exists "${autohotspot_service_path}"
            check_file_contains_string "ExecStart=${autohotspot_script}" "${autohotspot_service_path}"

            check_file_exists "${autohotspot_timer_path}"
            check_file_contains_string "Unit=${autohotspot_service}" "${autohotspot_timer_path}"

            # check the services state
            check_service_enablement "${autohotspot_service}" disabled
            check_service_enablement "${autohotspot_timer}" enabled
        fi
    fi
}

# Reads a textfile and pipes all lines as args to the given command.
# Does filter out comments, egg-prefixes and version suffixes
# Arguments:
#   1    : textfile to read
#   2... : command to receive args (e.g. 'echo', 'apt-get -y install', ...)
call_with_args_from_file() {
    local package_file="$1"
    shift

    sed 's/.*#egg=//g' ${package_file} | sed -E 's/(#|=|>|<).*//g' | xargs "$@"
}

verify_apt_packages() {
    local jukebox_dir="$1"
    local packages=$(call_with_args_from_file "${jukebox_dir}"/packages.txt echo)
    local packages_raspberrypi=$(call_with_args_from_file "${jukebox_dir}"/packages-raspberrypi.txt echo)
    local packages_spotify=$(call_with_args_from_file "${jukebox_dir}"/packages-spotify.txt echo)
    local packages_autohotspot_dhcpcd=$(call_with_args_from_file "${jukebox_dir}"/packages-autohotspot_dhcpcd.txt echo)
    local packages_autohotspot_NetworkManager=$(call_with_args_from_file "${jukebox_dir}"/packages-autohotspot_NetworkManager.txt echo)

    printf "\nTESTING installed packages...\n\n"

    # also check for spotify packages if it has been installed
    if [[ "${SPOTinstall}" == "YES" ]]; then
        packages="${packages} ${packages_spotify}"
        # not yet available on apt.mopidy.com, so install manually
        packages="${packages} gst-plugin-spotify"
    fi

    if [[ "$AUTOHOTSPOTconfig" == "YES" ]]; then
        if [[ $(is_dhcpcd_enabled) == true ]]; then
            packages="${packages} ${packages_autohotspot_dhcpcd}"
        fi
        if [[ $(is_NetworkManager_enabled) == true ]]; then
            packages="${packages} ${packages_autohotspot_NetworkManager}"
        fi
    fi

    # check for raspberry pi packages only on raspberry pi's but not on test docker containers running on x86_64 machines
    if [[ $(uname -m) =~ ^armv.+$ ]]; then
        packages="${packages} ${packages_raspberrypi}"
    fi

    local apt_list_installed=$(apt -qq list --installed 2>/dev/null)
    for package in ${packages}
    do
        if [[ $(echo "${apt_list_installed}" | grep -i "${package}.*installed") ]]; then
            echo "  ${package} is installed"
        else
            echo "  ERROR: ${package} is not installed"
            ((failed_tests++))
        fi
        ((tests++))
    done
}

verify_pip_packages() {
    local jukebox_dir="$1"
    local modules=$(call_with_args_from_file "${jukebox_dir}"/requirements.txt echo)
    local modules_spotify=$(call_with_args_from_file "${jukebox_dir}"/requirements-spotify.txt echo)
    local modules_pn532=$(call_with_args_from_file "${jukebox_dir}"/components/rfid-reader/PN532/requirements.txt echo)
    local modules_rc522=$(call_with_args_from_file "${jukebox_dir}"/components/rfid-reader/RC522/requirements.txt echo)
    local deviceName="${jukebox_dir}"/scripts/deviceName.txt

    printf "\nTESTING installed pip modules...\n\n"

    # also check for spotify pip modules if it has been installed
    if [[ "${SPOTinstall}" == "YES" ]]; then
        modules="${modules} ${modules_spotify}"
    fi

    if [[ -f "${deviceName}" ]]; then
        # RC522 reader is used
        if grep -Fxq "MFRC522" "${deviceName}"
        then
            modules="${modules} ${modules_rc522}"
        fi

        # PN532 reader is used
        if grep -Fxq "PN532" "${deviceName}"
        then
            modules="${modules} ${modules_pn532}"
        fi
    fi

    local pip_list_installed=$(pip3 list)
    for module in ${modules}
    do
        if [[ $(echo "${pip_list_installed}" | grep -i "${module}") ]]; then
            echo "  ${module} is installed"
        else
            echo "  ERROR: pip module ${module} is not installed"
            ((failed_tests++))
        fi
        ((tests++))
    done
}

verify_samba_config() {
    printf "\nTESTING samba config...\n\n"
    check_chmod_chown 644 root root "/etc/samba" "smb.conf"

    check_file_contains_string "path=${DIRaudioFolders}" "/etc/samba/smb.conf"
}

verify_webserver_config() {
    local phpver="$(ls -1 /etc/php)"
    printf "\nTESTING webserver config...\n\n"
    check_chmod_chown 644 root root "/etc/lighttpd" "lighttpd.conf"
    check_chmod_chown 644 root root "/etc/lighttpd/conf-available" "15-fastcgi-php.conf"
    check_chmod_chown 644 root root "/etc/php/${phpver}/cgi" "php.ini"
    check_file_contains_string "www-data ALL=(ALL) NOPASSWD: ALL" "/etc/sudoers.d/www-data"
    check_chmod_chown 440 root root "/etc/sudoers.d/" "www-data"

    # Bonus TODO: check that fastcgi and fastcgi-php mods are enabled
}

verify_systemd_services() {
    printf "\nTESTING systemd services...\n\n"
    # check that services exist
    check_chmod_chown 644 root root "/etc/systemd/system" "phoniebox-rfid-reader.service phoniebox-startup-scripts.service phoniebox-gpio-control.service phoniebox-idle-watchdog.service"

    # check that phoniebox services are enabled
    check_service_enablement phoniebox-idle-watchdog enabled
    check_service_enablement phoniebox-rfid-reader enabled
    check_service_enablement phoniebox-startup-scripts enabled
    check_service_enablement phoniebox-gpio-control enabled
}

verify_spotify_config() {
    if [[ "${SPOTinstall}" == "YES" ]]; then
        local mopidy_conf="/etc/mopidy/mopidy.conf"

        printf "\nTESTING spotify config...\n\n"

        check_file_contains_string "client_id = ${SPOTIclientid}" "${mopidy_conf}"
        check_file_contains_string "client_secret = ${SPOTIclientsecret}" "${mopidy_conf}"
        check_file_contains_string "media_dir = ${DIRaudioFolders}" "${mopidy_conf}"
        check_file_contains_string "mopidy ALL=NOPASSWD: /usr/local/lib/python" "/etc/sudoers.d/mopidy" allowPartCheck
        check_file_contains_string "/dist-packages/mopidy_iris/system.sh" "/etc/sudoers.d/mopidy" allowPartCheck
        check_chmod_chown 440 root root "/etc/sudoers.d/" "mopidy"

        # check that mopidy service is enabled
        check_service_enablement mopidy enabled
        # check that mpd service is disabled
        check_service_enablement mpd disabled
    fi
}

verify_mpd_config() {
    local mpd_conf="/etc/mpd.conf"

    printf "\nTESTING mpd config...\n\n"

    check_file_contains_string_regex "^[[:blank:]]\+mixer_control[[:blank:]]\+\"${AUDIOiFace}\"" "${mpd_conf}"
    check_file_contains_string_regex "^music_directory[[:blank:]]\+\"${DIRaudioFolders}\"" "${mpd_conf}"

    check_chmod_chown 640 mpd audio "/etc" "mpd.conf"

    # check that mpd service is enabled, when Spotify support is not installed
    if [[ "${SPOTinstall}" == "NO" ]]; then
        check_service_enablement mpd enabled
    fi
}

verify_folder_access() {
    local jukebox_dir="$1"
    printf "\nTESTING folder access...\n\n"

    # check owner and permissions
    check_chmod_chown 775 "$USER_NAME" www-data "${jukebox_dir}" "playlists shared htdocs settings"
    # ${DIRaudioFolders} => "testing" "audiofolders"
    check_chmod_chown 775 "$USER_NAME" www-data "${DIRaudioFolders}/.." "audiofolders"

    #find .sh and .py scripts that are NOT executable
    local count=$(find . -maxdepth 1 -type f \( -name "*.sh" -o -name "*.py" \) ! -executable | wc -l)
    if [[ "${count}" -gt 0 ]]; then
        echo "  ERROR: found ${count} '*.sh' and/or '*.py' files that are NOT executable:"
        find . -maxdepth 1 -type f \( -name "*.sh" -o -name "*.py" \) ! -executable
        ((failed_tests++))
    fi
    ((tests++))
}

main() {
    printf "\nTesting installation:\n"
    verify_installation_exitcode
    verify_conf_file
    verify_apt_packages "${JUKEBOX_HOME_DIR}"
    verify_pip_packages "${JUKEBOX_HOME_DIR}"
    verify_wifi_settings
    verify_samba_config
    verify_webserver_config
    verify_systemd_services
    verify_mpd_config
    verify_spotify_config
    verify_autohotspot_settings
    verify_folder_access "${JUKEBOX_HOME_DIR}"
}

start=$(date +%s)
main
end=$(date +%s)

runtime=$((end-start))
((h=${runtime}/3600))
((m=($runtime%3600)/60))
((s=$runtime%60))

if [[ "${failed_tests}" -gt 0 ]]; then
    echo "${failed_tests} Test(s) failed (of ${tests} tests) (in ${h}h ${m}m ${s}s)."
    exit 1
else
    echo "${tests} tests done in ${h}h ${m}m ${s}s."
fi

