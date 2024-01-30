#!/usr/bin/env bash

AUTOHOTSPOT_INTERFACES_CONF_FILE="/etc/network/interfaces"
AUTOHOTSPOT_TARGET_PATH="/usr/bin/autohotspot"
AUTOHOTSPOT_SERVICE="autohotspot.service"
AUTOHOTSPOT_SERVICE_PATH="${SYSTEMD_PATH}/${AUTOHOTSPOT_SERVICE}"
AUTOHOTSPOT_TIMER="autohotspot.timer"
AUTOHOTSPOT_TIMER_PATH="${SYSTEMD_PATH}/${AUTOHOTSPOT_TIMER}"

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
