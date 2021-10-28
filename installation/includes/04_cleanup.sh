#!/usr/bin/env bash

cleanup() {
  sudo rm -rf /var/lib/apt/lists/*

  echo "DONE: cleanup"
}
