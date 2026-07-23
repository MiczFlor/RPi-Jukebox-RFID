#!/usr/bin/env bash

# Runner script to ensure
# - independent from working directory
# - pyright itself is a uv dev-dependency (see pyproject.toml at repo root); `uv run` installs it into
#   .venv on first use.
#
# For pyright to actually resolve the application's imports (zmq, ruamel.yaml, ...) rather than just
# reporting them all as missing, that same .venv also needs the application's runtime dependencies
# installed, e.g.:
#   uv pip install -e src/jukebox
# (CI already has these installed into .venv before this script runs, see
# .github/workflows/pythonpackage_future3.yml)

# Change working directory to project root
SOURCE=${BASH_SOURCE[0]}
SCRIPT_DIR="$(dirname "$SOURCE")"
PROJECT_ROOT="$SCRIPT_DIR"
cd "$PROJECT_ROOT" || { echo "Could not change directory"; exit 1; }

uv run pyright "$@"
