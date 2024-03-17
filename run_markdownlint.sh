#!/usr/bin/env bash

# Runner script to ensure
# - independent from working directory

# Change working directory to project root
SOURCE=${BASH_SOURCE[0]}
SCRIPT_DIR="$(dirname "$SOURCE")"
PROJECT_ROOT="$SCRIPT_DIR"
cd "$PROJECT_ROOT" || { echo "Could not change directory"; exit 1; }

# Run markdownlint-cli2 (in a Docker container for convenience)
docker run -v $PWD:/workdir davidanson/markdownlint-cli2:v0.12.1 --config .markdownlint-cli2.yaml "#node_modules"