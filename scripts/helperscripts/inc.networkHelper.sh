_get_service_enablement() {
    local service="$1"
    local option="${2:+$2 }" # optional, dont't quote in 'systemctl' call!

    if [[ -z "${service}" ]]; then
        echo "ERROR: at least one parameter value is missing!"
        exit 1
    fi

    local actual_enablement=$(systemctl is-enabled ${option}${service} 2>/dev/null)

    echo "$actual_enablement"
}

is_service_enabled() {
    local service="$1"
    local option="$2"
    local actual_enablement=$(_get_service_enablement $service $option)

    if [[ "$actual_enablement" == "enabled" ]]; then
        echo true
    else
        echo false
    fi
}

is_dhcpcd_enabled() {
    echo $(is_service_enabled "dhcpcd.service")
}

is_NetworkManager_enabled() {
    echo $(is_service_enabled "NetworkManager.service")
}

WPA_CONF="/etc/wpa_supplicant/wpa_supplicant.conf"
clear_wireless_networks() {
    if [[ $(is_dhcpcd_enabled) == true ]]; then
        sudo sed -i '/^network={/,/^}/ d' $WPA_CONF
    fi

    if [[ $(is_NetworkManager_enabled) == true ]]; then
        nmcli -g NAME,TYPE connection show | grep -F "wireless" | cut -d : -f 1 | \
            while read name; do sudo nmcli connection delete "$name"; done
    fi
}

add_wireless_network() {
    local interface="$1"
    local ssid="$2"
    local pass="$3"
    local prio="$4"
    if [[ $(is_dhcpcd_enabled) == true ]]; then
        if ! sudo cat "$WPA_CONF" | grep -qF "ssid=\"${ssid}\"" ; then
            local wpa_network=$(wpa_passphrase $ssid $pass)
            if echo "$wpa_network" | grep -qF 'network='; then
                wpa_network=$(echo "$wpa_network" | grep -v -F '#psk' | sed "/^}/i\\\tpriority=${prio}" )
                sudo bash -c "echo '${wpa_network}' >> $WPA_CONF"
            else
                echo "Error while adding network config."
            fi
        fi
    fi

    if [[ $(is_NetworkManager_enabled) == true ]]; then
        if ! nmcli -g NAME,TYPE connection show | grep -F "wireless" | grep -qwF "$ssid"; then
            sudo nmcli connection add type wifi con-name "$ssid" ifname "$interface" autoconnect yes mode infrastructure ssid "$ssid"
            sudo nmcli connection modify "$ssid" wifi-sec.key-mgmt wpa-psk wifi-sec.psk "$pass" conn.autoconnect-p "$prio"
        fi
    fi
}

