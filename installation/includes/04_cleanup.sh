#!/usr/bin/env bash

_run_cleanup() {
    sudo rm -rf /var/lib/apt/lists/*
}

cleanup() {
    run_with_log_frame _run_cleanup "Cleanup"
}
