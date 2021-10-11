#!/usr/bin/env bash

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
