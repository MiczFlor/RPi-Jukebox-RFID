#!/usr/bin/env bash

usage() {
  echo "Runner script for sphinx documentation build"
  echo "Usage:"
  echo "   ./run_sphinx.sh    : incremental build"
  echo "   ./run_sphinx.sh -c : clean re-build"
  exit 1
}

# Change working directory to location of script
SOURCE=${BASH_SOURCE[0]}
SCRIPT_DIR="$(dirname "$SOURCE")"
cd "$SCRIPT_DIR/docs/sphinx" || (echo "Could not change to docs directory" && exit 1)

BUILD_DIR=_build

CLEAN_BUILD=false
while getopts ":ch" opt;
do
  case ${opt} in
    c ) CLEAN_BUILD=true
      ;;
    h ) usage
      ;;
    \? ) usage
      ;;
  esac
done

SPHINX_OPTS="-W --keep-going -T"

if [[ $CLEAN_BUILD = true ]]; then
  echo "Cleaning $BUILD_DIR"
  rm -rf $BUILD_DIR
  SPHINX_OPTS="-W --keep-going -T -a -E"
fi

echo "Building docs [ sphinx-build $SPHINX_OPTS -b html . ${BUILD_DIR}/html ]"
sphinx-build $SPHINX_OPTS -b html . ${BUILD_DIR}/html

