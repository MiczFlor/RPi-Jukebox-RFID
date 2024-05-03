#!/usr/bin/env bash

usage() {
    echo -e "\nRebuild the Web App\n"
    echo "${BASH_SOURCE[0]} [-u] [-m SIZE]"
    echo "  -u      : Update NPM dependencies before rebuild (only necessary on first build or if package.json changed"
    echo "  -m SIZE : Set Node memory limit in MB (if omitted limit is deduced automatically and swap might be adjusted)"
    echo "  -v      : Increase verbosity"
    echo -e "\n\n"
}

UPDATE_DEPENDENCIES=false
VERBOSE=false

while getopts ":uhvm:" opt; do
    case ${opt} in
    u)
        UPDATE_DEPENDENCIES=true
        ;;
    m)
        NODEMEM="${OPTARG}"
        ;;
    v)
        VERBOSE=true
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
    sudo dphys-swapfile setup 1&>/dev/null || return 1
    sudo dphys-swapfile swapon || return 1
}

# Need to check free space and limit Node memory usage for PIs with little memory.
# Adjust swap if needed to have minimum memory available
calc_nodemem() {
    echo "calculate usable memory"
    # keep a buffer for the kernel etc.
    local mem_buffer=256

    local mem_total=$(grep MemTotal /proc/meminfo | awk '{print $2}')
    local mem_free=$(grep MemFree /proc/meminfo | awk '{print $2}')
    local swap_total=$(grep SwapTotal /proc/meminfo | awk '{print $2}')
    local swap_free=$(grep SwapFree /proc/meminfo | awk '{print $2}')
    local total_free=$((swap_free + mem_free))

    mem_total=$((mem_total / 1024))
    mem_free=$((mem_free / 1024))
    swap_total=$((swap_total / 1024))
    swap_free=$((swap_free / 1024))
    total_free=$((total_free / 1024))

    local free_to_use=$((total_free - mem_buffer))

    if [ "$VERBOSE" == true ]; then
        echo "  Total phys memory : ${mem_total} MB"
        echo "  Free phys memory  : ${mem_free} MB"
        echo "  Total swap memory : ${swap_total} MB"
        echo "  Free swap memory  : ${swap_free} MB"
        echo "  Free total memory : ${total_free} MB"
        echo "  Keep as buffer    : ${mem_buffer} MB"
        echo -e "  Free usable memory: ${free_to_use} MB\n"
    fi

    if [[ -z $NODEMEM ]]; then
        # mininum memory used for node
        local mem_min=512
        if [[ $free_to_use -gt $mem_min ]]; then
            NODEMEM=$free_to_use
        else
            echo "  WARN: Not enough memory left on system for node (usable ${free_to_use} MB, min. ${mem_min} MB)."
            echo "        Trying to adjust swap size ..."

            local add_swap_size=$((mem_min / 2))
            local new_swap_size=$((swap_total + add_swap_size))

            # keep a buffer on the filesystem
            local filesystem_needed=$((add_swap_size + 512))
            local filesystem_free=$(df -BM -P / | tail -n 1 | awk '{print $4}')
            filesystem_free=${filesystem_free//M}

            if [ "$VERBOSE" == true ]; then
                echo "  New swap size = $new_swap_size MB"
                echo "  Additional filesystem space needed = $filesystem_needed MB"
                echo "  Current free filesystem space = $filesystem_free MB"
            fi

            if [ "${filesystem_free}" -lt "${filesystem_needed}" ]; then
                echo "  ERROR: Not enough space available on filesystem for swap (free ${filesystem_free} MB, min. ${filesystem_needed} MB). Abort!"
                exit 1
            elif ! change_swap $new_swap_size ; then
                echo "  ERROR: failed to change swap size. Abort!"
                exit 1
            fi

            calc_nodemem || return 1
        fi

    elif [[ $NODEMEM -gt $free_to_use ]]; then
        echo "  ERROR: Requested node memory setting is larger than usable free memory: ${NODEMEM} MB > ${free_to_use} MB (free ${total_free} MB - buffer ${mem_buffer} MB). Abort!"
        exit 1
    fi
}

calc_nodemem

export NODE_OPTIONS=--max-old-space-size=${NODEMEM}

echo "Setting Node Options:"
env | grep NODE

if [[ $(uname -m) == armv6l ]]; then
    echo "
-----------------------------------------------------------
| You are running a hardware with limited resources.      |
| Building the Web App takes significantly more time.     |
| In case it fails, check the documentation               |
| to trouble shoot.                                       |
-----------------------------------------------------------
"
fi

if [[ $UPDATE_DEPENDENCIES == true ]]; then
    npm install --prefer-offline --no-audit
fi

build_output_folder="build"
# Rebuild Web App
rm -rf "${build_output_folder}.bak"
if [ -d "${build_output_folder}" ]; then
    mv -f "${build_output_folder}" "${build_output_folder}.bak"
fi
if ! npm run build ; then
    echo "ERROR: rebuild of Web App failed!"
    exit 1
fi
