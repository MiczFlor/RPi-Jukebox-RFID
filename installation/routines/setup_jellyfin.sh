#!/usr/bin/env bash

JELLYFIN_SETTINGS_FILE="${SETTINGS_PATH}/jukebox.yaml"

_jellyfin_set_user_config() {
  print_lc "  Configure Jellyfin"
  print_lc "    Enter your Jellyfin server URL (e.g. http://jellyfin.local:8096):"
  read -r JELLYFIN_HOST

  unset JELLYFIN_USERNAME JELLYFIN_PASSWORD
  print_lc "    Enter the Jellyfin username:"
  read -r JELLYFIN_USERNAME
  print_lc "    Enter the Jellyfin password (input is hidden):"
  read -r -s JELLYFIN_PASSWORD
  echo
  print_lc "    The login token inherits the library permissions of that user."

  if [[ -z "$JELLYFIN_HOST" ]]; then
    print_c "  WARNING: Jellyfin server URL is required. Skipping Jellyfin setup."
    ENABLE_JELLYFIN=false
    return
  fi
  if [[ -z "$JELLYFIN_USERNAME" || -z "$JELLYFIN_PASSWORD" ]]; then
    print_c "  WARNING: Jellyfin username and password are required. Skipping Jellyfin setup."
    ENABLE_JELLYFIN=false
    return
  fi

  # The Python heredoc reads the values from the environment, never from shell
  # interpolation, so special characters in host and credentials are
  # preserved. The delimiter is quoted to prevent any shell expansion inside
  # the Python code.
  JELLYFIN_HOST="$JELLYFIN_HOST" \
  JELLYFIN_USERNAME="${JELLYFIN_USERNAME:-}" \
  JELLYFIN_PASSWORD="${JELLYFIN_PASSWORD:-}" \
  JELLYFIN_SETTINGS_FILE="$JELLYFIN_SETTINGS_FILE" \
  "$VIRTUAL_ENV/bin/python3" - << 'PYEOF'
from ruamel.yaml import YAML
import os

yaml = YAML()
yaml.preserve_quotes = True
settings_file = os.environ['JELLYFIN_SETTINGS_FILE']
with open(settings_file, 'r') as stream:
    data = yaml.load(stream) or {}
data.setdefault('players', {})
existing = data.get('players', {}).get('jellyfin', {}) or {}
jellyfin = {
    'enabled': True,
    'host': os.environ['JELLYFIN_HOST'],
    # Tunable defaults are written explicitly so they are always present in
    # jukebox.yaml; values a user already customized are preserved.
    'catalog_cache_ttl': existing.get('catalog_cache_ttl', 300),
    'request_timeout': existing.get('request_timeout', 30),
}
if os.environ.get('JELLYFIN_USERNAME'):
    jellyfin['username'] = os.environ['JELLYFIN_USERNAME']
if os.environ.get('JELLYFIN_PASSWORD'):
    jellyfin['password'] = os.environ['JELLYFIN_PASSWORD']
# The token file and the device id belong to this installation, not to the
# credentials: a re-run keeps them, so a device id set on a cloned SD card
# survives.
for key in ('token_file', 'device_id'):
    if key in existing:
        jellyfin[key] = existing[key]
data['players']['jellyfin'] = jellyfin
with open(settings_file, 'w') as stream:
    yaml.dump(data, stream)
PYEOF
  if [ $? -ne 0 ]; then
    print_c "  WARNING: Failed to write jellyfin config to ${JELLYFIN_SETTINGS_FILE}."
    ENABLE_JELLYFIN=false
  fi
}

_jellyfin_check() {
  print_verify_installation
  echo "  [Jellyfin] Phoniebox Jellyfin plugin will be activated on next boot."
}

setup_jellyfin() {
  if [[ "$ENABLE_JELLYFIN" == true ]]; then
    run_with_log_frame _jellyfin_set_user_config "Setup Jellyfin"
    if [[ "$ENABLE_JELLYFIN" == true ]]; then
      _jellyfin_check
    fi
  else
    log "Jellyfin setup skipped."
  fi
}
