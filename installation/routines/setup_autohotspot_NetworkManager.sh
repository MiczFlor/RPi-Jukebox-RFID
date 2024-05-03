#!/usr/bin/env bash

AUTOHOTSPOT_NETWORKMANAGER_RESOURCES_PATH="${INSTALLATION_PATH}/resources/autohotspot/NetworkManager"
AUTOHOTSPOT_NETWORKMANAGER_CONNECTIONS_PATH="/etc/NetworkManager/system-connections"

_install_packages_NetworkManager() {
    sudo apt-get -y install iw
}

_install_autohotspot_NetworkManager() {
    # configure interface conf
    config_file_backup "${AUTOHOTSPOT_INTERFACES_CONF_FILE}"
    sudo rm "${AUTOHOTSPOT_INTERFACES_CONF_FILE}"
    sudo touch "${AUTOHOTSPOT_INTERFACES_CONF_FILE}"

    # create service to trigger hotspot
    local ip_without_last_segment=$(_get_last_ip_segment $AUTOHOTSPOT_IP)
    sudo cp "${AUTOHOTSPOT_NETWORKMANAGER_RESOURCES_PATH}"/autohotspot "${AUTOHOTSPOT_TARGET_PATH}"
    sudo sed -i "s|%%WIFI_INTERFACE%%|${WIFI_INTERFACE}|g" "${AUTOHOTSPOT_TARGET_PATH}"
    sudo sed -i "s|%%AUTOHOTSPOT_PROFILE%%|${AUTOHOTSPOT_PROFILE}|g" "${AUTOHOTSPOT_TARGET_PATH}"
    sudo sed -i "s|%%AUTOHOTSPOT_SSID%%|${AUTOHOTSPOT_SSID}|g" "${AUTOHOTSPOT_TARGET_PATH}"
    sudo sed -i "s|%%AUTOHOTSPOT_PASSWORD%%|${AUTOHOTSPOT_PASSWORD}|g" "${AUTOHOTSPOT_TARGET_PATH}"
    sudo sed -i "s|%%AUTOHOTSPOT_IP%%|${AUTOHOTSPOT_IP}|g" "${AUTOHOTSPOT_TARGET_PATH}"
    sudo sed -i "s|%%IP_WITHOUT_LAST_SEGMENT%%|${ip_without_last_segment}|g" "${AUTOHOTSPOT_TARGET_PATH}"
    sudo sed -i "s|%%AUTOHOTSPOT_TIMER_NAME%%|${AUTOHOTSPOT_TIMER}|g" "${AUTOHOTSPOT_TARGET_PATH}"
    sudo chmod +x "${AUTOHOTSPOT_TARGET_PATH}"

    sudo cp "${AUTOHOTSPOT_NETWORKMANAGER_RESOURCES_PATH}"/autohotspot.service "${AUTOHOTSPOT_SERVICE_PATH}"
    sudo sed -i "s|%%AUTOHOTSPOT_SCRIPT%%|${AUTOHOTSPOT_TARGET_PATH}|g" "${AUTOHOTSPOT_SERVICE_PATH}"

    sudo cp "${AUTOHOTSPOT_NETWORKMANAGER_RESOURCES_PATH}"/autohotspot.timer "${AUTOHOTSPOT_TIMER_PATH}"
    sudo sed -i "s|%%AUTOHOTSPOT_SERVICE%%|${AUTOHOTSPOT_SERVICE}|g" "${AUTOHOTSPOT_TIMER_PATH}"


    sudo systemctl unmask "${AUTOHOTSPOT_SERVICE}"
    sudo systemctl unmask "${AUTOHOTSPOT_TIMER}"
    sudo systemctl disable "${AUTOHOTSPOT_SERVICE}"
    sudo systemctl enable "${AUTOHOTSPOT_TIMER}"
}

_uninstall_autohotspot_NetworkManager() {
    # clear autohotspot configurations made from past installation

    # stop services and clear services
    if systemctl list-unit-files "${AUTOHOTSPOT_SERVICE}" >/dev/null 2>&1 ; then
        sudo systemctl stop "${AUTOHOTSPOT_TIMER}"
        sudo systemctl disable "${AUTOHOTSPOT_TIMER}"
        sudo systemctl stop "${AUTOHOTSPOT_SERVICE}"
        sudo systemctl disable "${AUTOHOTSPOT_SERVICE}"
        sudo rm "${AUTOHOTSPOT_SERVICE_PATH}"
        sudo rm "${AUTOHOTSPOT_TIMER_PATH}"
    fi

    if [ -f "${AUTOHOTSPOT_TARGET_PATH}" ]; then
        sudo rm "${AUTOHOTSPOT_TARGET_PATH}"
    fi

    sudo rm -f "${AUTOHOTSPOT_NETWORKMANAGER_CONNECTIONS_PATH}/${AUTOHOTSPOT_PROFILE}*"

    # remove config files
    config_file_revert "${AUTOHOTSPOT_INTERFACES_CONF_FILE}"
}

_autohotspot_check_NetworkManager() {
    print_verify_installation

    verify_apt_packages iw

    verify_service_enablement "${AUTOHOTSPOT_SERVICE}" disabled
    verify_service_enablement "${AUTOHOTSPOT_TIMER}" enabled

    verify_files_exists "${AUTOHOTSPOT_INTERFACES_CONF_FILE}"

    local ip_without_last_segment=$(_get_last_ip_segment $AUTOHOTSPOT_IP)
    verify_files_exists "${AUTOHOTSPOT_TARGET_PATH}"
    verify_file_contains_string "wdev0='${WIFI_INTERFACE}'" "${AUTOHOTSPOT_TARGET_PATH}"
    verify_file_contains_string "ap_profile_name='${AUTOHOTSPOT_PROFILE}'" "${AUTOHOTSPOT_TARGET_PATH}"
    verify_file_contains_string "ap_ssid='${AUTOHOTSPOT_SSID}'" "${AUTOHOTSPOT_TARGET_PATH}"
    verify_file_contains_string "ap_pw='${AUTOHOTSPOT_PASSWORD}'" "${AUTOHOTSPOT_TARGET_PATH}"
    verify_file_contains_string "ap_ip='${AUTOHOTSPOT_IP}" "${AUTOHOTSPOT_TARGET_PATH}" #intentional "open end"
    verify_file_contains_string "ap_gate='${ip_without_last_segment}" "${AUTOHOTSPOT_TARGET_PATH}" #intentional "open end"
    verify_file_contains_string "timer_service_name='${AUTOHOTSPOT_TIMER}'" "${AUTOHOTSPOT_TARGET_PATH}"

    verify_files_exists "${AUTOHOTSPOT_SERVICE_PATH}"
    verify_file_contains_string "ExecStart=${AUTOHOTSPOT_TARGET_PATH}" "${AUTOHOTSPOT_SERVICE_PATH}"

    verify_files_exists "${AUTOHOTSPOT_TIMER_PATH}"
    verify_file_contains_string "Unit=${AUTOHOTSPOT_SERVICE}" "${AUTOHOTSPOT_TIMER_PATH}"
}

_run_setup_autohotspot_NetworkManager() {
    log "Install AutoHotspot NetworkManager"
    _install_packages_NetworkManager
    _get_interface
    _uninstall_autohotspot_NetworkManager
    _install_autohotspot_NetworkManager
    _autohotspot_check_NetworkManager
}
