#!/usr/bin/env bash

# Runner script to ensure
# - independent from working directory
# - ruff itself is a uv dev-dependency (see pyproject.toml at repo root, a lightweight tooling-only
#   project separate from the packaged application in src/jukebox/pyproject.toml); `uv run` installs
#   it into .venv on first use, no manual setup required.

# Change working directory to project root
SOURCE=${BASH_SOURCE[0]}
SCRIPT_DIR="$(dirname "$SOURCE")"
PROJECT_ROOT="$SCRIPT_DIR"
cd "$PROJECT_ROOT" || { echo "Could not change directory"; exit 1; }

# Lint, then format-check (leaves files untouched; use `uv run ruff format .` locally to actually reformat)
uv run ruff check --config ruff.toml . "$@" \
  && uv run ruff format --config ruff.toml --check --diff .
