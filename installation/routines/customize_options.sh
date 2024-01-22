#!/usr/bin/env bash

_option_static_ip() {
  # ENABLE_STATIC_IP
  # Using the dynamically assigned IP address as it is the best guess to be free
  # Reference: https://unix.stackexchange.com/a/505385
  CURRENT_ROUTE=$(ip route get 8.8.8.8)
  CURRENT_GATEWAY=$(echo "${CURRENT_ROUTE}" | awk '{ print $3; exit }')
  CURRENT_INTERFACE=$(echo "${CURRENT_ROUTE}" | awk '{ print $5; exit }')
  CURRENT_IP_ADDRESS=$(echo "${CURRENT_ROUTE}" | awk '{ print $7; exit }')
  clear_c
  print_c "----------------------- STATIC IP -----------------------

Setting a static IP will save a lot of start up time.
The static adress will be '${CURRENT_IP_ADDRESS}'
from interface '${CURRENT_INTERFACE}'
with the gateway '${CURRENT_GATEWAY}'.

Set a static IP? [Y/n]"
  read -r response
  case "$response" in
    [nN][oO]|[nN])
      ENABLE_STATIC_IP=false
      ;;
    *)
      ;;
  esac
  log "ENABLE_STATIC_IP=${ENABLE_STATIC_IP}"
}

_option_ipv6() {
  # DISABLE_IPv6
  clear_c
  print_c "------------------------- IP V6 -------------------------

IPv6 is only needed if you intend to use it.
Otherwise it can be disabled.

Do you want to disable IPv6? [Y/n]"
  read -r response
  case "$response" in
    [nN][oO]|[nN])
      DISABLE_IPv6=false
      ;;
    *)
      ;;
  esac
  log "DISABLE_IPv6=${DISABLE_IPv6}"
}

_option_autohotspot() {
  # ENABLE_AUTOHOTSPOT
  clear_c
  print_c "---------------------- AUTOHOTSPOT ----------------------

When enabled, this service spins up a WiFi hotspot
when the Phoniebox is unable to connect to a known
WiFi. This way you can still access it.

Do you want to enable an Autohotpot? [y/N]"
  read -r response
  case "$response" in
    [yY][eE][sS]|[yY])
      ENABLE_AUTOHOTSPOT=true
      ;;
    *)
      ;;
  esac

  if [ "$ENABLE_AUTOHOTSPOT" = true ]; then
      print_c "Do you want to set a custom Password? (default: ${AUTOHOTSPOT_PASSWORD}) [y/N] "
      read -r response_pw_q
      case "$response_pw_q" in
        [yY][eE][sS]|[yY])
          while [ $(echo ${response_pw}|wc -m) -lt 8 ]
          do
              print_c "Please type the new password (at least 8 character)."
              read -r response_pw
          done
          AUTOHOTSPOT_PASSWORD="${response_pw}"
          ;;
        *)
          ;;
      esac

      if [ "$ENABLE_STATIC_IP" = true ]; then
        print_c "Wifi hotspot cannot be enabled with static IP. Disabling static IP configuration."
        ENABLE_STATIC_IP=false
        log "ENABLE_STATIC_IP=${ENABLE_STATIC_IP}"
      fi
  fi

  log "ENABLE_AUTOHOTSPOT=${ENABLE_AUTOHOTSPOT}"
  if [ "$ENABLE_AUTOHOTSPOT" = true ]; then
    log "AUTOHOTSPOT_PASSWORD=${AUTOHOTSPOT_PASSWORD}"
  fi
}

_option_bluetooth() {
  # DISABLE_BLUETOOTH
  clear_c
  print_c "----------------------- BLUETOOTH -----------------------

Turning off Bluetooth will save energy and
start up time, if you do not plan to use it.

Do you want to disable Bluetooth? [Y/n]"
  read -r response
  case "$response" in
    [nN][oO]|[nN])
      DISABLE_BLUETOOTH=false
      ;;
    *)
      ;;
  esac
  log "DISABLE_BLUETOOTH=${DISABLE_BLUETOOTH}"
}

