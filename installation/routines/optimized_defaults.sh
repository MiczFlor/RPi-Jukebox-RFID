#!/usr/bin/env bash

# Reference: https://panther.software/configuration-code/raspberry-pi-3-4-faster-boot-time-in-few-easy-steps/

# TODO: Allow options to enable/disable wifi, Dynamic/Static IP etc.
_optimize_static_ip() {
  # Static IP Address and DHCP optimizations
  if [ "$ENABLE_STATIC_IP" = true ] ; then
    ./../options/static_ip.sh enable
  else
    ./../options/static_ip.sh disable
  fi
}

_optimize_ipv6_arp() {
  if [ "$DISABLE_IPv6" = true ] ; then
    ./../options/ipv6.sh disable
  fi
}

_run_optimized_defaults() {
    # Source: https://raspberrypi.stackexchange.com/a/66939
    # Autologin
    log "Enable Autologin for user"
    sudo raspi-config nonint do_boot_behaviour B2
    # Wait for network at boot
    # log "Enable 'Wait for network at boot'"
    # sudo raspi-config nonint do_boot_wait 1
    # power management of wifi: switch off to avoid disconnecting
    log "Disable Wifi power management to avoid disconnecting"
    sudo iwconfig wlan0 power off

    ./../options/systemctl_services.sh disable
    ./../options/bluetooth.sh disable
    ./../options/boot_screen.sh disable
    ./../options/boot_logs.sh disable
    ./../options/ssh_qos.sh disable

    _optimize_static_ip
    _optimize_ipv6_arp
}

optimized_defaults() {
    run_with_log_frame _run_optimized_defaults "Optimize boot time and system settings"
}
