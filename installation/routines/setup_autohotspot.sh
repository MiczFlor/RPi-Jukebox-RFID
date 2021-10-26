#!/usr/bin/env bash

# Constants
interfaceWifi=wlan0
interfaceWired=eth0
ipAddress=192.168.99.1/24


_modify_wpa_supplicant() {
    echo "Inserting Accesspoint information into wpa_supplicant.conf"
    INPUT_FILE="${INSTALLATION_PATH}"/resources/autohotspot/wpa_supplicant-AP.conf
    WPA_FILE="/etc/wpa_supplicant/wpa_supplicant.conf"

    if [ "$AUTOHOTSPOT_CHANGE_PASSWORD" = true ]
    then
      sed -i "s/PlayItLoud\!/${AUTOHOTSPOT_PASSWORD}/g" "${INPUT_FILE}"
      echo "AUTOHOTSPOT_PASSWORD=${AUTOHOTSPOT_PASSWORD}"
    fi
    sudo awk '/^network=/{while((getline p<f)>0) print p}1' f=$INPUT_FILE $WPA_FILE | sudo tee $WPA_FILE
}

## Change over to systemd-networkd
## https://raspberrypi.stackexchange.com/questions/108592
_uninstall_classic_network() {
    echo "Deinstalling classic networking"
    sudo apt --autoremove -y purge ifupdown dhcpcd5 isc-dhcp-client isc-dhcp-common rsyslog
    sudo apt-mark hold ifupdown dhcpcd5 isc-dhcp-client isc-dhcp-common rsyslog raspberrypi-net-mods openresolv
    sudo rm -r /etc/network /etc/dhcp
}

_install_networkd() {
    echo "setup/enable systemd-resolved and systemd-networkd"
    sudo apt --autoremove -y purge avahi-daemon
    sudo apt-mark hold avahi-daemon libnss-mdns
    sudo apt install -y libnss-resolve
    sudo ln -sf /run/systemd/resolve/stub-resolv.conf /etc/resolv.conf
    sudo systemctl enable systemd-networkd.service systemd-resolved.service
}

_install_config_files() {
    echo "Install configuration files for systemd-networkd"
    sudo tee -a /etc/systemd/network/04-${interfaceWired}.network <<-EOF
    [Match]
    Name=$interfaceWired
    [Network]
    DHCP=yes
EOF

    sudo tee -a /etc/systemd/network/08-${interfaceWifi}-CLI.network <<-EOF
    [Match]
    Name=$interfaceWifi
    [Network]
    DHCP=yes
    LinkLocalAddressing=yes
    MulticastDNS=yes
EOF

    sudo tee -a /etc/systemd/network/12-${interfaceWifi}-AP.network <<-EOF
    [Match]
    Name=$interfaceWifi
    [Network]
    Address=$ipAddress
    IPForward=yes
    IPMasquerade=yes
    DHCPServer=yes
    LinkLocalAddressing=yes
    MulticastDNS=yes
    [DHCPServer]
    DNS=84.200.69.80 84.200.70.40 1.1.1.1
EOF
}

_install_control_script() {
    sudo cp "${INSTALLATION_PATH}"/resources/autohotspot/auto-hotspot /usr/local/sbin/
    sudo chmod +x /usr/local/sbin/auto-hotspot
}

_install_service() {
    echo "Install systemd-service to configure interface automatically"
    if [ ! -f /etc/systemd/system/wpa_cli@${interfaceWifi}.service ] ; then
        sudo tee -a /etc/systemd/system/wpa_cli@${interfaceWifi}.service <<-EOF
    [Unit]
    Description=Wpa_cli to Automatically Create an Accesspoint if no Client Connection is Available
    After=wpa_supplicant@%i.service
    BindsTo=wpa_supplicant@%i.service
    [Service]
    ExecStart=/sbin/wpa_cli -i %I -a /usr/local/sbin/auto-hotspot
    Restart=on-failure
    RestartSec=1
    [Install]
    WantedBy=multi-user.target
EOF
    else
      echo "wpa_cli@$interfaceWifi.service is already installed"
    fi

    sudo systemctl daemon-reload
    sudo systemctl enable wpa_cli@${interfaceWifi}.service
}


setup_autohotspot() {
    echo "Install AutoHotspot functionality" | tee /dev/fd/3
    # copied from https://github.com/0unknwn/auto-hotspot

    _modify_wpa_supplicant
    _uninstall_classic_network
    _install_networkd
    _install_config_files
    _install_control_script
    _install_service

    echo "DONE: setup_autohotspot"
}
