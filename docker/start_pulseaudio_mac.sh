#!/usr/bin/env bash
#
# Ensure the host pulseaudio daemon is running with module-native-protocol-tcp
# loaded so containers can reach it via PULSE_SERVER=tcp:host.docker.internal:4713.
#
# Run before `docker compose up` and after each reboot. Idempotent: safe to
# re-run when pulse is already running and the TCP module is already loaded.

set -euo pipefail

TCP_MODULE="module-native-protocol-tcp"

if ! command -v pulseaudio >/dev/null 2>&1; then
    echo "pulseaudio not found. Install it first: brew install pulseaudio" >&2
    exit 1
fi

if ! pulseaudio --check 2>/dev/null; then
    echo "Starting pulseaudio with ${TCP_MODULE}..."
    pulseaudio --load="${TCP_MODULE}" --exit-idle-time=-1 --daemon
    exit 0
fi

if pactl list modules short 2>/dev/null | grep -q "${TCP_MODULE}"; then
    echo "pulseaudio already running with ${TCP_MODULE} loaded."
    exit 0
fi

echo "pulseaudio running; loading ${TCP_MODULE}..."
pactl load-module "${TCP_MODULE}" >/dev/null
echo "Done."
