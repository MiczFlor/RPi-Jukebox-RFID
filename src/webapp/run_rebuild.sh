#!/usr/bin/env bash

usage() {
  echo -e "\nRebuild the Web App\n"
  echo "${BASH_SOURCE[0]} [-u] [-m SIZE]"
  echo "  -u      : Update NPM dependencies before rebuild (only necessary on first build or if package.json changed"
  echo "  -m SIZE : Set Node memory limit in MB (if omitted limit is deduced automatically and swap might be adjusted)"
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

calc_nodemem() {
    # keep a buffer for the kernel etc.
    local mem_buffer=256
    # Need to check free space and limit Node memory usage
    # for PIs with little memory
    MemTotal=$(grep MemTotal /proc/meminfo | awk '{print $2}')
    MemFree=$(grep MemFree /proc/meminfo | awk '{print $2}')
    SwapTotal=$(grep SwapTotal /proc/meminfo | awk '{print $2}')
    SwapFree=$(grep SwapFree /proc/meminfo | awk '{print $2}')
    TotalFree=$((SwapFree + MemFree))

    MemTotal=$((MemTotal / 1024))
    MemFree=$((MemFree / 1024))
    SwapTotal=$((SwapTotal / 1024))
    SwapFree=$((SwapFree / 1024))
    TotalFree=$((TotalFree / 1024))
    FreeToUse=$((TotalFree - mem_buffer))

    echo "Total phys memory : ${MemTotal} MB"
    echo "Free phys memory  : ${MemFree} MB"
    echo "Total swap memory : ${SwapTotal} MB"
    echo "Free swap memory  : ${SwapFree} MB"
    echo "Free total memory : ${TotalFree} MB"
    echo "Keep as buffer    : ${mem_buffer} MB"
    echo "Free usable memory: ${FreeToUse} MB"
    echo ""

  if [[ -z $NODEMEM ]]; then
    # mininum memory used for node
    local mem_min=512
    if [[ $FreeToUse -gt $mem_min ]]; then
        NODEMEM=$FreeToUse
    else
        local new_swap_size=$((SwapTotal + mem_min))
        echo "WARN: Not enough memory left on system for node (min. $mem_min MB)."
        echo "Trying to adjust swap size ..."

        # keep a buffer on the filesystem
        local filesystem_left=$((new_swap_size + 512))
        local filesystem_free=$(df -BM -P / | tail -n 1 | awk '{print $4}')
        filesystem_free=${filesystem_free//M}
        if [ "${filesystem_free}" -lt "${filesystem_left}" ]; then
            echo "ERROR: Not enough space available on filesystem. At least ${filesystem_left} MB free memory are needed."
            echo "Current free space = $filesystem_free MB"
            exit 1
        else
            echo "Swap will be increased to ${new_swap_size} MB"
            if ! change_swap $new_swap_size ; then
                echo "ERROR: failed to change swap size"
                exit 1
            fi
        fi

        calc_nodemem || return 1
    fi
  fi
}

calc_nodemem

if [[ $NODEMEM -gt $FreeToUse ]]; then
  echo "ERROR: Requested node memory setting is larger than usable free memory: $NODEMEM MB > $FreeToUse MB"
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

if [[ $UPDATE_DEPENDENCIES == true ]]; then
  npm install 
  # TODO this was used in the install script (not activated for some time). Is one of the options prefered?
  # npm ci --prefer-offline --no-audit --production
fi

# Rebuild Web App
npm run build
