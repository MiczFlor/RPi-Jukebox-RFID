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
