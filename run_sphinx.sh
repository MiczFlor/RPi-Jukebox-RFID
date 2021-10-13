#!/usr/bin/env bash

# Runner script for sphinx documentation build
# Usage:
# (a) run_sphinx.sh for incremental build
# (b) run_sphinx.sh clean for clean re-build

# Change working directory to location of script
SOURCE=${BASH_SOURCE[0]}
SCRIPT_DIR="$(dirname "$SOURCE")"
cd "$SCRIPT_DIR/docs/sphinx" || (echo "Could not change to docs directory" && exit 1)

# Run sphinx
make "$@" html
