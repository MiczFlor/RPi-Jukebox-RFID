AUTOHOTSPOT_INTERFACES_CONF_FILE="/etc/network/interfaces"
AUTOHOTSPOT_TARGET_PATH="/usr/bin/autohotspot"
AUTOHOTSPOT_SERVICE="autohotspot.service"
AUTOHOTSPOT_SERVICE_PATH="${SYSTEMD_PATH}/${AUTOHOTSPOT_SERVICE}"

_is_service_enabled() {
    local service="$1"
	local option="${2:+$2 }" # optional, dont't quote in next call!
    local actual_state=$(systemctl is-enabled ${option}${service})

	if [[ "$actual_state" == "enabled" ]]; then
		echo true
	else
		echo false
	fi
}

_is_dhcpcd_enabled() {
	echo $(_is_service_enabled "dhcpcd.service")
}

_is_NetworkManager_enabled() {
	echo $(_is_service_enabled "NetworkManager.service")
}


_get_interface() {
    # interfaces may vary
    WIFI_INTERFACE=$(iw dev | grep "Interface"| awk '{ print $2 }')
    #WIFI_REGION=$(iw reg get | grep country |  head -n 1 | awk '{ print $2}' | cut -d: -f1)

    # fix for CI runs on docker
    if [ "${CI_RUNNING}" == "true" ]; then
        if [ -z "${WIFI_INTERFACE}" ]; then
            WIFI_INTERFACE="CI TEST INTERFACE"
        fi
        # if [ -z "${WIFI_REGION}" ]; then
        #     WIFI_REGION="CI TEST REGION"
        # fi
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
            if [[ $(_is_dhcpcd_enabled) == true || "${CI_RUNNING}" == "true" ]]; then
                run_with_log_frame _run_setup_autohotspot_dhcpcd "Install AutoHotspot dhcpcd"
                installed=true
            fi

            if [[ $(_is_NetworkManager_enabled) == true || "${CI_RUNNING}" == "true" ]]; then
                run_with_log_frame _run_setup_autohotspot_NetworkManager "Install AutoHotspot NetworkManager"
                installed=true
            fi

            if [[ "$installed" != true ]]; then
                exit_on_error "ERROR: No network service available"
            fi
        fi
    fi
}
