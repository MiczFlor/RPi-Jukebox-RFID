#!/usr/bin/env bash

JUKEBOX_HOME_DIR="$1"
AUTOHOTSPOTconfig="$2"
AUTOHOTSPOTssid="$3"
AUTOHOTSPOTcountryCode="$4"
AUTOHOTSPOTpass="$5"
AUTOHOTSPOTip="$6"
if [[ "$#" -lt 2 || ( "${AUTOHOTSPOTconfig}" != "NO" && "${AUTOHOTSPOTconfig}" != "YES") || ( "${AUTOHOTSPOTconfig}" == "YES" && "$#" -ne 6 ) ]] ; then
    echo "error: missing paramter"
    echo "usage: ./setup_autohotspot.sh <jukeboxDir> <activation=YES> <ssid> <countryCode (e.g. DE, GB, CZ, ...)> <password (8..63 characters)> <ipAdress>"
    echo "or"
    echo "usage: ./setup_autohotspot.sh <jukeboxDir> <activation=NO>"
    exit 1
fi


apt_get="sudo apt-get -qq --yes"

systemd_dir="/etc/systemd/system"

autohotspot_service="autohotspot.service"
autohotspot_service_path="${systemd_dir}/${autohotspot_service}"
autohotspot_script="/usr/bin/autohotspot"

dnsmasq_conf=/etc/dnsmasq.conf
hostapd_conf=/etc/hostapd/hostapd.conf
hostapd_deamon=/etc/default/hostapd
dhcpcd_conf=/etc/dhcpcd.conf
dhcpcd_conf_nohook_wpa_supplicant="nohook wpa_supplicant"

if [ "${AUTOHOTSPOTconfig}" == "YES" ]; then

    # adapted from https://www.raspberryconnect.com/projects/65-raspberrypi-hotspot-accesspoints/158-raspberry-pi-auto-wifi-hotspot-switch-direct-connection

    # power management of wifi: switch off to avoid disconnecting
    sudo iwconfig wlan0 power off

    # required packages
    ${apt_get} install dnsmasq hostapd iw
    sudo systemctl unmask hostapd
    sudo systemctl disable hostapd
    sudo systemctl stop hostapd
    sudo systemctl unmask dnsmasq
    sudo systemctl disable dnsmasq
    sudo systemctl stop dnsmasq

    # configure DNS
    # create flag file or copy present conf to orig file
    # to correctly handling future deactivation of autohotspot
    if [ ! -f "${dnsmasq_conf}" ]; then
        sudo touch "${dnsmasq_conf}.remove"
    elif [ ! -f "${dnsmasq_conf}.orig" ] && [ ! -f "${dnsmasq_conf}.remove" ]; then
        sudo cp "${dnsmasq_conf}" "${dnsmasq_conf}.orig"
    fi

    ip_without_last_segment=$(echo $AUTOHOTSPOTip | cut -d'.' -f1-3)
    sudo cp "${JUKEBOX_HOME_DIR}"/misc/sampleconfigs/dnsmasq.conf.stretch-default2-Hotspot.sample "${dnsmasq_conf}"
    sudo sed -i "s|%IP_WITHOUT_LAST_SEGMENT%|${ip_without_last_segment}|g" "${dnsmasq_conf}"
    sudo chown root:root "${dnsmasq_conf}"
    sudo chmod 644 "${dnsmasq_conf}"

    # configure hostapd conf
    # create flag file or copy present conf to orig file
    # to correctly handling future deactivation of autohotspot
    if [ ! -f "${hostapd_conf}" ]; then
        sudo touch "${hostapd_conf}.remove"
    elif [ ! -f "${hostapd_conf}.orig" ] && [ ! -f "${hostapd_conf}.remove" ]; then
        sudo cp "${hostapd_conf}" "${hostapd_conf}.orig"
    fi

    sudo cp "${JUKEBOX_HOME_DIR}"/misc/sampleconfigs/hostapd.conf.stretch-default2-Hotspot.sample "${hostapd_conf}"
    sudo sed -i "s|%AUTOHOTSPOTssid%|${AUTOHOTSPOTssid}|g" "${hostapd_conf}"
    sudo sed -i "s|%AUTOHOTSPOTpass%|${AUTOHOTSPOTpass}|g" "${hostapd_conf}"
    sudo sed -i "s|%AUTOHOTSPOTcountryCode%|${AUTOHOTSPOTcountryCode}|g" "${hostapd_conf}"
    sudo chown root:root "${hostapd_conf}"
    sudo chmod 644 "${hostapd_conf}"

    # configure hostapd daemon
    # create flag file or copy present conf to orig file
    # to correctly handling future deactivation of autohotspot
    if [ ! -f "${hostapd_deamon}" ]; then
        sudo touch "${hostapd_deamon}.remove"
    elif [ ! -f "${hostapd_deamon}.orig" ] && [ ! -f "${hostapd_deamon}.remove" ]; then
        sudo cp "${hostapd_deamon}" "${hostapd_deamon}.orig"
    fi

    sudo cp "${JUKEBOX_HOME_DIR}"/misc/sampleconfigs/hostapd.stretch-default2-Hotspot.sample "${hostapd_deamon}"
    sudo sed -i "s|%HOSTAPD_CONF%|${hostapd_conf}|g" "${hostapd_deamon}"
    sudo chown root:root "${hostapd_deamon}"
    sudo chmod 644 "${hostapd_deamon}"

    # configure dhcpcd conf
    # create flag file or copy present conf to orig file
    # to correctly handling future deactivation of autohotspot
    if [ ! -f "${dhcpcd_conf}" ]; then
        sudo touch "${dhcpcd_conf}.remove"
        sudo touch "${dhcpcd_conf}"
        sudo chown root:netdev "${dhcpcd_conf}"
        sudo chmod 664 "${dhcpcd_conf}"
    elif [ ! -f "${dhcpcd_conf}.orig" ] && [ ! -f "${dhcpcd_conf}.remove" ]; then
        sudo cp "${dhcpcd_conf}" "${dhcpcd_conf}.orig"
    fi

    if [[ ! $(grep -w "${dhcpcd_conf_nohook_wpa_supplicant}" ${dhcpcd_conf}) ]]; then
        sudo bash -c "echo ${dhcpcd_conf_nohook_wpa_supplicant} >> ${dhcpcd_conf}"
    fi

    # create service to trigger hotspot
    sudo cp "${JUKEBOX_HOME_DIR}"/misc/sampleconfigs/autohotspot.sh.stretch-default2-Hotspot.sample "${autohotspot_script}"
    sudo sed -i "s|%AUTOHOTSPOT_IP%|${AUTOHOTSPOTip}|g" "${autohotspot_script}"
    sudo chmod +x "${autohotspot_script}"

    sudo cp "${JUKEBOX_HOME_DIR}"/misc/sampleconfigs/autohotspot.service.stretch-default2-Hotspot.sample "${autohotspot_service_path}"
    sudo sed -i "s|%AUTOHOTSPOT_SCRIPT%|${autohotspot_script}|g" "${autohotspot_service_path}"
    sudo chown root:root "${autohotspot_service_path}"
    sudo chmod 644 "${autohotspot_service_path}"

    sudo systemctl enable "${autohotspot_service}"

    # create crontab entry
    crontab_user=$(crontab -l 2>/dev/null)
    if [[ -z "${crontab_user}" || ! $(echo "${crontab_user}" | grep -w "${autohotspot_script}") ]]; then
        (echo "${crontab_user}"; echo "*/5 * * * * sudo ${autohotspot_script} >/dev/null 2>&1") | crontab -
    fi

