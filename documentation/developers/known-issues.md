# Known Issues

## Browsers

The Web UI will **not** work with Firefox, due to an issue with websockets and pyzmq. Please use a different
browser for now.

## Configuration

In `jukebox.yaml` (and all other config files): do not use relative paths with `~/some/dir`.
Always use relativ path from settingsfile '../../'

**Sole** exception is in `playermpd.mpd_conf`.
