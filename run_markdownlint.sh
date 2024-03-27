#!/usr/bin/env bash

# Runner script to ensure
# - independent from working directory

# Change working directory to project root
SOURCE=${BASH_SOURCE[0]}
SCRIPT_DIR="$(dirname "$SOURCE")"
PROJECT_ROOT="$SCRIPT_DIR"
cd "$PROJECT_ROOT" || { echo "Could not change directory"; exit 1; }

# Run markdownlint-cli2
./src/webapp/node_modules/.bin/markdownlint-cli2 --config .markdownlint-cli2.yaml "#node_modules" || { echo "ERROR: markdownlint-cli2 not found"; exit 1; }
