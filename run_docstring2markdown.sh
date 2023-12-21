#!/usr/bin/env bash

# Runner script for lazydocs to ensure
# - independent from working directory

# Change working directory to location of script
SOURCE=${BASH_SOURCE[0]}
SCRIPT_DIR="$(dirname "$SOURCE")"
cd "$SCRIPT_DIR" || (echo "Could not change to top-level project directory" && exit 1)

# Run lazydocs
lazydocs \
    --output-path="./documentation/developers/docstring" \
    --overview-file="docstring.md" \
    --src-base-url="https://github.com/MiczFlor/RPi-Jukebox-RFID/tree/future3/develop/src/jukebox/" \
    --ignored-modules="ruamel,pulsectl" \
    ./src/jukebox