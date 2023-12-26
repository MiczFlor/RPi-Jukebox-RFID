#!/usr/bin/env bash

# Runner script for pydoc-markdown to ensure
# - independent from working directory

# Change working directory to location of script
SOURCE=${BASH_SOURCE[0]}
SCRIPT_DIR="$(dirname "$SOURCE")"
cd "$SCRIPT_DIR" || (echo "Could not change to top-level project directory" && exit 1)

# Run pydoc-markdown
# make sure, directory exists
mkdir -p ./documentation/developers/docstring
# expects pydoc-markdown.yml at working dir
pydoc-markdown
