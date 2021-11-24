#!/usr/bin/env bash

_option_static_ip() {
  # ENABLE_STATIC_IP
  CURRENT_IP_ADDRESS=$(hostname -I)
  echo "Would you like to set a static IP (will be ${CURRENT_IP_ADDRESS})?
It'll save a lot of start up time. This can be changed later.
[Y/n] " 1>&3
  read -r response
  case "$response" in
    [nN][oO]|[nN])
      ENABLE_STATIC_IP=false
      ;;
    *)
      ;;
  esac
  echo "ENABLE_STATIC_IP=${ENABLE_STATIC_IP}"
}

_option_ipv6() {
  # DISABLE_IPv6
  echo "Do you want to disable IPv6? [Y/n] " 1>&3
  read -r response
  case "$response" in
    [nN][oO]|[nN])
      DISABLE_IPv6=false
      ;;
    *)
      ;;
  esac
  echo "DISABLE_IPv6=${DISABLE_IPv6}"
}

_option_autohotspot() {
  # ENABLE_AUTOHOTSPOT
  echo "Do you want to enable a WiFi hotspot on demand?
When enabled, this service spins up a WiFi hotspot 
when the Phonbox is unable to connect to a known
WiFi. This way you can still access it.
[y/N] " 1>&3
  read -r response
  case "$response" in
    [yY])
      ENABLE_AUTOHOTSPOT=true
      ;;
    *)
      ;;
  esac

  echo "Do you want to set a custom Password? (default: ${AUTOHOTSPOT_PASSWORD}) [y/N] " 1>&3
  read -r response_pw_q
  case "$response_pw_q" in
    [yY])
      while [ $(echo ${response_pw}|wc -m) -lt 8 ]
      do
          echo "Please type the new password (at least 8 character)." 1>&3
          read -r response_pw
      done
      AUTOHOTSPOT_PASSWORD="${response_pw}"
      ;;
    *)
      ;;
  esac

  if [ "$ENABLE_STATIC_IP" = true ]; then
    echo "Wifi hotspot cannot be enabled with static IP. Disabling static IP configuration." 1>&3
    echo "---------------------
" 1>&3
    ENABLE_STATIC_IP=false
    echo "ENABLE_STATIC_IP=${ENABLE_STATIC_IP}"
  fi

  echo "ENABLE_AUTOHOTSPOT=${ENABLE_AUTOHOTSPOT}"
  if [ "$ENABLE_AUTOHOTSPOT" = true ]; then
    echo "AUTOHOTSPOT_PASSWORD=${AUTOHOTSPOT_PASSWORD}"
  fi
}

_option_bluetooth() {
  # DISABLE_BLUETOOTH
  echo "Do you want to disable Bluethooth?
We recommend to turn off Bluetooth to save energy and booting time.
[Y/n] " 1>&3
  read -r response
  case "$response" in
    [nN][oO]|[nN])
      DISABLE_BLUETOOTH=false
      ;;
    *)
      ;;
  esac
  echo "DISABLE_BLUETOOTH=${DISABLE_BLUETOOTH}"
}

_option_samba() {
  # ENABLE_SAMBA
  echo "Would you like to install and configure Samba for easy file transfer?
There are other ways to copy music to your RPi but Samba is the simplest
method. If you are unsure, say yes!
[Y/n] " 1>&3
  read -r response
  case "$response" in
    [nN][oO]|[nN])
      ENABLE_SAMBA=false
      ENABLE_KIOSK_MODE=false
      ;;
    *)
      ;;
  esac
  echo "ENABLE_SAMBA=${ENABLE_SAMBA}"
}

_option_webapp() {
  # ENABLE_WEBAPP
  echo "Would you like to install the web application?
If you don't want to use a graphical interface to manage your Phoniebox,
you don't need to install the web application.
[Y/n] " 1>&3
  read -r response
  case "$response" in
    [nN][oO]|[nN])
      ENABLE_WEBAPP=false
      ENABLE_KIOSK_MODE=false
      ;;
    *)
      ;;
  esac
  echo "ENABLE_WEBAPP=${ENABLE_WEBAPP}"
}

_option_kiosk_mode() {
  # ENABLE_KIOSK_MODE
  echo "Would you like to enable the Kiosk Mode?
If you have a screen attached to your RPi, this will launch the
web application right after boot. It will only install the necessary
xserver dependencies and not the entire RPi desktop environment.
[y/N] " 1>&3
  read -r response
  case "$response" in
    [yY])
      ENABLE_KIOSK_MODE=true
      ;;
    *)
      ;;
  esac
  echo "ENABLE_KIOSK_MODE=${ENABLE_KIOSK_MODE}"
}

_options_update_raspi_os() {
  # UPDATE_RASPI_OS
  echo "Would you like to update the operating system?
This shall be done eventually, but increases the installation time a lot.
[y/N] " 1>&3
  read -r response
  case "$response" in
    [yY])
      UPDATE_RASPI_OS=true
      ;;
    *)
      ;;
  esac
  echo "UPDATE_RASPI_OS=${UPDATE_RASPI_OS}"
}

_option_disable_onboard_audio() {
  # Disable BCM on-chip audio (typically Headphones)
  # not needed when external sound card is sued

  echo -e "Disable Pi's on-chip audio (headphone / jack output)?
If you are using an external sound card (e.g. USB, HifiBerry, PirateAudio, etc),
we recommend to disable the on-chip audio. It will make the ALSA sound configuration easier.
If you are planning to only use Bluetooth speakers, leave the on-chip audio enabled!
(This will touch your boot configuration in ${RPI_BOOT_CONFIG_FILE}.
We will do our best not to mess anything up. However, a backup copy will be written to
${DISABLE_ONBOARD_AUDIO_BACKUP} if things go pear-shaped.)
[y/N] " 1>&3
  read -r response
  case "$response" in
    [yY])
      DISABLE_ONBOARD_AUDIO=true
      ;;
    *)
      ;;
  esac
  echo "DISABLE_ONBOARD_AUDIO=${DISABLE_ONBOARD_AUDIO}"

}

customize_options() {
  echo "Customize Options starts"

  _option_static_ip
  _option_ipv6
  _option_autohotspot
  _option_bluetooth
  _option_disable_onboard_audio
  _option_samba
  _option_webapp
  if [ "$ENABLE_WEBAPP" = true ] ; then
    _option_kiosk_mode
  fi
  _options_update_raspi_os

  echo "Customize Options ends"
}
