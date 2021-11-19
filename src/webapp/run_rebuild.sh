#!/usr/bin/env bash

usage() {
  echo -e "\nRebuild the Web App\n"
  echo "${BASH_SOURCE[0]} [-u] [-m SIZE]"
  echo "  -u      : Update NPM dependencies before rebuild (only necessary if package.json changed)"
  echo "  -m SIZE : Set Node memory limit in MB (if omitted limit is deduced automatically)"
  echo -e "\n\n"
}

UPDATE_DEPENDENCIES=false

while getopts ":uhm:" opt; do
  case ${opt} in
  u)
    UPDATE_DEPENDENCIES=true
    ;;
  m)
    NODEMEM="${OPTARG}"
    ;;
  h)
    usage
    ;;
  \?)
    usage
    ;;
  esac
done

# Change working directory to location of script
SOURCE=${BASH_SOURCE[0]}
SCRIPT_DIR="$(dirname "$SOURCE")"
cd "$SCRIPT_DIR" || exit 1

# Need to check free space and limit Node memory usage
# for PIs with little memory
MEMORY=$(grep MemTotal /proc/meminfo | awk '{print $2}')
FREEMEM=$(free -mt | sed -rn 's/Total:\s+[0-9]+\s+[0-9]+\s+([0-9])/\1/p')

echo "Max memory: ${MEMORY}"
echo "Free memory: ${FREEMEM}"

if [ "$MEMORY" -lt 600000 ]; then
  if [[ -z $NODEMEM ]]; then
    # Keep a buffer of minimum 20 MB
    if [[ $FREEMEM -gt 1044 ]]; then
      NODEMEM=1024
    elif [[ $FREEMEM -gt 532 ]]; then
      NODEMEM=512
    elif [[ $FREEMEM -gt 276 ]]; then
      NODEMEM=256
    else
      echo "ERROR: Not enough memory available on system. Please increase swap size to give at least 276 MByte free memory."
      echo "Current free memory = $FREEMEM"
      echo "Hint: if only a little memory is missing, stopping spocon, mpd, and jukebox-daemon might give you enough space"
      exit 1
    fi
  fi

  if [[ $NODEMEM -gt $FREEMEM ]]; then
    echo "ERROR: Requested node memory setting is larger than available free memory: $NODEMEM MB > $FREEMEM MB"
    exit 1
  fi

  export NODE_OPTIONS=--max-old-space-size=${NODEMEM}

  echo "Setting Node Options:"
  env | grep NODE
fi

# In rare cases you will need to update the npm dependencies
# This is the case when the file package.json changed
if [[ $UPDATE_DEPENDENCIES == true ]]; then
  npm install
fi

# Rebuild Web App
npm run build
