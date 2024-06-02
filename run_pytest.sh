#!/usr/bin/env bash

# Runner script to ensure
# - correct venv activation
# - independent from working directory

# Change working directory to project root
SOURCE=${BASH_SOURCE[0]}
SCRIPT_DIR="$(dirname "$SOURCE")"
PROJECT_ROOT="$SCRIPT_DIR"
cd "$PROJECT_ROOT" || { echo "Could not change directory"; exit 1; }

source .venv/bin/activate || { echo "ERROR: Failed to activate virtual environment for python"; exit 1; }

# Run pytest
pytest -c pytest.ini $@