_option_mpd() {
    clear_c
    if [[ "$SETUP_MPD" == true ]]; then
        if [[ -f "${MPD_CONF_PATH}" || -f "${SYSTEMD_USR_PATH}/mpd.service" ]]; then
            print_c "-------------------------- MPD --------------------------

It seems there is a MPD already installed.
Note: It is important that MPD runs as a user service!
Would you like to overwrite your configuration? [Y/n]"
            read -r response
            case "$response" in
                [nN][oO]|[nN])
                    ENABLE_MPD_OVERWRITE_INSTALL=false
                    ;;
                *)
                    ;;
            esac
        fi
    fi

    log "SETUP_MPD=${SETUP_MPD}"
    if [ "$SETUP_MPD" == true ]; then
        log "ENABLE_MPD_OVERWRITE_INSTALL=${ENABLE_MPD_OVERWRITE_INSTALL}"
    fi
}

_option_rfid_reader() {
  # ENABLE_RFID_READER
  clear_c
  print_c "---------------------- RFID READER ----------------------

Phoniebox can be controlled with rfid cards/tags, if you
have a rfid reader connected.
Choose yes to setup a reader. You get prompted for
the type selection and configuration later on.

Do you want to setup a rfid reader? [Y/n]"
  read -r response
  case "$response" in
    [nN][oO]|[nN])
      ENABLE_RFID_READER=false
      ;;
    *)
      ;;
  esac
  log "ENABLE_RFID_READER=${ENABLE_RFID_READER}"
}

_option_samba() {
  # ENABLE_SAMBA
  clear_c
  print_c "------------------------- SAMBA -------------------------

Samba is required to conveniently copy files
to your Phoniebox via a network share.
If you don't need it, feel free to skip the installation.
If you are unsure, stick to YES!

Do you want to install Samba? [Y/n]"
  read -r response
  case "$response" in
    [nN][oO]|[nN])
      ENABLE_SAMBA=false
      ;;
    *)
      ;;
  esac
  log "ENABLE_SAMBA=${ENABLE_SAMBA}"
}

_option_webapp() {
  # ENABLE_WEBAPP
  clear_c
  print_c "------------------------ WEB APP ------------------------

This is only required if you want to use
a graphical interface to manage your Phoniebox!

Would you like to install the Web App? [Y/n]"
  read -r response
  case "$response" in
    [nN][oO]|[nN])
      ENABLE_WEBAPP=false
      ENABLE_KIOSK_MODE=false
      ;;
    *)
      ;;
  esac
  log "ENABLE_WEBAPP=${ENABLE_WEBAPP}"
}

_option_kiosk_mode() {
    # ENABLE_KIOSK_MODE
    clear_c
    print_c "----------------------- KIOSK MODE ----------------------"
    if [[ $(get_architecture) == "armv6" ]]; then

        print_c "
Due to limited resources the kiosk mode is not supported
on Raspberry Pi 1 or Zero 1 ('ARMv6' models).
Kiosk mode will not be installed.

Press enter to continue."
        read
        ENABLE_KIOSK_MODE=false
    else

        print_c "
If you have a screen attached to your RPi,
this will launch the Web App right after boot.
It will only install the necessary xserver dependencies
and not the entire RPi desktop environment.

Would you like to enable the Kiosk Mode? [y/N]"
        read -r response
        case "$response" in
            [yY][eE][sS]|[yY])
            ENABLE_KIOSK_MODE=true
            ;;
            *)
            ;;
        esac
    fi

    log "ENABLE_KIOSK_MODE=${ENABLE_KIOSK_MODE}"
}

