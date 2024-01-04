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

change_swap() {
    local new_swap_size="$1"
    sudo dphys-swapfile swapoff || return 1
    sudo sed -i "s|.*CONF_SWAPSIZE=.*|CONF_SWAPSIZE=${new_swap_size}|g" /etc/dphys-swapfile || return 1
    sudo sed -i "s|^\s*CONF_SWAPFACTOR=|#CONF_SWAPFACTOR=|g" /etc/dphys-swapfile || return 1
    sudo dphys-swapfile setup || return 1
    sudo dphys-swapfile swapon || return 1
}

RECURSION_BREAKER=false
calc_nodemem() {

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
    echo ""

  if [[ -z $NODEMEM ]]; then
    # Keep a buffer of minimum 20 MB
    if [[ $TotalFree -gt 1044 ]]; then
        NODEMEM=1024
    elif [[ $TotalFree -gt 532 ]]; then
        NODEMEM=512
    elif [[ $TotalFree -gt 276 ]]; then
        NODEMEM=256
    else
        if [ "$RECURSION_BREAKER" == true ]; then
            return 1;
        fi

        local new_swap_size=532
        echo "ERROR: Not enough memory available on system."
        echo "Current free memory = $TotalFree MB"
        echo "Swap file will be increased to ${new_swap_size} MB"

        local filesystem_left=$((new_swap_size + 512))
        local filesystem_free=$(df -BM -P / | tail -n 1 | awk '{print $4}')
        filesystem_free=${filesystem_free//M}
        if [ "${filesystem_free}" -le "${filesystem_left}" ]; then
            echo "ERROR: Not enough space available on filesystem. At least ${filesystem_left} MB free memory are needed."
            echo "Current free space = $filesystem_free MB"
            echo "Hint: if only a little memory is missing, stopping spocon, mpd, and jukebox-daemon might give you enough space"
            exit 1
        else
            if ! change_swap $new_swap_size ; then
                echo "ERROR: failed to change swap file"
                exit 1
            fi
        fi

        RECURSION_BREAKER=true
        calc_nodemem || return 1
    fi
  fi
}

calc_nodemem

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
