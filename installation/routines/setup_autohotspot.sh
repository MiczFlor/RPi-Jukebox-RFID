#!/usr/bin/env bash

_get_interface() {
    # interfaces may vary
    WIFI_INTERFACE=$(iw dev | grep "Interface"| awk '{ print $2 }')
    WIFI_REGION=$(iw reg get | grep country | awk '{ print $2}' | cut -d: -f1)
}


_install_packages() {
    sudo apt-get -y install hostapd dnsmasq

    # disable services. We want to start them manually
    sudo systemctl unmask hostapd
    sudo systemctl disable hostapd
    sudo systemctl disable dnsmasq
}

_configure_hostapd() {
    HOSTAPD_CUSTOM_FILE="${INSTALLATION_PATH}"/resources/autohotspot/hostapd.conf
    HOSTAPD_CONF_FILE="/etc/hostapd/hostapd.conf"
    sed -i "s/WIFI_INTERFACE/${WIFI_INTERFACE}/g" "${HOSTAPD_CUSTOM_FILE}"
    sed -i "s/AUTOHOTSPOT_PASSWORD/${AUTOHOTSPOT_PASSWORD}/g" "${HOSTAPD_CUSTOM_FILE}"
    sed -i "s/WIFI_REGION/${WIFI_REGION}/g" "${HOSTAPD_CUSTOM_FILE}"
    sudo cp "${HOSTAPD_CUSTOM_FILE}" "${HOSTAPD_CONF_FILE}"

    sudo sed -i "s@^#DAEMON_CONF=.*@DAEMON_CONF=\"${HOSTAPD_CONF_FILE}\"@g" /etc/default/hostapd
}

_configure_dnsmasq() {
    sudo tee -a /etc/dnsmasq.conf <<-EOF
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
    echo nohook wpa_supplicant | sudo tee -a /etc/dhcpcd.conf
}

_install_service_and_timer() {
    sudo cp "${INSTALLATION_PATH}"/resources/autohotspot/autohotspot.service /etc/systemd/system/autohotspot.service
    sudo systemctl enable autohotspot.service
    sudo cp "${INSTALLATION_PATH}"/resources/autohotspot/autohotspot.timer /etc/cron.d/autohotspot
}

_install_autohotspot_script() {
    TARGET_PATH="/usr/bin/autohotspot"
    sudo cp "${INSTALLATION_PATH}"/resources/autohotspot/autohotspot "${TARGET_PATH}"
    sudo chmod +x "${TARGET_PATH}"
}

setup_autohotspot() {
    echo "Install AutoHotspot functionality" | tee /dev/fd/3
    # inspired by
    # https://www.raspberryconnect.com/projects/65-raspberrypi-hotspot-accesspoints/158-raspberry-pi-auto-wifi-hotspot-switch-direct-connection

    _get_interface
    _install_packages
    _configure_hostapd
    _configure_dnsmasq
    _other_configuration
    _install_autohotspot_script
    _install_service_and_timer

    echo "DONE: setup_autohotspot"
}
