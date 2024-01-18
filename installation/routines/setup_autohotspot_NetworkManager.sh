

AUTOHOTSPOT_RESOURCES_PATH="${INSTALLATION_PATH}/resources/autohotspot/NetworkManager"
AUTOHOTSPOT_TIMER="autohotspot.timer"
AUTOHOTSPOT_TIMER_PATH="${SYSTEMD_PATH}/${AUTOHOTSPOT_TIMER}"

_install_packages() {
    sudo apt-get -y install iw
}

_install_autohotspot() {
    # configure interface conf
    _config_file_backup "${AUTOHOTSPOT_INTERFACES_CONF_FILE}"
    sudo rm "${AUTOHOTSPOT_INTERFACES_CONF_FILE}"
    sudo touch "${AUTOHOTSPOT_INTERFACES_CONF_FILE}"

    # create service to trigger hotspot
    local ip_without_last_segment=$(_get_last_ip_segment $AUTOHOTSPOT_IP)
    sudo cp "${AUTOHOTSPOT_RESOURCES_PATH}"/accesspopup "${AUTOHOTSPOT_TARGET_PATH}"
    sudo sed -i "s|%%WIFI_INTERFACE%%|${WIFI_INTERFACE}|g" "${AUTOHOTSPOT_TARGET_PATH}"
    sudo sed -i "s|%%AUTOHOTSPOT_SSID%%|${AUTOHOTSPOT_SSID}|g" "${AUTOHOTSPOT_TARGET_PATH}"
    sudo sed -i "s|%%AUTOHOTSPOT_PASSWORD%%|${AUTOHOTSPOT_PASSWORD}|g" "${AUTOHOTSPOT_TARGET_PATH}"
    sudo sed -i "s|%%AUTOHOTSPOT_IP%%|${AUTOHOTSPOT_IP}|g" "${AUTOHOTSPOT_TARGET_PATH}"
    sudo sed -i "s|%%IP_WITHOUT_LAST_SEGMENT%%|${ip_without_last_segment}|g" "${AUTOHOTSPOT_TARGET_PATH}"
    sudo chmod +x "${AUTOHOTSPOT_TARGET_PATH}"

    sudo cp "${AUTOHOTSPOT_RESOURCES_PATH}"/autohotspot.service "${AUTOHOTSPOT_SERVICE_PATH}"
    sudo sed -i "s|%%AUTOHOTSPOT_SCRIPT%%|${AUTOHOTSPOT_TARGET_PATH}|g" "${AUTOHOTSPOT_SERVICE_PATH}"
    #sudo chown root:root "${AUTOHOTSPOT_SERVICE_PATH}"
    #sudo chmod 644 "${AUTOHOTSPOT_SERVICE_PATH}"

    sudo cp "${AUTOHOTSPOT_RESOURCES_PATH}"/autohotspot.timer "${AUTOHOTSPOT_TIMER_PATH}"
    sudo sed -i "s|%%AUTOHOTSPOT_SERVICE%%|${AUTOHOTSPOT_SERVICE_PATH}|g" "${AUTOHOTSPOT_TIMER_PATH}"
    #sudo chown root:root "${AUTOHOTSPOT_SERVICE_PATH}"
    #sudo chmod 644 "${AUTOHOTSPOT_SERVICE_PATH}"


    sudo systemctl unmask "${AUTOHOTSPOT_SERVICE}"
    sudo systemctl unmask "${AUTOHOTSPOT_TIMER}"
    sudo systemctl enable "${AUTOHOTSPOT_SERVICE}"
    sudo systemctl enable "${AUTOHOTSPOT_TIMER}"

    sudo systemctl start "${AUTOHOTSPOT_TIMER}"
}

_uninstall_autohotspot() {
    # clear autohotspot configurations made from past installation

    # stop services and clear services
    if systemctl list-unit-files "${AUTOHOTSPOT_SERVICE}" >/dev/null 2>&1 ; then
        sudo systemctl stop "${AUTOHOTSPOT_SERVICE}"
        sudo systemctl stop "${AUTOHOTSPOT_TIMER}"
        sudo systemctl disable "${AUTOHOTSPOT_SERVICE}"
        sudo systemctl disable "${AUTOHOTSPOT_TIMER}"
        sudo rm "${AUTOHOTSPOT_SERVICE_PATH}"
        sudo rm "${AUTOHOTSPOT_TIMER_PATH}"
    fi

    if [ -f "${AUTOHOTSPOT_TARGET_PATH}" ]; then
        sudo rm "${AUTOHOTSPOT_TARGET_PATH}"
    fi

    # remove config files
    _config_file_revert "${AUTOHOTSPOT_INTERFACES_CONF_FILE}"
}

_autohotspot_check() {
    print_verify_installation

    verify_apt_packages iw

    verify_service_enablement hostapd.service disabled
    verify_service_enablement dnsmasq.service disabled
    verify_service_enablement "${AUTOHOTSPOT_SERVICE}" enabled

    verify_files_exists "${AUTOHOTSPOT_INTERFACES_CONF_FILE}"

    local ip_without_last_segment=$(_get_last_ip_segment $AUTOHOTSPOT_IP)
    verify_files_exists "${AUTOHOTSPOT_TARGET_PATH}"
    verify_file_contains_string "wdev0=\"${WIFI_INTERFACE}\"" "${AUTOHOTSPOT_TARGET_PATH}"
    verify_file_contains_string "ap_ssid=${AUTOHOTSPOT_SSID}" "${AUTOHOTSPOT_TARGET_PATH}"
    verify_file_contains_string "ap_pw=${AUTOHOTSPOT_PASSWORD}" "${AUTOHOTSPOT_TARGET_PATH}"
    verify_file_contains_string "ap_ip=${AUTOHOTSPOT_IP}" "${AUTOHOTSPOT_TARGET_PATH}"
    verify_file_contains_string "ap_gate=${ip_without_last_segment}" "${AUTOHOTSPOT_TARGET_PATH}"

    verify_files_exists "${AUTOHOTSPOT_SERVICE_PATH}"
    verify_file_contains_string "ExecStart=${AUTOHOTSPOT_TARGET_PATH}" "${AUTOHOTSPOT_SERVICE_PATH}"

    verify_files_exists "${AUTOHOTSPOT_TIMER_PATH}"
    verify_file_contains_string "ExecStart=${AUTOHOTSPOT_SERVICE_PATH}" "${AUTOHOTSPOT_TIMER_PATH}"
}

_run_setup_autohotspot_NetworkManager() {
    _install_packages
    _get_interface
    _uninstall_autohotspot
    _install_autohotspot
    _autohotspot_check
}