else
    # clear autohotspot configurations made from past installation

    # stop services and clear services
    if systemctl list-unit-files "${autohotspot_service}" >/dev/null 2>&1 ; then
        sudo systemctl stop hostapd
        sudo systemctl stop dnsmasq
        sudo systemctl stop "${autohotspot_service}"
        sudo systemctl disable "${autohotspot_service}"
        sudo rm "${autohotspot_service_path}"
    fi

    # remove crontab entry and script
    crontab_user=$(crontab -l 2>/dev/null)
    if [[ ! -z "${crontab_user}" && $(echo "${crontab_user}" | grep -w "${autohotspot_script}") ]]; then
        echo "${crontab_user}" | sed "s|^.*\s${autohotspot_script}\s.*$||g" | crontab -
    fi

    if [ -f "${autohotspot_script}" ]; then
        sudo rm "${autohotspot_script}"
    fi

    # remove config files
    if [ -f "${dnsmasq_conf}.remove" ]; then
        sudo rm "${dnsmasq_conf}.remove" "${dnsmasq_conf}"
    elif [ -f "${dnsmasq_conf}.orig" ]; then
        sudo mv "${dnsmasq_conf}.orig" "${dnsmasq_conf}"
    fi
    if [ -f "${hostapd_conf}.remove" ]; then
        sudo rm "${hostapd_conf}.remove" "${hostapd_conf}"
    elif [ -f "${hostapd_conf}.orig" ]; then
        sudo mv "${hostapd_conf}.orig" "${hostapd_conf}"
    fi
    if [ -f "${hostapd_deamon}.remove" ]; then
        sudo rm "${hostapd_deamon}.remove" "${hostapd_deamon}"
    elif [ -f "${hostapd_deamon}.orig" ]; then
        sudo mv "${hostapd_deamon}.orig" "${hostapd_deamon}"
    fi
    if [ -f "${dhcpcd_conf}.remove" ]; then
        sudo rm "${dhcpcd_conf}.remove" "${dhcpcd_conf}"
    elif [ -f "${dhcpcd_conf}.orig" ]; then
        sudo mv "${dhcpcd_conf}.orig" "${dhcpcd_conf}"
    fi
fi
