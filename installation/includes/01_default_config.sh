#!/usr/bin/env bash

BUILD_LIBZMQ_WITH_DRAFTS_ON_DEVICE=${BUILD_LIBZMQ_WITH_DRAFTS_ON_DEVICE:-"false"}
ENABLE_STATIC_IP=true
DISABLE_IPv6=true
ENABLE_AUTOHOTSPOT=false
AUTOHOTSPOT_PROFILE="Phoniebox_Hotspot"
AUTOHOTSPOT_SSID="$AUTOHOTSPOT_PROFILE"
AUTOHOTSPOT_PASSWORD="PlayItLoud!"
AUTOHOTSPOT_IP="10.0.0.1"
AUTOHOTSPOT_COUNTRYCODE="DE"
DISABLE_BLUETOOTH=true
DISABLE_SSH_QOS=true
DISABLE_BOOT_SCREEN=true
DISABLE_BOOT_LOGS_PRINT=true
SETUP_MPD=true
ENABLE_MPD_OVERWRITE_INSTALL=true
UPDATE_RASPI_OS=${UPDATE_RASPI_OS:-"true"}
ENABLE_RFID_READER=true
ENABLE_SAMBA=true
ENABLE_WEBAPP=true
ENABLE_KIOSK_MODE=false
DISABLE_ONBOARD_AUDIO=false
# Always try to use GIT with SSH first, and on failure drop down to HTTPS
GIT_USE_SSH=${GIT_USE_SSH:-"true"}

# A pre-build binary for the Web App is only available for release builds
# For non-production builds, the Wep App must be build locally
# Valid values
# - release-only: download in release branch only
# - true: force download even in non-release branch
# - false: never download
ENABLE_WEBAPP_PROD_DOWNLOAD=${ENABLE_WEBAPP_PROD_DOWNLOAD:-"release-only"}
