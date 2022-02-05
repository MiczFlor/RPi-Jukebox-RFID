#!/usr/bin/env bash

usage() {
  echo "Runner script for sphinx documentation build"
  echo -e "\nWarnings are treated as errors as preparation for documentation releases.\n"
  echo "Usage:"
  echo "   ./run_sphinx.sh    : incremental build"
  echo "   ./run_sphinx.sh -c : clean re-build"
  echo "   ./run_sphinx.sh -n : Don't escalate warning to errors (for debug only!)"
  exit 1
}

# Change working directory to location of script
SOURCE=${BASH_SOURCE[0]}
SCRIPT_DIR="$(dirname "$SOURCE")"
cd "$SCRIPT_DIR/docs/sphinx" || (echo "Could not change to docs directory" && exit 1)

BUILD_DIR=_build

CLEAN_BUILD=false
SPHINX_OPTS="-W --keep-going -T"
while getopts ":chn" opt;
do
  case ${opt} in
    c ) CLEAN_BUILD=true
      ;;
    h ) usage
      ;;
    n ) SPHINX_OPTS="-T"
      ;;
    \? ) usage
      ;;
  esac
done


if [[ $CLEAN_BUILD = true ]]; then
  echo "Cleaning $BUILD_DIR"
  rm -rf $BUILD_DIR
  SPHINX_OPTS="$SPHINX_OPTS -a -E"
fi

echo "Building docs [ sphinx-build $SPHINX_OPTS -b html . ${BUILD_DIR}/html/docs ]"
sphinx-build $SPHINX_OPTS -b html . ${BUILD_DIR}/html/docs

