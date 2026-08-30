#!/usr/bin/env bash

# Install Phoniebox and test it — in both installation modes.
# Used e.g. for tests on Docker.

# Objective:
# Test the common installation path (including autohotspot) in BOTH modes:
#   1. interactive     — the installer is driven by prompt answers (heredoc)
#   2. non-interactive — the same options are supplied via a flat KEY=VALUE
#                        config file (--config)
# Keeping both modes in one script guarantees they stay consistent: the
# interactive answers and the non-interactive config describe the very same
# scenario and are defined side by side (see below).

set -euo pipefail

SOURCE="${BASH_SOURCE[0]}"
SCRIPT_DIR="$(dirname "$SOURCE")"
LOCAL_INSTALL_SCRIPT_PATH="${INSTALL_SCRIPT_PATH:-${SCRIPT_DIR}/../../installation}"
LOCAL_INSTALL_SCRIPT_PATH="${LOCAL_INSTALL_SCRIPT_PATH%/}"
INSTALL_SCRIPT="${LOCAL_INSTALL_SCRIPT_PATH}/install-jukebox.sh"

# ---------------------------------------------------------------------------
# Common test scenario — the single source of truth for both modes.
#
# Non-interactive config value       Interactive answer (prompt order):
#   welcome                                y - start setup
#   ENABLE_STATIC_IP=false                 n - use static ip
#   DISABLE_IPv6=false                     n - deactivate ipv6
#   ENABLE_AUTOHOTSPOT=true                y - setup autohotspot
#   (autohotspot sub-prompt)               n -   change default configuration
#   DISABLE_BLUETOOTH=false                n - deactivate bluetooth
#   DISABLE_ONBOARD_AUDIO=false            n - disable on-chip audio
#   ENABLE_RFID_READER=false               n - setup rfid reader
#   ENABLE_SAMBA=true                      y - setup samba
#   ENABLE_WEBAPP=true                     y - setup webapp
#   ENABLE_WEBAPP_PROD_DOWNLOAD=true       - - exact Web App bundle download (forced)
#   ENABLE_KIOSK_MODE=false                n - setup kiosk mode
#   EXISTING_INSTALL_ACTION=remove         n - reboot
#
# The mpd overwrite prompt only appears with an existing installation, which
# is not the case for the interactive run on the fresh test image.
# ---------------------------------------------------------------------------

SCENARIO_CONFIG="$(mktemp)"
trap 'rm -f "${SCENARIO_CONFIG}"' EXIT

cat > "${SCENARIO_CONFIG}" <<'EOF'
ENABLE_STATIC_IP=false
DISABLE_IPv6=false
ENABLE_AUTOHOTSPOT=true
DISABLE_BLUETOOTH=false
DISABLE_ONBOARD_AUDIO=false
ENABLE_RFID_READER=false
ENABLE_SAMBA=true
ENABLE_WEBAPP=true
ENABLE_WEBAPP_PROD_DOWNLOAD=true
ENABLE_KIOSK_MODE=false
EXISTING_INSTALL_ACTION=remove
EOF

# Interactive answers, in prompt order (see scenario above).
export ENABLE_WEBAPP_PROD_DOWNLOAD=true
INTERACTIVE_ANSWERS='y
n
n
y
n
n
n
n
y
y
n
n
'

# --- Mode 1: interactive ---------------------------------------------------
echo "--- Running common install scenario (interactive mode) ---"
"${INSTALL_SCRIPT}" <<< "${INTERACTIVE_ANSWERS}"

# --- Mode 2: non-interactive ----------------------------------------------
# Re-runs the same scenario non-interactively. The installation from the
# interactive run above is removed first, which also exercises the
# EXISTING_INSTALL_ACTION=remove handling.
echo "--- Running common install scenario (non-interactive mode) ---"
"${INSTALL_SCRIPT}" --config "${SCENARIO_CONFIG}"

