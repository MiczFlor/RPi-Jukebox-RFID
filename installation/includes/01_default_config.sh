#!/usr/bin/env bash

# NOTE: All defaults use ${VAR:-"default"} so that values already set via
# `--config`/environment (non-interactive install) are NOT overwritten.
ENABLE_STATIC_IP=${ENABLE_STATIC_IP:-"true"}
DISABLE_IPv6=${DISABLE_IPv6:-"true"}
ENABLE_AUTOHOTSPOT=${ENABLE_AUTOHOTSPOT:-"false"}
AUTOHOTSPOT_PROFILE=${AUTOHOTSPOT_PROFILE:-"Phoniebox_Hotspot"}
AUTOHOTSPOT_SSID=${AUTOHOTSPOT_SSID:-"$AUTOHOTSPOT_PROFILE"}
AUTOHOTSPOT_PASSWORD=${AUTOHOTSPOT_PASSWORD:-"PlayItLoud!"}
AUTOHOTSPOT_IP=${AUTOHOTSPOT_IP:-"10.0.0.1"}
AUTOHOTSPOT_COUNTRYCODE=${AUTOHOTSPOT_COUNTRYCODE:-"DE"}
DISABLE_BLUETOOTH=${DISABLE_BLUETOOTH:-"true"}
DISABLE_BOOT_SCREEN=${DISABLE_BOOT_SCREEN:-"true"}
DISABLE_BOOT_LOGS_PRINT=${DISABLE_BOOT_LOGS_PRINT:-"true"}
SETUP_MPD=${SETUP_MPD:-"true"}
ENABLE_MPD_OVERWRITE_INSTALL=${ENABLE_MPD_OVERWRITE_INSTALL:-"true"}
UPDATE_RASPI_OS=${UPDATE_RASPI_OS:-"false"}
ENABLE_RFID_READER=${ENABLE_RFID_READER:-"true"}
ENABLE_SAMBA=${ENABLE_SAMBA:-"false"}
ENABLE_WEBAPP=${ENABLE_WEBAPP:-"true"}
ENABLE_KIOSK_MODE=${ENABLE_KIOSK_MODE:-"false"}
DISABLE_ONBOARD_AUDIO=${DISABLE_ONBOARD_AUDIO:-"false"}
# HTTPS works without repository credentials. Developers can explicitly opt in
# to SSH; a failed SSH fetch still falls back to HTTPS.
GIT_USE_SSH=${GIT_USE_SSH:-"false"}

# Valid values
# - release-only: download an exact-commit release bundle
# - true: download an exact-commit development or release bundle
# - false: unsupported legacy setting; installation will fail
ENABLE_WEBAPP_PROD_DOWNLOAD=${ENABLE_WEBAPP_PROD_DOWNLOAD:-"release-only"}
