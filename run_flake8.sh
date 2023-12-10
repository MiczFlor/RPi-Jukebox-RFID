#!/usr/bin/env bash

# Runner script for flak8 to ensure
# - correct config file
# - independent from working directory

# Change working directory to location of script
SOURCE=${BASH_SOURCE[0]}
SCRIPT_DIR="$(dirname "$SOURCE")"
cd "$SCRIPT_DIR" || (echo "Could not change to top-level project directory" && exit 1)

# Run flake8
flake8 --config .flake8 "$@"
