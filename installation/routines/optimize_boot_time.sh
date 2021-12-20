#!/usr/bin/env bash

# Reference: https://panther.software/configuration-code/raspberry-pi-3-4-faster-boot-time-in-few-easy-steps/

_optimize_disable_irrelevant_services() {
  echo "  * Disable keyboard-setup.service"
  sudo systemctl disable keyboard-setup.service

  echo "  * Disable triggerhappy.service"
  sudo systemctl disable triggerhappy.service
  sudo systemctl disable triggerhappy.socket

  echo "  * Disable raspi-config.service"
  sudo systemctl disable raspi-config.service

  echo "  * Disable apt-daily.service & apt-daily-upgrade.service"
  sudo systemctl disable apt-daily.service
  sudo systemctl disable apt-daily-upgrade.service
  sudo systemctl disable apt-daily.timer
  sudo systemctl disable apt-daily-upgrade.timer
}

# TODO: If false, actually make sure bluetooth is enabled
_optimize_handle_bluetooth() {
  if [ "$DISABLE_BLUETOOTH" = true ] ; then
    echo "  * Disable hciuart.service and bluetooth"
    sudo systemctl disable hciuart.service
    sudo systemctl disable bluetooth.service
  fi
}

# TODO: Allow options to enable/disable wifi, Dynamic/Static IP etc.
_optimize_handle_network_connection() {
  # Static IP Address and DHCP optimizations
  local DHCP_CONF="/etc/dhcpcd.conf"

  if [ "$ENABLE_STATIC_IP" = true ] ; then
    echo "  * Set static IP address" | tee /dev/fd/3
    if grep -q "## Jukebox DHCP Config" "$DHCP_CONF"; then
      echo "    Skipping. Already set up!" | tee /dev/fd/3
    else
      # DHCP has not been configured
      # Reference: https://unix.stackexchange.com/a/307790/478030
      INTERFACE=$(route | grep '^default' | grep -o '[^ ]*$')

      # Reference: https://serverfault.com/a/31179/431930
      GATEWAY=$(route -n | grep 'UG[ \t]' | awk '{print $2}')

      # Using the dynamically assigned IP address as it is the best guess to be free
      # Reference: https://unix.stackexchange.com/a/48254/478030
      CURRENT_IP_ADDRESS=$(hostname -I)
      echo "    * ${INTERFACE} is the default network interface" | tee /dev/fd/3
      echo "    * ${GATEWAY} is the Router Gateway address" | tee /dev/fd/3
      echo "    * Using ${CURRENT_IP_ADDRESS} as the static IP for now" | tee /dev/fd/3

      sudo tee -a $DHCP_CONF <<-EOF

## Jukebox DHCP Config
interface ${INTERFACE}
static ip_address=${CURRENT_IP_ADDRESS}/24
static routers=${GATEWAY}
static domain_name_servers=${GATEWAY}

EOF

    fi
  else
    echo "  * Skipped static IP address"
  fi
}

# TODO: Allow both Enable and Disable
_optimize_ipv6_arp() {
  if [ "$DISABLE_IPv6" = true ] ; then
      echo "  * Disabling IPV6 and ARP"
      sudo tee -a $DHCP_CONF <<-EOF

## Jukebox boot speed-up settings
noarp
ipv4only
noipv6

EOF

  fi
}

# TODO: Allow both Enable and Disable
_optimize_handle_boot_screen() {
  if [ "$DISABLE_BOOT_SCREEN" = true ] ; then
    echo "  * Disable RPi rainbow screen"
    BOOT_CONFIG='/boot/config.txt'
    sudo tee -a $BOOT_CONFIG <<-EOF

## Jukebox Settings
disable_splash=1

EOF
  fi
}

# TODO: Allow both Enable and Disable
_optimize_handle_boot_logs() {
  if [ "$DISABLE_BOOT_LOGS_PRINT" = true ] ; then
    echo "  * Disable boot logs"
    BOOT_CMDLINE='/boot/cmdline.txt'
    sudo sed -i "$ s/$/ consoleblank=1 logo.nologo quiet loglevel=0 plymouth.enable=0 vt.global_cursor_default=0 plymouth.ignore-serial-consoles splash fastboot noatime nodiratime noram/" $BOOT_CMDLINE
  fi
}

optimize_boot_time() {
  echo "Optimize boot time" | tee /dev/fd/3

  _optimize_disable_irrelevant_services
  _optimize_handle_bluetooth
  _optimize_handle_network_connection
  _optimize_ipv6_arp
  _optimize_handle_boot_screen
  _optimize_handle_boot_logs

  echo "DONE: optimize_boot_time"
}
