#!/usr/bin/env bash

ENABLE_STATIC_IP=true
ENABLE_AUTOHOTSPOT=false
AUTOHOTSPOT_PROFILE="Phoniebox_Hotspot"
AUTOHOTSPOT_SSID="$AUTOHOTSPOT_PROFILE"
AUTOHOTSPOT_PASSWORD="PlayItLoud!"
AUTOHOTSPOT_IP="10.0.0.1"
AUTOHOTSPOT_COUNTRYCODE="DE"
DISABLE_BLUETOOTH=true
DISABLE_BOOT_SCREEN=true
DISABLE_BOOT_LOGS_PRINT=true
SETUP_MPD=true
ENABLE_MPD_OVERWRITE_INSTALL=true
SETUP_SPOTIFY=${SETUP_SPOTIFY:-"false"}
LIBRESPOT_ALLOW_SOURCE_BUILD=${LIBRESPOT_ALLOW_SOURCE_BUILD:-"false"}
SPOTIFY_CLIENT_ID=${SPOTIFY_CLIENT_ID:-""}
SPOTIFY_DEFAULT_REDIRECT_URI="http://127.0.0.1:3000/api/v1/spotify/oauth/callback"
SPOTIFY_REDIRECT_URI=${SPOTIFY_REDIRECT_URI:-""}
SPOTIFY_DEVICE_NAME=${SPOTIFY_DEVICE_NAME:-"Phoniebox"}
UPDATE_RASPI_OS=${UPDATE_RASPI_OS:-"false"}
ENABLE_RFID_READER=true
ENABLE_SAMBA=false
ENABLE_JELLYFIN=${ENABLE_JELLYFIN:-false}
ENABLE_WEBAPP=true
ENABLE_KIOSK_MODE=false
DISABLE_ONBOARD_AUDIO=false
# HTTPS works without repository credentials. Developers can explicitly opt in
# to SSH; a failed SSH fetch still falls back to HTTPS.
GIT_USE_SSH=${GIT_USE_SSH:-"false"}

# Valid values
# - release-only: download an exact-commit release bundle
# - true: download an exact-commit development or release bundle
# - false: unsupported legacy setting; installation will fail
ENABLE_WEBAPP_PROD_DOWNLOAD=${ENABLE_WEBAPP_PROD_DOWNLOAD:-"release-only"}
