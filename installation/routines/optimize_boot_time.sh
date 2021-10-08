#!/usr/bin/env bash

optimize_boot_time() {
  local time_start=$(date +%s)

  # Reference: https://panther.software/configuration-code/raspberry-pi-3-4-faster-boot-time-in-few-easy-steps/
  echo "Optimize boot time" | tee /dev/fd/3

  echo "  * Disable exim4.service" | tee /dev/fd/3
  sudo systemctl disable exim4.service

  if [ "$DISABLE_BLUETOOTH" = true ] ; then
    echo "  * Disable hciuart.service and bluetooth" | tee /dev/fd/3
    sudo systemctl disable hciuart.service
    sudo systemctl disable bluetooth.service
  fi

  echo "  * Disable keyboard-setup.service" | tee /dev/fd/3
  sudo systemctl disable keyboard-setup.service

  echo "  * Disable triggerhappy.service" | tee /dev/fd/3
  sudo systemctl disable triggerhappy.service
  sudo systemctl disable triggerhappy.socket

  echo "  * Disable raspi-config.service" | tee /dev/fd/3
  sudo systemctl disable raspi-config.service

  echo "  * Disable apt-daily.service & apt-daily-upgrade.service" | tee /dev/fd/3
  sudo systemctl disable apt-daily.service
  sudo systemctl disable apt-daily-upgrade.service
  sudo systemctl disable apt-daily.timer
  sudo systemctl disable apt-daily-upgrade.timer

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

      cat << EOF | sudo tee -a $DHCP_CONF

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

  # Disable IPv6 and ARP
  if [ "$DISABLE_IPv6" = true ] ; then
      echo "  * Disabling IPV6 and ARP" | tee /dev/fd/3
      cat << EOF | sudo tee -a $DHCP_CONF

## Jukebox boot speed-up settings
noarp
ipv4only
noipv6

EOF

  fi

  # Disable RPi rainbow screen
  if [ "$DISABLE_BOOT_SCREEN" = true ] ; then
    echo "  * Disable RPi rainbow screen" | tee /dev/fd/3
    BOOT_CONFIG='/boot/config.txt'
    cat << EOF | sudo tee -a $BOOT_CONFIG

## Jukebox Settings
disable_splash=1

EOF
  fi

  # Disable boot logs
  if [ "$DISABLE_BOOT_LOGS_PRINT" = true ] ; then
    echo "  * Disable boot logs" | tee /dev/fd/3
    BOOT_CMDLINE='/boot/cmdline.txt'
    sudo sed -i "$ s/$/ consoleblank=1 logo.nologo quiet loglevel=0 plymouth.enable=0 vt.global_cursor_default=0 plymouth.ignore-serial-consoles splash fastboot noatime nodiratime noram/" $BOOT_CMDLINE
  fi


  calc_runtime_and_print time_start $(date +%s)
  echo "DONE: optimize_boot_time"
}
