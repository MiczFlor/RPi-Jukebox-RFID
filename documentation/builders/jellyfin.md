# Jellyfin

Phoniebox can use a Jellyfin media server as an additional music source.
The Jellyfin player backend streams audio through MPD — no extra playback
daemon is installed.

## Requirements

- A Jellyfin server **12.0 or newer** with a music library.
- `EnableLegacyAuthorization` disabled on the server. That is the factory
  default of 12.0, and the server migration
  `20260531160000_DisableLegacyAuthorization` sets it on upgrade.
- A Jellyfin user with access to the music library. A dedicated Phoniebox user
  is recommended: the login token inherits that user's library permissions, so
  a restricted user only ever sees the albums that user may access.
- The user must be allowed to sign in from this device. Without the
  "Allow access from all devices" permission the server rejects the login, and
  the device id shown in the Jellyfin device list has to be added to the
  allowed devices.

API keys are not supported. Jellyfin 12 passes them through unrestricted, so an
API key would bypass every library permission.

## Installation

Run the installer and answer **yes** to the "Setup Jellyfin?" prompt.
You will be asked for:

1. **Server URL** — e.g. `http://jellyfin.local:8096`
2. **Username** and **password** of the Jellyfin user

The installer stores the credentials in `jukebox.yaml` and enables the plugin.
An existing token file and device id are kept when the installer runs again.

## Manual configuration

```yaml
# shared/settings/jukebox.yaml
players:
  jellyfin:
    enabled: true
    host: "http://jellyfin.local:8096"
    username: "phoniebox"
    password: "your-password"
    token_file: ../../shared/settings/jellyfin_token.json
    device_id: ""            # optional: set explicitly on a cloned SD card
    catalog_cache_ttl: 300   # optional: seconds the album catalog is cached (default 300)
    request_timeout: 30      # optional: seconds to wait for server responses (default 30)
```

The installer writes `catalog_cache_ttl` and `request_timeout` with their
default values into `jukebox.yaml` automatically, so both keys are always
present and can be tuned without a code change.

`token_file` holds the access token together with the user name and the device
id it was issued for, and is created with owner-only permissions. Set
`device_id` explicitly on a cloned SD card image or when several boxes share
the same Jellyfin user — the copy then signs in as a device of its own. A
changed user name or device id makes the box sign in again; a changed password
alone is not detected, and the existing session stays valid until it is revoked
in the Jellyfin dashboard.

Restart the daemon: `sudo systemctl restart jukebox-daemon`

## Use

### Web App

Open the **Library** page. A **Jellyfin** source tab appears with
**Albums**. Browse, play, and create RFID cards as with the local library.

The plugin is configured under **Settings → Jellyfin**: server address,
username, password, catalog cache TTL and request timeout. The password is
never displayed; enter a new value to change it.

### After a restart

MPD restores its queue when it starts, so a Jellyfin album keeps playing
after a reboot or a `systemctl restart jukebox-daemon`. The Jellyfin backend
claims that playback within a few seconds: the Start view then shows the
track metadata and the album cover from the local cover cache, as before the
restart. Covers that were downloaded once are reused and are not fetched
again; only a cover that is still missing is downloaded.

### RFID cards

```yaml
# shared/settings/cards.yaml
rfid_card_01:
  provider: "jellyfin"
  value: "service:jellyfin:album:<itemid>"

# or a single track:
rfid_card_02:
  provider: "jellyfin"
  value: "service:jellyfin:track:<itemid>"
```

## Troubleshooting

- **"No Jellyfin source tab"** — `players.jellyfin.enabled` is not `true`,
  wrong server URL, or the daemon needs a restart.
- **"Jellyfin rejected the credentials"** — check username and password and
  that the server is reachable from the Phoniebox.
- **"User is not allowed access from this device"** — the Jellyfin user may not
  sign in from this device. Allow all devices for that user, or add the device
  id from the Jellyfin device list to its allowed devices.
- **Playback starts but no sound** — check MPD audio output (Jellyfin streams
  are played by MPD).
- **Jellyfin source shows an error while local library works** — the Jellyfin
  server is offline or unreachable; the local MPD library is unaffected.
- **Cover and title of the restored song are missing after a restart** — the
  album cover is looked up as soon as the Jellyfin server answers. A server
  that is unreachable while the box boots delays that by up to a minute per
  attempt, and the cover itself is then served from the local cache.
- **Large library (1000+ albums) times out on first open** — building the
  initial album catalog takes several seconds per page (500 albums). The daemon
  warms the catalog in the background at start-up and the WebApp waits up
  to 60 s for catalog requests, so a freshly installed/restarted daemon serves
  the first library view from the warm cache. If you still see a timeout,
  check `players.jellyfin.request_timeout` (each page request must finish
  within it) and that the Jellyfin server is not busy scanning.

## Known limitations

- Playlists are not yet supported (Albums only).
- The access token is part of the MPD stream URL — MPD cannot send an
  `Authorization` header — and therefore also appears in MPD's playlist and
  state file. It is never exposed through any RPC method. Use a dedicated
  Phoniebox Jellyfin user whose permissions cover only the music library.
- Re-adding an item after a library re-scan on the Jellyfin server may change
  its item ID and invalidate previously stored card values.
