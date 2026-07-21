# Trixie and PipeWire Branch Review

## Review Scope

This document records the review and resolution of
`future3/trixie-pipewire`. The original review was performed at `84b22350`;
the migration was then corrected and rewritten from
`origin/future3/develop`.

| Item | Value |
| --- | --- |
| Review date | 2026-07-21 |
| Original reviewed head | `84b22350` |
| Rewritten implementation head | `3e259701` |
| Merge base | `b44bd892` |
| Implementation commits | 18 |
| Implementation files changed | 41 |
| Merge assessment | Automated checks passed; Trixie hardware validation pending |

## Resolved Findings

### Bluetooth Hot-Connect Buttons

**Status:** Resolved

Sound-card callbacks now receive `(device_name, is_bluetooth)`. The audio
monitor derives `is_bluetooth` from the stable `device.api == bluez5` and
`device.bus == bluetooth` properties, so both PipeWire and PulseAudio-style
drivers work. Non-Bluetooth cards do not activate media-button listeners.

Mocked tests cover startup discovery, hot connection, PipeWire and PulseAudio
driver values, non-Bluetooth ALSA cards, and unknown card indices.

### Shutdown Audio Ordering

**Status:** Resolved

`jukebox-daemon.service` now lists `pipewire-pulse.service` in both `Requires`
and `After`. Inverse shutdown ordering keeps the audio service available while
the daemon plays its synchronous shutdown jingle and restores the volume.

The service file is parsed by an automated regression test.

### Trixie Installer and ARM64 CI

**Status:** Resolved

The installer image bootstraps the current Raspbian and Raspberry Pi keyring
packages over HTTPS after verifying pinned SHA-256 checksums. Apt sources use
the installed `signed-by` keyrings, and the Raspbian source is restricted to
ARMHF.

The workflow now runs the complete five-scenario installer matrix for both
`linux/arm/v7` and `linux/arm64`.

### Git Ownership Validation

**Status:** Resolved

The installer verifies `.git` ownership without asserting a mode. Both `755`
and umask-derived `775` directories pass, while an owner mismatch fails.

### Documentation Migration

**Status:** Resolved

The system and audio guides use current PipeWire terminology and commands.
The audio configuration tool is documented as selecting primary and secondary
sinks only. The tracked API reference was regenerated after the stack-neutral
callback names and removed processing features were finalized.

## History Result

The rewritten migration history:

* Keeps the five Mac Docker development commits.
* Moves the RDM6300 reader fix to `future3/fix-rdm6300-serial` at `9e06f789`.
* Combines the two PulseAudio-only processing-removal commits.
* Drops `9aa531be` while retaining the NetworkManager explanation.
* Folds installation documentation, CI cleanup, installer cleanup, and queued
  regression fixes into their behavior-specific commits.
* Contains no merge-only or fixup commits.

A local recovery branch,
`backup/future3-trixie-pipewire-pre-rewrite-20260721`, preserves the complete
pre-rewrite checkpoint.

## Verification Performed

The rewritten implementation passed:

* 46 Python tests on Python 3.12.
* Full `flake8` validation of `src` and `test`.
* Shell syntax and per-commit whitespace checks.
* Linux and macOS `docker compose config --quiet`.
* Focused Markdown lint.
* ARMv7 and ARM64 Trixie base and update image builds.
* Ownership validation for modes `755` and `775`, including a negative owner
  check.
* All five ARMv7 and all five ARM64 installer scenarios against the rewritten
  remote branch.

GitHub Actions run
[29826033134](https://github.com/MiczFlor/RPi-Jukebox-RFID/actions/runs/29826033134)
passed both architecture builds and all ten installer scenarios.

## Trixie Hardware Smoke Test

Run this check on Raspberry Pi OS Trixie with a Bluetooth device that exposes
media buttons and with a shutdown jingle configured:

1. Start the daemon with `systemctl --user start jukebox-daemon`.
2. Connect the Bluetooth device and verify that its play/pause and next buttons
   control playback.
3. Disconnect and reconnect the device, then verify both buttons again.
4. Confirm `systemctl --user show jukebox-daemon -p Requires -p After` lists
   `pipewire-pulse.service` in both properties.
5. Stop the daemon with `systemctl --user stop jukebox-daemon`.
6. Verify that the shutdown jingle plays, the previous volume is restored, and
   the daemon exits within the five-second graceful-shutdown window.

This hardware-only check was not run in the development environment.

## Merge Checklist

* [x] Fix PipeWire Bluetooth hot-connect button activation.
* [x] Restore shutdown ordering for the synchronous shutdown jingle.
* [x] Repair the Trixie installer base image.
* [x] Add focused runtime and service regression tests.
* [x] Add the full ARM64 installer lane.
* [x] Correct and regenerate the affected documentation.
* [x] Restore ownership-only validation for `.git`.
* [x] Clean up and split the commit history.
* [x] Complete both remote installer matrices.
* [x] Complete GitHub Actions run 29826033134.
* [ ] Pass the hardware smoke test on Raspberry Pi OS Trixie.
