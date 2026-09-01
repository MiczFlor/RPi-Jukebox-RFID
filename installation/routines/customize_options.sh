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

_option_autohotspot() {
    # ENABLE_AUTOHOTSPOT
    clear_c
    print_c "---------------------- AUTOHOTSPOT ----------------------

When enabled, this service spins up a WiFi hotspot
when the Phoniebox is unable to connect to a known
WiFi. This way you can still access it.

Note:
Static IP configuration cannot be enabled with
WiFi hotspot and will be disabled, if selected before.

Do you want to enable an Autohotspot? [y/N]"
    read -r response
    case "$response" in
        [yY][eE][sS]|[yY])
            ENABLE_AUTOHOTSPOT=true
            ;;
        *)
            ;;
    esac

    if [ "$ENABLE_AUTOHOTSPOT" = true ]; then
        #add hostname to default SSID to prevent collision
        local local_hostname=$(hostname)
        AUTOHOTSPOT_SSID="${AUTOHOTSPOT_SSID}_${local_hostname}"
        AUTOHOTSPOT_SSID="${AUTOHOTSPOT_SSID:0:32}"

        local response_autohotspot
        while [[ $response_autohotspot != "n" ]]
        do
            print_c "
--- Current configuration for Autohotpot
SSID              : $AUTOHOTSPOT_SSID
Password          : $AUTOHOTSPOT_PASSWORD
WiFi Country Code : $AUTOHOTSPOT_COUNTRYCODE
IP                : $AUTOHOTSPOT_IP
Do you want to change this values? [y/N]"
            read -r response_autohotspot
            case "$response_autohotspot" in
                [yY][eE][sS]|[yY])
                    local response_ssid=""
                    local response_ssid_length=0
                    while [[ $response_ssid_length -lt 1 || $response_ssid_length -gt 32 ]]
                    do
                        print_c "Please type the hotspot ssid (must be between 1 and 32 characters long):"
                        read -r response_ssid
                        response_ssid_length=$(get_string_length ${response_ssid})
                    done

                    local response_pw=""
                    local response_pw_length=0
                    while [[ $response_pw_length -lt 8 || $response_pw_length -gt 63 ]]
                    do
                        print_c "Please type the new password (must be between 8 and 63 characters long):"
                        read -r response_pw
                        response_pw_length=$(get_string_length ${response_pw})
                    done

                    local response_country_code=""
                    local response_country_code_length=0
                    while [[ $response_country_code_length -ne 2 ]]
                    do
                        print_c "Please type the WiFi country code (e.g. DE, GB, CZ or US):"
                        read -r response_country_code
                        response_country_code="${response_country_code^^}" # to Uppercase
                        response_country_code_length=$(get_string_length ${response_country_code})
                    done

                    AUTOHOTSPOT_SSID="${response_ssid}"
                    AUTOHOTSPOT_PASSWORD="${response_pw}"
                    AUTOHOTSPOT_COUNTRYCODE="${response_country_code}"
                    ;;
                *)
                    response_autohotspot=n
                    ;;
            esac
        done

        if [ "$ENABLE_STATIC_IP" = true ]; then
            ENABLE_STATIC_IP=false
            echo "ENABLE_STATIC_IP=${ENABLE_STATIC_IP}"
        fi
    fi

    echo "ENABLE_AUTOHOTSPOT=${ENABLE_AUTOHOTSPOT}"
    if [ "$ENABLE_AUTOHOTSPOT" = true ]; then
        echo "AUTOHOTSPOT_SSID=${AUTOHOTSPOT_SSID}"
        echo "AUTOHOTSPOT_PASSWORD=${AUTOHOTSPOT_PASSWORD}"
        echo "AUTOHOTSPOT_COUNTRYCODE=${AUTOHOTSPOT_COUNTRYCODE}"
        echo "AUTOHOTSPOT_IP=${AUTOHOTSPOT_IP}"
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

_option_spotify() {
  clear_c

  if [[ "$(get_architecture)" == "armv6" ]]; then
    print_c "----------------------- SPOTIFY -------------------------

Spotify is not yet supported on ARMv6 Raspberry Pi models.
Spotify support will not be installed."
    SETUP_SPOTIFY=false
    log "SETUP_SPOTIFY=${SETUP_SPOTIFY}"
    return
  fi

  print_c "----------------------- SPOTIFY -------------------------

Spotify playback requires a Premium account and a Spotify
developer app. Librespot will be installed as a user service.

Would you like to install Spotify support? [y/N]"
  read -r response
  case "$response" in
    [yY][eE][sS]|[yY])
      SETUP_SPOTIFY=true
      ;;
    *)
      SETUP_SPOTIFY=false
      ;;
  esac

  if [[ "${SETUP_SPOTIFY}" == true ]]; then
    if [[ -z "${SPOTIFY_REDIRECT_URI}" ]]; then
      print_c "Spotify requires an exact OAuth redirect URI.
