#!/usr/bin/env bash

# Reference: https://panther.software/configuration-code/raspberry-pi-3-4-faster-boot-time-in-few-easy-steps/

OPTIMIZE_DHCP_CONF="/etc/dhcpcd.conf"
OPTIMIZE_BOOT_CMDLINE_OPTIONS="consoleblank=1 logo.nologo quiet loglevel=0 plymouth.enable=0 vt.global_cursor_default=0 plymouth.ignore-serial-consoles splash fastboot noatime nodiratime noram"
OPTIMIZE_BOOT_CMDLINE_OPTIONS_IPV6="ipv6.disable=1"
OPTIMIZE_DHCP_CONF_HEADER="## Jukebox DHCP Config"
OPTIMIZE_BOOT_CONF_HEADER="## Jukebox Boot Config"

_optimize_disable_irrelevant_services() {
  log "  Disable keyboard-setup.service"
  sudo systemctl disable keyboard-setup.service

  log "  Disable triggerhappy.service"
  sudo systemctl disable triggerhappy.service
  sudo systemctl disable triggerhappy.socket

  log "  Disable raspi-config.service"
  sudo systemctl disable raspi-config.service

  log "  Disable apt-daily.service & apt-daily-upgrade.service"
  sudo systemctl disable apt-daily.service
  sudo systemctl disable apt-daily-upgrade.service
  sudo systemctl disable apt-daily.timer
  sudo systemctl disable apt-daily-upgrade.timer
}

_add_options_to_cmdline() {
    local options="$1"

    local cmdlineFile="${RPI_BOOT_CMDLINE_FILE}"
    if [ ! -s "${cmdlineFile}" ];then
        sudo tee "${cmdlineFile}" <<-EOF
${options}
EOF
    else
        for option in $options
        do
            if ! grep -qiw "$option" "${cmdlineFile}" ; then
                sudo sed -i "s/$/ $option/" "${cmdlineFile}"
            fi
        done
    fi
}

# TODO: If false, actually make sure bluetooth is enabled
_optimize_handle_bluetooth() {
  if [ "$DISABLE_BLUETOOTH" = true ] ; then
    print_lc "  Disable bluetooth"
    sudo systemctl disable hciuart.service
    sudo systemctl disable bluetooth.service
  fi
}

# TODO: Allow options to enable/disable wifi, Dynamic/Static IP etc.
_optimize_static_ip() {
    # Static IP Address and DHCP optimizations
    if [[ $(is_dhcpcd_enabled) == true ]]; then
        if [ "$ENABLE_STATIC_IP" = true ] ; then
            print_lc "  Set static IP address"
            if grep -q "${OPTIMIZE_DHCP_CONF_HEADER}" "$OPTIMIZE_DHCP_CONF"; then
                log "    Skipping. Already set up!"
            else
                # DHCP has not been configured
                log "    ${CURRENT_INTERFACE} is the default network interface"
                log "    ${CURRENT_GATEWAY} is the Router Gateway address"
                log "    Using ${CURRENT_IP_ADDRESS} as the static IP for now"

                sudo tee -a $OPTIMIZE_DHCP_CONF <<-EOF

${OPTIMIZE_DHCP_CONF_HEADER}
interface ${CURRENT_INTERFACE}
static ip_address=${CURRENT_IP_ADDRESS}/24
static routers=${CURRENT_GATEWAY}
static domain_name_servers=${CURRENT_GATEWAY}
noarp

EOF

            fi
        fi
    fi
}

# TODO: Allow both Enable and Disable
# Disable ipv6 thoroughly on the system with kernel parameter
_optimize_ipv6_arp() {
    if [ "$DISABLE_IPv6" = true ] ; then
        print_lc "  Disabling IPV6"
        _add_options_to_cmdline "${OPTIMIZE_BOOT_CMDLINE_OPTIONS_IPV6}"
    fi
}

# TODO: Allow both Enable and Disable
_optimize_handle_boot_screen() {
  if [ "$DISABLE_BOOT_SCREEN" = true ] ; then
    log "  Disable RPi rainbow screen"
    if grep -q "${OPTIMIZE_BOOT_CONF_HEADER}" "$RPI_BOOT_CONFIG_FILE"; then
      log "    Skipping. Already set up!"
    else
      sudo tee -a $RPI_BOOT_CONFIG_FILE <<-EOF

${OPTIMIZE_BOOT_CONF_HEADER}
disable_splash=1

EOF
    fi
  fi
}

