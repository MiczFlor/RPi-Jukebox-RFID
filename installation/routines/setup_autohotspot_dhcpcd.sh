#!/usr/bin/env bash

# inspired by
# https://www.raspberryconnect.com/projects/65-raspberrypi-hotspot-accesspoints/158-raspberry-pi-auto-wifi-hotspot-switch-direct-connection

AUTOHOTSPOT_HOSTAPD_CONF_FILE="/etc/hostapd/hostapd.conf"
AUTOHOTSPOT_HOSTAPD_DAEMON_CONF_FILE="/etc/default/hostapd"
AUTOHOTSPOT_DNSMASQ_CONF_FILE="/etc/dnsmasq.conf"
AUTOHOTSPOT_DHCPCD_CONF_FILE="/etc/dhcpcd.conf"
AUTOHOTSPOT_DHCPCD_CONF_NOHOOK_WPA_SUPPLICANT="nohook wpa_supplicant"

AUTOHOTSPOT_RESOURCES_PATH="${INSTALLATION_PATH}/resources/autohotspot/dhcpcd"

_install_packages_dhcpcd() {
    sudo apt-get -y install hostapd dnsmasq iw

    # disable services. We want to start them manually
    sudo systemctl unmask hostapd
    sudo systemctl disable hostapd
    sudo systemctl stop hostapd
    sudo systemctl unmask dnsmasq
    sudo systemctl disable dnsmasq
    sudo systemctl stop dnsmasq
}

