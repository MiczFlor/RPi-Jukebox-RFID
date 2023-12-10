#!/usr/bin/env bash

# Runner script for python scripts with activated venv

SOURCE=${BASH_SOURCE[0]}
SCRIPT_DIR="$(dirname "$SOURCE")"
source ${SCRIPT_DIR}/.venv/bin/activate || { echo "ERROR: Failed to activate virtual environment"; exit 1; }

#Run commands given as paramter
$@