Press Enter to use the recommended URI below. A custom LAN or
public redirect URI normally requires HTTPS.

Spotify OAuth redirect URI [${SPOTIFY_DEFAULT_REDIRECT_URI}]:"
      read -r response
      SPOTIFY_REDIRECT_URI="${response:-$SPOTIFY_DEFAULT_REDIRECT_URI}"
    fi

    print_c "Before continuing, create a Spotify developer app:

1. Go to https://developer.spotify.com/dashboard
2. Click 'Create app'.
3. Enter an App name and App description, add this exact
   Redirect URI, and select 'Web API':

   ${SPOTIFY_REDIRECT_URI}

4. Save the app.

After creating the app, copy the Client ID from its
Basic Information page and enter it below."
    while [[ -z "${SPOTIFY_CLIENT_ID}" ]]; do
      print_c "Spotify developer app client ID:"
      read -r SPOTIFY_CLIENT_ID
    done

    if [[ "${SPOTIFY_REDIRECT_URI}" == "${SPOTIFY_DEFAULT_REDIRECT_URI}" ]]; then
      print_c "After installation, run this command on the computer where
you will open the Phoniebox Web App:

ssh -L 3000:127.0.0.1:80 ${CURRENT_USER:-USER}@$(hostname).local

Keep the SSH session open, browse to http://127.0.0.1:3000,
then select Settings > Spotify > Connect."
    fi

    print_c "Spotify Connect device name [${SPOTIFY_DEVICE_NAME}]:"
    read -r response
    response="${response:-$SPOTIFY_DEVICE_NAME}"
    if [[ ! "${response}" =~ ^[A-Za-z0-9._\ -]+$ ]]; then
      print_c "Invalid device name. Using '${SPOTIFY_DEVICE_NAME}'."
    else
      SPOTIFY_DEVICE_NAME="${response}"
    fi
  fi

  log "SETUP_SPOTIFY=${SETUP_SPOTIFY}"
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

The Web App can upload and manage files in the audio
library. Samba additionally provides direct network
access to the complete shared directory, including
configuration files.

Do you want to install Samba? [y/N]"
  read -r response
  case "$response" in
    [yY][eE][sS]|[yY])
      ENABLE_SAMBA=true
      ;;
    *)
      ENABLE_SAMBA=false
      ;;
  esac
  log "ENABLE_SAMBA=${ENABLE_SAMBA}"
}

_option_jellyfin() {
  # ENABLE_JELLYFIN
  clear_c
  print_c "------------------------ JELLYFIN -----------------------

The Phoniebox can use a Jellyfin media server as an additional
music source. The Jellyfin player backend streams audio through
MPD, so no extra playback daemon is installed.

You will be asked for the Jellyfin server address and the
authentication (API key or Jellyfin user login) after installation.

Would you like to setup Jellyfin? [y/N]"
  read -r response
  case "$response" in
    [yY][eE][sS]|[yY])
      ENABLE_JELLYFIN=true
      ;;
    *)
      ENABLE_JELLYFIN=false
      ;;
  esac
  log "ENABLE_JELLYFIN=${ENABLE_JELLYFIN}"
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
(This will touch your boot configuration file.
We will do our best not to mess anything up. However,
a backup copy will be written. Please check the install
log after for further details.)

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

_configure_webapp_bundle_download() {
  # Let's detect if we are on the official release branch
  if [[ "$GIT_BRANCH" != "${GIT_BRANCH_RELEASE}" && "$GIT_BRANCH" != "${GIT_BRANCH_DEVELOP}" ]] || [[ "$GIT_USER" != "$GIT_UPSTREAM_USER" ]] || [[ "$CI_RUNNING" == "true" ]] ; then
    # Development branches use their commit-addressed development bundle.
    if [[ "$ENABLE_WEBAPP_PROD_DOWNLOAD" == "release-only" ]]; then
      ENABLE_WEBAPP_PROD_DOWNLOAD=true
    fi
  fi

  log "ENABLE_WEBAPP_PROD_DOWNLOAD=${ENABLE_WEBAPP_PROD_DOWNLOAD}"
}

_run_customize_options() {
  _option_static_ip
  _option_autohotspot
  _option_bluetooth
  _option_disable_onboard_audio
  _option_mpd
  _option_spotify
  _option_jellyfin
  _option_rfid_reader
  _option_samba
  _option_webapp
  if [[ $ENABLE_WEBAPP == true ]] ; then
    _configure_webapp_bundle_download
    _option_kiosk_mode
  fi
}

customize_options() {
    run_with_log_frame _run_customize_options "Customize Options"
}
