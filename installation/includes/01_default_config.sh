#!/usr/bin/env bash

BUILD_LIBZMQ_WITH_DRAFTS_ON_DEVICE=false
ENABLE_STATIC_IP=true
DISABLE_IPv6=true
ENABLE_AUTOHOTSPOT=false
AUTOHOTSPOT_CHANGE_PASSWORD=false
AUTOHOTSPOT_PASSWORD="PlayItLoud!"
DISABLE_BLUETOOTH=true
DISABLE_SSH_QOS=true
DISABLE_BOOT_SCREEN=true
DISABLE_BOOT_LOGS_PRINT=true
SETUP_MPD=true
UPDATE_RASPI_OS=${UPDATE_RASPI_OS:-"true"}
ENABLE_SAMBA=true
ENABLE_WEBAPP=true
ENABLE_KIOSK_MODE=false
DISABLE_ONBOARD_AUDIO=false
DISABLE_ONBOARD_AUDIO_BACKUP="${RPI_BOOT_CONFIG_FILE}.backup.audio_on_$(date +%d.%m.%y_%H.%M.%S)"
# Always try to use GIT with SSH first, and on failure drop down to HTTPS
GIT_USE_SSH=${GIT_USE_SSH:-"true"}

# A pre-build binary for the Web App is only available for release builds
# For non-production builds, the Wep App must be build locally
# Valid values
# - release-only: download in release branch only
# - true: force download even in non-release branch,
# - false: never download
ENABLE_WEBAPP_PROD_DOWNLOAD=${ENABLE_WEBAPP_PROD_DOWNLOAD:-"release-only"}
# Install Node during setup for Web App building. This is only needed for development builds
ENABLE_INSTALL_NODE=${ENABLE_INSTALL_NODE:-"false"}