_install_autohotspot_dhcpcd() {
    # configure interface conf
    _config_file_backup "${AUTOHOTSPOT_INTERFACES_CONF_FILE}"
    sudo rm "${AUTOHOTSPOT_INTERFACES_CONF_FILE}"
    sudo touch "${AUTOHOTSPOT_INTERFACES_CONF_FILE}"


    # configure DNS
    _config_file_backup "${AUTOHOTSPOT_DNSMASQ_CONF_FILE}"

    local ip_without_last_segment=$(_get_last_ip_segment $AUTOHOTSPOT_IP)
    sudo cp "${AUTOHOTSPOT_RESOURCES_PATH}"/dnsmasq.conf "${AUTOHOTSPOT_DNSMASQ_CONF_FILE}"
    sudo sed -i "s|%%WIFI_INTERFACE%%|${WIFI_INTERFACE}|g" "${AUTOHOTSPOT_DNSMASQ_CONF_FILE}"
    sudo sed -i "s|%%IP_WITHOUT_LAST_SEGMENT%%|${ip_without_last_segment}|g" "${AUTOHOTSPOT_DNSMASQ_CONF_FILE}"
    #sudo chown root:root "${AUTOHOTSPOT_DNSMASQ_CONF_FILE}"
    #sudo chmod 644 "${AUTOHOTSPOT_DNSMASQ_CONF_FILE}"


    # configure hostapd conf
    _config_file_backup "${AUTOHOTSPOT_HOSTAPD_CONF_FILE}"

    sudo cp "${AUTOHOTSPOT_RESOURCES_PATH}"/hostapd.conf "${AUTOHOTSPOT_HOSTAPD_CONF_FILE}"
    sudo sed -i "s|%%WIFI_INTERFACE%%|${WIFI_INTERFACE}|g" "${AUTOHOTSPOT_HOSTAPD_CONF_FILE}"
    sudo sed -i "s|%%AUTOHOTSPOT_SSID%%|${AUTOHOTSPOT_SSID}|g" "${AUTOHOTSPOT_HOSTAPD_CONF_FILE}"
    sudo sed -i "s|%%AUTOHOTSPOT_PASSWORD%%|${AUTOHOTSPOT_PASSWORD}|g" "${AUTOHOTSPOT_HOSTAPD_CONF_FILE}"
    sudo sed -i "s|%%AUTOHOTSPOT_COUNTRYCODE%%|${AUTOHOTSPOT_COUNTRYCODE}|g" "${AUTOHOTSPOT_HOSTAPD_CONF_FILE}"
    #sudo chown root:root "${AUTOHOTSPOT_HOSTAPD_CONF_FILE}"
    #sudo chmod 644 "${AUTOHOTSPOT_HOSTAPD_CONF_FILE}"


    # configure hostapd daemon
    _config_file_backup "${AUTOHOTSPOT_HOSTAPD_DAEMON_CONF_FILE}"

    sudo cp "${AUTOHOTSPOT_RESOURCES_PATH}"/hostapd "${AUTOHOTSPOT_HOSTAPD_DAEMON_CONF_FILE}"
    sudo sed -i "s|%%HOSTAPD_CONF%%|${AUTOHOTSPOT_HOSTAPD_CONF_FILE}|g" "${AUTOHOTSPOT_HOSTAPD_DAEMON_CONF_FILE}"
    #sudo chown root:root "${AUTOHOTSPOT_HOSTAPD_DAEMON_CONF_FILE}"
    #sudo chmod 644 "${AUTOHOTSPOT_HOSTAPD_DAEMON_CONF_FILE}"


    # configure dhcpcd conf
    _config_file_backup "${AUTOHOTSPOT_DHCPCD_CONF_FILE}"
    if [ ! -f "${AUTOHOTSPOT_DHCPCD_CONF_FILE}" ]; then
        sudo touch "${AUTOHOTSPOT_DHCPCD_CONF_FILE}"
        sudo chown root:netdev "${AUTOHOTSPOT_DHCPCD_CONF_FILE}"
        sudo chmod 664 "${AUTOHOTSPOT_DHCPCD_CONF_FILE}"
    fi

    if [[ ! $(grep -w "${AUTOHOTSPOT_DHCPCD_CONF_NOHOOK_WPA_SUPPLICANT}" ${AUTOHOTSPOT_DHCPCD_CONF_FILE}) ]]; then
        sudo bash -c "echo ${AUTOHOTSPOT_DHCPCD_CONF_NOHOOK_WPA_SUPPLICANT} >> ${AUTOHOTSPOT_DHCPCD_CONF_FILE}"
    fi

    # create service to trigger hotspot
    sudo cp "${AUTOHOTSPOT_RESOURCES_PATH}"/autohotspot "${AUTOHOTSPOT_TARGET_PATH}"
    sudo sed -i "s|%%WIFI_INTERFACE%%|${WIFI_INTERFACE}|g" "${AUTOHOTSPOT_TARGET_PATH}"
    sudo sed -i "s|%%AUTOHOTSPOT_IP%%|${AUTOHOTSPOT_IP}|g" "${AUTOHOTSPOT_TARGET_PATH}"
    sudo chmod +x "${AUTOHOTSPOT_TARGET_PATH}"

    sudo cp "${AUTOHOTSPOT_RESOURCES_PATH}"/autohotspot.service "${AUTOHOTSPOT_SERVICE_PATH}"
    sudo sed -i "s|%%AUTOHOTSPOT_SCRIPT%%|${AUTOHOTSPOT_TARGET_PATH}|g" "${AUTOHOTSPOT_SERVICE_PATH}"
    #sudo chown root:root "${AUTOHOTSPOT_SERVICE_PATH}"
    #sudo chmod 644 "${AUTOHOTSPOT_SERVICE_PATH}"

    sudo systemctl enable "${AUTOHOTSPOT_SERVICE}"

    # create crontab entry
    local crontab_user=$(crontab -l 2>/dev/null)
    if [[ -z "${crontab_user}" || ! $(echo "${crontab_user}" | grep -w "${AUTOHOTSPOT_TARGET_PATH}") ]]; then
        (echo "${crontab_user}"; echo "*/5 * * * * sudo ${AUTOHOTSPOT_TARGET_PATH} 2>&1 | logger -t autohotspot") | crontab -
        (echo "${crontab_user}"; echo "@reboot sudo ${AUTOHOTSPOT_TARGET_PATH} 2>&1 | logger -t autohotspot") | crontab -
    fi
}


