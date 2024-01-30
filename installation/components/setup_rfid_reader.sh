#!/usr/bin/env bash

SOURCE=${BASH_SOURCE[0]}
SCRIPT_DIR="$(dirname "$SOURCE")"
PROJECT_ROOT="$SCRIPT_DIR"/../../
cd "$SCRIPT_DIR" || (echo "Could not change to script directory" && exit 1)

source "$PROJECT_ROOT"/.venv/bin/activate
python "$PROJECT_ROOT"/src/jukebox/components/rfid/hardware/run_register_rfid_reader.py