_options_update_raspi_os() {
  # UPDATE_RASPI_OS
  clear_c
  print_c "----------------------- UPDATE OS -----------------------

This shall be done eventually,
but increases the installation time a lot.

Would you like to update the operating system? [Y/n]"
  read -r response
  case "$response" in
    [nN][oO]|[nN])
      UPDATE_RASPI_OS=false
      ;;
    *)
      ;;
  esac
  log "UPDATE_RASPI_OS=${UPDATE_RASPI_OS}"
}

_option_disable_onboard_audio() {
  # Disable BCM on-chip audio (typically Headphones)
  # not needed when external sound card is sued
  clear_c
  print_c "--------------------- ON-CHIP AUDIO ---------------------

If you are using an external sound card (e.g. USB,
HifiBerry, PirateAudio, etc), we recommend to disable
the on-chip audio. It will make the ALSA sound
configuration easier.
If you are planning to only use Bluetooth speakers,
leave the on-chip audio enabled!
(This will touch your boot configuration in
${RPI_BOOT_CONFIG_FILE}.
We will do our best not to mess anything up. However,
a backup copy will be written to
${DISABLE_ONBOARD_AUDIO_BACKUP} )

Disable Pi's on-chip audio (headphone / jack output)? [y/N]"
  read -r response
  case "$response" in
    [yY][eE][sS]|[yY])
      DISABLE_ONBOARD_AUDIO=true
      ;;
    *)
      ;;
  esac
  log "DISABLE_ONBOARD_AUDIO=${DISABLE_ONBOARD_AUDIO}"

}

_option_webapp_devel_build() {
  # Let's detect if we are on the official release branch
  if [[ "$GIT_BRANCH" != "${GIT_BRANCH_RELEASE}" && "$GIT_BRANCH" != "${GIT_BRANCH_DEVELOP}" ]] || [[ "$GIT_USER" != "$GIT_UPSTREAM_USER" ]] || [[ "$CI_RUNNING" == "true" ]] ; then
    # Unless ENABLE_WEBAPP_PROD_DOWNLOAD is forced to true by user override, do not download a potentially stale build
    if [[ "$ENABLE_WEBAPP_PROD_DOWNLOAD" == "release-only" ]]; then
      ENABLE_WEBAPP_PROD_DOWNLOAD=false
    fi
    if [[ "$ENABLE_WEBAPP_PROD_DOWNLOAD" != true && "$ENABLE_WEBAPP_PROD_DOWNLOAD" != "release-only" ]]; then
      clear_c
      print_c "--------------------- WEB APP BUILD ---------------------

You are installing from a non-release branch
and/or an unofficial repository.
Therefore a pre-build Web App is not available
and it needs to be built locally.
This requires Node to be installed.

If you decline, the lastest pre-build version
from the official repository will be installed.
This can lead to incompatibilities.

Do you want to build the Web App? [Y/n]"
      read -r response
      case "$response" in
        [nN][oO]|[nN])
            ENABLE_WEBAPP_PROD_DOWNLOAD=true
            ;;
        *)
            ;;
      esac
    fi
  fi

  log "ENABLE_WEBAPP_PROD_DOWNLOAD=${ENABLE_WEBAPP_PROD_DOWNLOAD}"
}

_run_customize_options() {
  _option_ipv6        # Optional: Not required for installation
  _option_static_ip   # Optional: Not required for installation
  _option_autohotspot # Optional: Not required for installation
  _option_bluetooth   # Optional: Not required for installation
  _option_disable_onboard_audio # Optional: Should be merged with other audio installations, like HifiBerry
  _option_mpd         # !!Required, without options
  _option_rfid_reader # !!Required, with options
  _option_samba       # !!Required, without options
  _option_webapp      # !!Required, without options
  if [[ $ENABLE_WEBAPP == true ]] ; then
    _option_webapp_devel_build # Optional: Not required for installation
    _option_kiosk_mode # Optional: Not required for installation
  fi
}

customize_options() {
    run_with_log_frame _run_customize_options "Customize Options"
}