_uninstall_autohotspot_dhcpcd() {
    # clear autohotspot configurations made from past installation

    # stop services and clear services
    if systemctl list-unit-files "${AUTOHOTSPOT_SERVICE}" >/dev/null 2>&1 ; then
        sudo systemctl stop hostapd
        sudo systemctl stop dnsmasq
        sudo systemctl stop "${AUTOHOTSPOT_SERVICE}"
        sudo systemctl disable "${AUTOHOTSPOT_SERVICE}"
        sudo rm "${AUTOHOTSPOT_SERVICE_PATH}"
    fi

    # remove crontab entry and script
    local crontab_user=$(crontab -l 2>/dev/null)
    if [[ ! -z "${crontab_user}" && $(echo "${crontab_user}" | grep -w "${AUTOHOTSPOT_TARGET_PATH}") ]]; then
        echo "${crontab_user}" | sed "s|^.*\s${AUTOHOTSPOT_TARGET_PATH}\s.*$||g" | crontab -
    fi

    if [ -f "${AUTOHOTSPOT_TARGET_PATH}" ]; then
        sudo rm "${AUTOHOTSPOT_TARGET_PATH}"
    fi

    # remove config files
    _config_file_revert "${AUTOHOTSPOT_DNSMASQ_CONF_FILE}"
    _config_file_revert "${AUTOHOTSPOT_HOSTAPD_CONF_FILE}"
    _config_file_revert "${AUTOHOTSPOT_HOSTAPD_DAEMON_CONF_FILE}"
    _config_file_revert "${AUTOHOTSPOT_DHCPCD_CONF_FILE}"
    _config_file_revert "${AUTOHOTSPOT_INTERFACES_CONF_FILE}"
}


_autohotspot_check_dhcpcd() {
    print_verify_installation

    verify_apt_packages hostapd dnsmasq iw

    verify_service_enablement hostapd.service disabled
    verify_service_enablement dnsmasq.service disabled
    verify_service_enablement "${AUTOHOTSPOT_SERVICE}" enabled

    verify_files_exists "${AUTOHOTSPOT_INTERFACES_CONF_FILE}"

    local ip_without_last_segment=$(_get_last_ip_segment $AUTOHOTSPOT_IP)
    verify_files_exists "${AUTOHOTSPOT_DNSMASQ_CONF_FILE}"
    verify_file_contains_string "${WIFI_INTERFACE}" "${AUTOHOTSPOT_DNSMASQ_CONF_FILE}"
    verify_file_contains_string "dhcp-range=${ip_without_last_segment}" "${AUTOHOTSPOT_DNSMASQ_CONF_FILE}"

    verify_files_exists "${AUTOHOTSPOT_HOSTAPD_CONF_FILE}"
    verify_file_contains_string "interface=${WIFI_INTERFACE}" "${AUTOHOTSPOT_HOSTAPD_CONF_FILE}"
    verify_file_contains_string "ssid=${AUTOHOTSPOT_SSID}" "${AUTOHOTSPOT_HOSTAPD_CONF_FILE}"
    verify_file_contains_string "wpa_passphrase=${AUTOHOTSPOT_PASSWORD}" "${AUTOHOTSPOT_HOSTAPD_CONF_FILE}"
    verify_file_contains_string "country_code=${AUTOHOTSPOT_COUNTRYCODE}" "${AUTOHOTSPOT_HOSTAPD_CONF_FILE}"

    verify_files_exists "${AUTOHOTSPOT_HOSTAPD_DAEMON_CONF_FILE}"
    verify_file_contains_string "DAEMON_CONF=\"${AUTOHOTSPOT_HOSTAPD_CONF_FILE}\"" "${AUTOHOTSPOT_HOSTAPD_DAEMON_CONF_FILE}"

    verify_files_exists "${AUTOHOTSPOT_DHCPCD_CONF_FILE}"
    verify_file_contains_string "${AUTOHOTSPOT_DHCPCD_CONF_NOHOOK_WPA_SUPPLICANT}" "${AUTOHOTSPOT_DHCPCD_CONF_FILE}"

    verify_files_exists "${AUTOHOTSPOT_TARGET_PATH}"
    verify_file_contains_string "wifidev=\"${WIFI_INTERFACE}\"" "${AUTOHOTSPOT_TARGET_PATH}"
    verify_file_contains_string "hotspot_ip=${AUTOHOTSPOT_IP}" "${AUTOHOTSPOT_TARGET_PATH}"

    verify_files_exists "${AUTOHOTSPOT_SERVICE_PATH}"
    verify_file_contains_string "ExecStart=${AUTOHOTSPOT_TARGET_PATH}" "${AUTOHOTSPOT_SERVICE_PATH}"

    local crontab_user=$(crontab -l 2>/dev/null)
    if [[ ! $(echo "${crontab_user}" | grep -w "${AUTOHOTSPOT_TARGET_PATH}") ]]; then
        exit_on_error "ERROR: crontab for user not installed"
    fi
}

_run_setup_autohotspot_dhcpcd() {
    _install_packages_dhcpcd
    _get_interface
    _uninstall_autohotspot_dhcpcd
    _install_autohotspot_dhcpcd
    _autohotspot_check_dhcpcd
}
