#!/usr/bin/env bash

# Runner script for sniffer tool to ensure
# - correct venv activation
# - independent from working directory

# Change working directory to location of script
SOURCE=${BASH_SOURCE[0]}
SCRIPT_DIR="$(dirname "$SOURCE")"
PROJECT_ROOT="$(realpath "$SCRIPT_DIR"/../..)"

cd "$PROJECT_ROOT" ||  { echo "Could not change directory"; exit 1; }
source "${PROJECT_ROOT}"/.venv/bin/activate || { echo "ERROR: Failed to activate virtual environment for python"; exit 1; }

cd "${PROJECT_ROOT}"/src/jukebox ||  { echo "Could not change directory"; exit 1; }
python run_register_rfid_reader.py $@
