# Known Issues

## Browsers

The Web UI will **not** work with Firefox, due to an issue with websockets and pyzmq. Please use a different
browser for now.

## Configuration

In `jukebox.yaml` (and all other config files): 
Always use relative path from settingsfile `../../`, but do not use relative paths with `~/`.

**Sole** exception is in `playermpd.mpd_conf`.
