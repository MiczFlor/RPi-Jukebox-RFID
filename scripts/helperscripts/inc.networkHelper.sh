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
    if [[ $(is_service_enabled "dhcpcd.service") == true || "${CI_TEST_DHCPCD}" == true ]]; then
        echo true
    else
        echo false
    fi
}

is_NetworkManager_enabled() {
    if [[ $(is_service_enabled "NetworkManager.service") == true || "${CI_TEST_NETWORKMANAGER}" == true ]]; then
        echo true
    else
        echo false
    fi
}

WPA_CONF="/etc/wpa_supplicant/wpa_supplicant.conf"
clear_wireless_networks() {
    if [[ $(is_dhcpcd_enabled) == true ]]; then
        sudo sed -i -e '/^[[:space:]]*$/d' -e '/^network={/,/^}/d' $WPA_CONF
    fi

    if [[ $(is_NetworkManager_enabled) == true ]]; then
        nmcli -g UUID,TYPE,ACTIVE connection show | grep  "^.*:.*:no$" | grep -F "wireless" | cut -d : -f 1 | \
            while read uuid; do sudo nmcli connection delete "$uuid"; done
    fi
}

_get_passphrase_for_config() {
    local ssid="$1"
    local pass="$2"
    if [[ "${#pass}" -lt 64 ]]; then
        pass=$(wpa_passphrase "$ssid" "$pass" | grep -vF '#psk' | grep -F "psk=" | cut -d = -f 2)
    fi
    echo $pass
}

add_wireless_network() {
    local interface="$1"
    local ssid="$2"
    local pass="$3"
    local prio="$4"

    pass=$(_get_passphrase_for_config "$ssid" "$pass")

    if [[ $(is_dhcpcd_enabled) == true ]]; then
        if ! sudo cat "$WPA_CONF" | grep -qF "ssid=\"${ssid}\"" ; then
            local wpa_network_with_dummy_psk=$(wpa_passphrase "$ssid" "dummypsk")
            if echo "$wpa_network_with_dummy_psk" | grep -qF 'network='; then
                local wpa_network=$(echo "$wpa_network_with_dummy_psk" | sed -e '/#psk/d' -e "s/psk=.*$/psk=${pass}/" -e "/^}/i\\\tpriority=${prio}" )
                sudo bash -c "echo '${wpa_network}' >> $WPA_CONF"
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

# gets the configured wireless networks. Returns an array with the format "ssid:pass:prio ssid:pass:prio".
get_wireless_networks() {
    networks=()

    if [[ $(is_dhcpcd_enabled) == true ]]; then
        local wpa_networks=$(sudo sed '/^network={/,/^}/!d' $WPA_CONF)
        local wpa_networks_perline=$(echo "${wpa_networks//$'\n'/\\n}" | sed -e 's/[[:space:]]//g' -e 's/\\nnetwork=/\nnetwork=/g')
        for wpa_network in $wpa_networks_perline
        do
            local wpa_network_multiline="${wpa_network//\\n/$'\n'}"
            local ssid=$(echo "$wpa_network_multiline" | grep -F "ssid=" | cut -d = -f 2 | tr -d '"')
            local pass=$(echo "$wpa_network_multiline" | grep -F "psk=" | cut -d = -f 2)
            local prio=$(echo "$wpa_network_multiline" | grep -F "priority=" | cut -d = -f 2)

            networks+=("$ssid":"$pass":"$prio")
        done
    fi

    if [[ $(is_NetworkManager_enabled) == true ]]; then
        local network_profiles=$(nmcli -g UUID,TYPE connection show | grep -F "wireless" | cut -d : -f 1)

        for network_profile in $network_profiles
        do
            local result=$(sudo nmcli --show-secrets -t -f 802-11-wireless.ssid,802-11-wireless-security.psk,connection.autoconnect-priority con show $network_profile)
            local ssid=$(echo "$result" | grep -F "802-11-wireless.ssid" | cut -d : -f 2)
            local pass=$(echo "$result" | grep -F "802-11-wireless-security.psk" | cut -d : -f 2)
            local prio=$(echo "$result" | grep -F "connection.autoconnect-priority" | cut -d : -f 2)

            networks+=("$ssid":"$pass":"$prio")
        done
    fi

    echo "${networks[@]}"
}
