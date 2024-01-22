#!/usr/bin/env bash

# Reference: https://panther.software/configuration-code/raspberry-pi-3-4-faster-boot-time-in-few-easy-steps/

_optimize_disable_irrelevant_services() {
  ./../options/systemctl_services.sh disable
}

_optimize_handle_bluetooth() {
  if [ "$DISABLE_BLUETOOTH" = true ] ; then
    ./../options/bluetooth.sh disable
  fi
}

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

_optimize_handle_boot_screen() {
  if [ "$DISABLE_BOOT_SCREEN" = true ] ; then
    ./../options/boot_screen.sh disable
  fi
}

_optimize_handle_boot_logs() {
  if [ "$DISABLE_BOOT_LOGS_PRINT" = true ] ; then
    ./../options/boot_logs.sh disable
  fi
}

_run_optimize_boot_time() {
    _optimize_disable_irrelevant_services
    _optimize_handle_bluetooth
    _optimize_static_ip
    _optimize_ipv6_arp
    _optimize_handle_boot_screen
    _optimize_handle_boot_logs
    _optimize_check
}

optimize_boot_time() {
    run_with_log_frame _run_optimize_boot_time "Optimize boot time"
}
