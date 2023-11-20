#!/usr/bin/env bash

AUTOHOTSPOT_HOSTAPD_CONF_FILE="/etc/hostapd/hostapd.conf"
AUTOHOTSPOT_HOSTAPD_DAEMON_CONF_FILE="/etc/default/hostapd"
AUTOHOTSPOT_DNSMASQ_CONF_FILE="/etc/dnsmasq.conf"
AUTOHOTSPOT_DHCPD_CONF_FILE="/etc/dhcpcd.conf"

AUTOHOTSPOT_TARGET_PATH="/usr/bin/autohotspot"

_get_interface() {
    # interfaces may vary
    WIFI_INTERFACE=$(iw dev | grep "Interface"| awk '{ print $2 }')
    WIFI_REGION=$(iw reg get | grep country | awk '{ print $2}' | cut -d: -f1)
}

_install_packages() {
    sudo apt-get -y install hostapd dnsmasq iw

    # disable services. We want to start them manually
    sudo systemctl unmask hostapd
    sudo systemctl disable hostapd
    sudo systemctl disable dnsmasq
}

_configure_hostapd() {
    local HOSTAPD_CUSTOM_FILE="${INSTALLATION_PATH}"/resources/autohotspot/hostapd.conf

    sed -i "s/WIFI_INTERFACE/${WIFI_INTERFACE}/g" "${HOSTAPD_CUSTOM_FILE}"
    sed -i "s/AUTOHOTSPOT_PASSWORD/${AUTOHOTSPOT_PASSWORD}/g" "${HOSTAPD_CUSTOM_FILE}"
    sed -i "s/WIFI_REGION/${WIFI_REGION}/g" "${HOSTAPD_CUSTOM_FILE}"
    sudo cp "${HOSTAPD_CUSTOM_FILE}" "${AUTOHOTSPOT_HOSTAPD_CONF_FILE}"

    sudo sed -i "s@^#DAEMON_CONF=.*@DAEMON_CONF=\"${AUTOHOTSPOT_HOSTAPD_CONF_FILE}\"@g" "${AUTOHOTSPOT_HOSTAPD_DAEMON_CONF_FILE}"
}

_configure_dnsmasq() {
    sudo tee -a "${AUTOHOTSPOT_DNSMASQ_CONF_FILE}" <<-EOF
#AutoHotspot Config
#stop DNSmasq from using resolv.conf
no-resolv
#Interface to use
interface=${WIFI_INTERFACE}
bind-interfaces
dhcp-range=10.0.0.50,10.0.0.150,12h
EOF
}

_other_configuration() {
    sudo mv /etc/network/interfaces /etc/network/interfaces.bak
    sudo touch /etc/network/interfaces
    echo nohook wpa_supplicant | sudo tee -a "${AUTOHOTSPOT_DHCPD_CONF_FILE}"
}

_install_service_and_timer() {
    sudo cp "${INSTALLATION_PATH}"/resources/autohotspot/autohotspot.service /etc/systemd/system/autohotspot.service
    sudo systemctl enable autohotspot.service
    sudo cp "${INSTALLATION_PATH}"/resources/autohotspot/autohotspot.timer /etc/cron.d/autohotspot
}

_install_autohotspot_script() {
    sudo cp "${INSTALLATION_PATH}"/resources/autohotspot/autohotspot "${AUTOHOTSPOT_TARGET_PATH}"
    sudo chmod +x "${AUTOHOTSPOT_TARGET_PATH}"
}


_autohotspot_check () {
    echo "Check AutoHotspot Installation" | tee /dev/fd/3

    verify_apt_packages hostapd dnsmasq iw

    verify_service_enablement hostapd.service disabled
    verify_service_enablement dnsmasq.service disabled
    verify_service_enablement autohotspot.service enabled

    verify_files_exists "/etc/cron.d/autohotspot"
    verify_files_exists "${AUTOHOTSPOT_TARGET_PATH}"

    verify_file_contains_string "${WIFI_INTERFACE}" "${AUTOHOTSPOT_HOSTAPD_CONF_FILE}"
    verify_file_contains_string "${AUTOHOTSPOT_PASSWORD}" "${AUTOHOTSPOT_HOSTAPD_CONF_FILE}"
    verify_file_contains_string "${WIFI_REGION}" "${AUTOHOTSPOT_HOSTAPD_CONF_FILE}"
    verify_file_contains_string "${AUTOHOTSPOT_HOSTAPD_CONF_FILE}" "${AUTOHOTSPOT_HOSTAPD_DAEMON_CONF_FILE}"

    verify_file_contains_string "${WIFI_INTERFACE}" "${AUTOHOTSPOT_DNSMASQ_CONF_FILE}"
    verify_file_contains_string "nohook wpa_supplicant" "${AUTOHOTSPOT_DHCPD_CONF_FILE}"
}

setup_autohotspot() {
    if [ "$ENABLE_AUTOHOTSPOT" == true ] ; then
        echo "Install AutoHotspot functionality" | tee /dev/fd/3
        # inspired by
        # https://www.raspberryconnect.com/projects/65-raspberrypi-hotspot-accesspoints/158-raspberry-pi-auto-wifi-hotspot-switch-direct-connection

        _install_packages
        _get_interface
        _configure_hostapd
        _configure_dnsmasq
        _other_configuration
        _install_autohotspot_script
        _install_service_and_timer
        _autohotspot_check

        echo "DONE: setup_autohotspot"
    fi
}
