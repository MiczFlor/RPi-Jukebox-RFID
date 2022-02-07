#!/usr/bin/env bash

# Helpers

# $1->start, $2->end
calc_runtime_and_print() {
  runtime=$(($2-$1))
  ((h=${runtime}/3600))
  ((m=(${runtime}%3600)/60))
  ((s=${runtime}%60))

  echo "Done in ${h}h ${m}m ${s}s."
}

run_with_timer() {
  local time_start=$(date +%s);

  $1; # Executes the function passed as an argument

  calc_runtime_and_print time_start $(date +%s) | tee /dev/fd/3
  echo "--------------------------------------"
}

_download_file_from_google_drive() {
  GD_SHARING_ID=${1}
  TAR_FILENAME=${2}
  wget --load-cookies /tmp/cookies.txt "https://docs.google.com/uc?export=download&confirm=$(wget --save-cookies /tmp/cookies.txt --keep-session-cookies --no-check-certificate 'https://docs.google.com/uc?export=download&id=${GD_SHARING_ID}' -O- | sed -rn 's/.*confirm=([0-9A-Za-z_]+).*/\1\n/p')&id=${GD_SHARING_ID}" -O ${TAR_FILENAME} && rm -rf /tmp/cookies.txt
  echo "Downloaded from Google Drive ID ${GD_SHARING_ID} into ${TAR_FILENAME}"
}

get_onboard_audio() {
  if grep -q -E "^dtparam=([^,]*,)*audio=(on|true|yes|1).*" ${RPI_BOOT_CONFIG_FILE}
  then
    echo 1
  else
    echo 0
  fi
}

check_os_type() {
  # Check if current distro is a 32 bit version
  # Support for 64 bit Distros has not been checked (or precisely: is known not to work)
  # All RaspianOS versions report as machine "armv6l" or "armv7l", if 32 bit (even the ARMv8 cores!)

  local os_type
  os_type=$(uname -m)

  echo "Checking OS type ... $os_type" | tee /dev/fd/3

  if [[ $os_type == "armv7l" ||  $os_type == "armv6l" ]]; then
    echo -e "  ... OK!\n" | tee /dev/fd/3
  else
    echo "ERROR: Only 32 bit operating systems supported. Please use a 32bit version of RaspianOS!" | tee /dev/fd/3
    exit 1
  fi

}
