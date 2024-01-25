#!/usr/bin/env bash

AUTOHOTSPOT_INTERFACES_CONF_FILE="/etc/network/interfaces"
AUTOHOTSPOT_TARGET_PATH="/usr/bin/autohotspot"
AUTOHOTSPOT_SERVICE="autohotspot.service"
AUTOHOTSPOT_SERVICE_PATH="${SYSTEMD_PATH}/${AUTOHOTSPOT_SERVICE}"

_get_interface() {
    # interfaces may vary
    WIFI_INTERFACE=$(iw dev | grep "Interface"| awk '{ print $2 }')

    # fix for CI runs on docker
    if [ "${CI_RUNNING}" == "true" ]; then
        if [ -z "${WIFI_INTERFACE}" ]; then
            WIFI_INTERFACE="CI TEST INTERFACE"
        fi
    fi
}

_config_file_backup() {
    # create flag file or copy present conf to orig file
    # to correctly handling future deactivation of autohotspot
    local config_file="$1"
    local config_flag_file="${config_file}.remove"
    local config_orig_file="${config_file}.orig"
    if [ ! -f "${config_file}" ]; then
        sudo touch "${config_flag_file}"
    elif [ ! -f "${config_orig_file}" ] && [ ! -f "${config_flag_file}" ]; then
        sudo cp "${config_file}" "${config_orig_file}"
    fi
}

_config_file_revert() {
    # revert config files to original (remove if it wasn't existing before)
    local config_file="$1"
    local config_flag_file="${config_file}.remove"
    local config_orig_file="${config_file}.orig"
    if [ -f "${config_flag_file}" ]; then
        sudo rm "${config_flag_file}" "${config_file}"
    elif [ -f "${config_orig_file}" ]; then
        sudo mv "${config_orig_file}" "${config_file}"
    fi
}

_get_last_ip_segment() {
    local ip="$1"
    echo $ip | cut -d'.' -f1-3
}


setup_autohotspot() {
    if [ "$ENABLE_AUTOHOTSPOT" == true ] ; then
        local installed=false
        if [[ $(is_dhcpcd_enabled) == true || "${CI_RUNNING}" == "true" ]]; then
            run_with_log_frame _run_setup_autohotspot_dhcpcd "Install AutoHotspot"
            installed=true
        fi

        if [[ $(is_NetworkManager_enabled) == true || "${CI_RUNNING}" == "true" ]]; then
            run_with_log_frame _run_setup_autohotspot_NetworkManager "Install AutoHotspot"
            installed=true
        fi

        if [[ "$installed" != true ]]; then
            exit_on_error "ERROR: No network service available"
        fi
    fi
}
