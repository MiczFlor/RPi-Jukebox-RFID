#!/usr/bin/env bash

usage() {
  echo -e "\nRebuild the Web App\n"
  echo "${BASH_SOURCE[0]} [-u]"
  echo -e "  -u: Update NPM dependencies before rebuild (only necessary if package.json changed)\n\n"
}

UPDATE_DEPENDENCIES=false

while getopts ":uh" opt;
do
  case ${opt} in
    u ) UPDATE_DEPENDENCIES=true
      ;;
    h ) usage
      ;;
    \? ) usage
      ;;
  esac
done


# Change working directory to location of script
SOURCE=${BASH_SOURCE[0]}
SCRIPT_DIR="$(dirname "$SOURCE")"
cd "$SCRIPT_DIR" || exit 1

# PIs with little memory need this to finish building the Webapp
export NODE_OPTIONS=--max-old-space-size=512

# In rare cases you will need to update the npm dependencies
# This is the case when the file package.json changed
if [[ $UPDATE_DEPENDENCIES == true ]]
then
  npm install
fi

# Rebuild Web App
npm run build