# TODO: Allow both Enable and Disable
_optimize_handle_boot_logs() {
  if [ "$DISABLE_BOOT_LOGS_PRINT" = true ] ; then
    log "  Disable boot logs"

    _add_options_to_cmdline "${OPTIMIZE_BOOT_CMDLINE_OPTIONS}"
  fi
}

get_nm_active_profile()
{
	local active_profile=$(nmcli -g DEVICE,CONNECTION device status | grep "^${CURRENT_INTERFACE}" | cut -d':' -f2)
	echo "$active_profile"
}

_optimize_static_ip_NetworkManager() {
    if [[ $(is_NetworkManager_enabled) == true ]]; then
        if [ "$ENABLE_STATIC_IP" = true ] ; then
            print_lc "  Set static IP address"
            log "    ${CURRENT_INTERFACE} is the default network interface"
            log "    ${CURRENT_GATEWAY} is the Router Gateway address"
            log "    Using ${CURRENT_IP_ADDRESS} as the static IP for now"
            local active_profile=$(get_nm_active_profile)
            sudo nmcli connection modify "$active_profile" ipv4.method manual ipv4.address "${CURRENT_IP_ADDRESS}/24" ipv4.gateway "$CURRENT_GATEWAY" ipv4.dns "$CURRENT_GATEWAY"
        #else
            # for future deactivation
            #sudo nmcli connection modify "$active_profile" ipv4.method auto ipv4.address "" ipv4.gateway "" ipv4.dns ""
        fi
    fi
}


_optimize_check() {
    print_verify_installation

    verify_optional_service_enablement keyboard-setup.service disabled
    verify_optional_service_enablement triggerhappy.service disabled
    verify_optional_service_enablement triggerhappy.socket disabled
    verify_optional_service_enablement raspi-config.service disabled
    verify_optional_service_enablement apt-daily.service disabled
    verify_optional_service_enablement apt-daily-upgrade.service disabled
    verify_optional_service_enablement apt-daily.timer disabled
    verify_optional_service_enablement apt-daily-upgrade.timer disabled

    if [ "$DISABLE_BLUETOOTH" = true ] ; then
        verify_optional_service_enablement hciuart.service disabled
        verify_optional_service_enablement bluetooth.service disabled
    fi

    if [ "$ENABLE_STATIC_IP" = true ] ; then
        if [[ $(is_dhcpcd_enabled) == true ]]; then
            verify_file_contains_string_once "${OPTIMIZE_DHCP_CONF_HEADER}" "${OPTIMIZE_DHCP_CONF}"
            verify_file_contains_string "${CURRENT_INTERFACE}" "${OPTIMIZE_DHCP_CONF}"
            verify_file_contains_string "${CURRENT_IP_ADDRESS}" "${OPTIMIZE_DHCP_CONF}"
            verify_file_contains_string "${CURRENT_GATEWAY}" "${OPTIMIZE_DHCP_CONF}"
        fi

        if [[ $(is_NetworkManager_enabled) == true ]]; then
            local active_profile=$(get_nm_active_profile)
            local active_profile_path="/etc/NetworkManager/system-connections/${active_profile}.nmconnection"
            verify_files_exists "${active_profile_path}"
            verify_file_contains_string "${CURRENT_IP_ADDRESS}" "${active_profile_path}"
            verify_file_contains_string "${CURRENT_GATEWAY}" "${active_profile_path}"
        fi
    fi
    if [ "$DISABLE_IPv6" = true ] ; then
        verify_file_contains_string_once "${OPTIMIZE_BOOT_CMDLINE_OPTIONS_IPV6}" "${RPI_BOOT_CMDLINE_FILE}"
    fi
    if [ "$DISABLE_BOOT_SCREEN" = true ] ; then
        verify_file_contains_string_once "${OPTIMIZE_BOOT_CONF_HEADER}" "${RPI_BOOT_CONFIG_FILE}"
    fi

    if [ "$DISABLE_BOOT_LOGS_PRINT" = true ] ; then
        for option in $OPTIMIZE_BOOT_CMDLINE_OPTIONS
        do
            verify_file_contains_string_once $option "${RPI_BOOT_CMDLINE_FILE}"
        done
    fi
}

_run_optimize_boot_time() {
    _optimize_disable_irrelevant_services
    _optimize_handle_bluetooth
    _optimize_static_ip
    _optimize_static_ip_NetworkManager
    _optimize_ipv6_arp
    _optimize_handle_boot_screen
    _optimize_handle_boot_logs
    _optimize_check
}

optimize_boot_time() {
    run_with_log_frame _run_optimize_boot_time "Optimize boot time"
}
