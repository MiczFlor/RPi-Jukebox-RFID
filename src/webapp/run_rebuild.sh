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
MemTotal=$(grep MemTotal /proc/meminfo | awk '{print $2}')
MemFree=$(grep MemFree /proc/meminfo | awk '{print $2}')
SwapFree=$(grep SwapFree /proc/meminfo | awk '{print $2}')
TotalFree=$((SwapFree + MemFree))

MemTotal=$((MemTotal / 1024))
MemFree=$((MemFree / 1024))
SwapFree=$((SwapFree / 1024))
TotalFree=$((TotalFree / 1024))

echo "Total phys memory: ${MemTotal} MB"
echo "Free phys memory : ${MemFree} MB"
echo "Free swap memory : ${SwapFree} MB"
echo "Free total memory: ${TotalFree} MB"


if [[ -z $NODEMEM ]]; then
  # Keep a buffer of minimum 20 MB
  if [[ $TotalFree -gt 1044 ]]; then
    NODEMEM=1024
  elif [[ $TotalFree -gt 532 ]]; then
    NODEMEM=512
  elif [[ $TotalFree -gt 276 ]]; then
    NODEMEM=256
  else
    echo "ERROR: Not enough memory available on system. Please increase swap size to give at least 276 MByte free memory."
    echo "Current free memory = $TotalFree MB"
    echo "Hint: if only a little memory is missing, stopping spocon, mpd, and jukebox-daemon might give you enough space"
    exit 1
  fi
fi

if [[ $NODEMEM -gt $TotalFree ]]; then
  echo "ERROR: Requested node memory setting is larger than available free memory: $NODEMEM MB > $TotalFree MB"
  exit 1
fi

export NODE_OPTIONS=--max-old-space-size=${NODEMEM}

echo "Setting Node Options:"
env | grep NODE

if [[ $(uname -m) == armv6l ]]; then
  echo "  You are running on a hardware with less resources. Building
  the webapp might fail. If so, try to install the stable
  release installation instead."
fi

# In rare cases you will need to update the npm dependencies
# This is the case when the file package.json changed
if [[ $UPDATE_DEPENDENCIES == true ]]; then
  npm install
fi

# Rebuild Web App
npm run build
