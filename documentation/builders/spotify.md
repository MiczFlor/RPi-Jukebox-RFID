# Spotify

Phoniebox can use Spotify next to the local MPD library. Saved albums,
playlists, Liked Songs, or a parent-curated selection appear in the Web App
and can be assigned to RFID cards through the same library workflow as local
content.

## How It Works

Spotify support combines two separate integrations:

1. [librespot](https://github.com/librespot-org/librespot) is the Spotify
   Connect receiver. It downloads and renders audio through the same
   PulseAudio-compatible output used by MPD.
2. The official Spotify Web API supplies library metadata and controls
   playback on the librespot receiver.

The Web API does not provide the audio stream. Librespot does not provide the
library and arbitrary-URI control API needed by the Web App, so both parts
must be connected.

## Requirements

- A Spotify Premium account.
- A Spotify developer app owned by the person configuring Phoniebox.
- The same Spotify account connected to the Web App and the librespot
  receiver.
- A redirect URI that the browser can reach and that exactly matches the
  developer app configuration.

No Spotify client secret is stored. Phoniebox uses Authorization Code with
PKCE.

## Create The Spotify Developer App

1. Sign in to the
   [Spotify Developer Dashboard](https://developer.spotify.com/dashboard)
   with the Spotify account that will own the integration.
2. Create an app, select **Web API** when prompted, and copy its
   **Client ID**.
3. Add one redirect URI for the environment being configured:

   | Environment | Example redirect URI |
   | --- | --- |
   | Phoniebox with HTTPS | `https://phoniebox.example/api/v1/spotify/oauth/callback` |
   | Phoniebox through an SSH tunnel | `http://127.0.0.1:3000/api/v1/spotify/oauth/callback` |
   | Docker on the browser's computer | `http://127.0.0.1:3000/api/v1/spotify/oauth/callback` |

Spotify permits plain HTTP for loopback addresses. Normal host names require
HTTPS. The redirect URI is case-sensitive and its scheme, host, port, and
path must exactly match `players.spotify.redirect_uri`.

## Physical Phoniebox Setup

### Install

For a new installation, follow the regular
[Phoniebox installation guide](installation.md). When prompted:

1. Enable Spotify support.
2. Enter the developer app Client ID.
3. Register the displayed redirect URI in the Spotify dashboard and press
   Enter to accept it. Enter a different URI only for custom HTTPS or tunnel
   setups.
4. Choose a Spotify Connect device name or keep `Phoniebox`.

The installer downloads the pinned, checksum-verified librespot build for
ARMv7, ARM64, or AMD64, creates its user service, enables Spotify in
`shared/settings/jukebox.yaml`, and makes `jukebox-daemon` depend on
librespot. Spotify is not yet available on ARMv6 models; the installer warns
and continues without enabling it.

Source compilation is a recovery option rather than an automatic fallback.
To opt in when no release binary is available, start the installer with
`LIBRESPOT_ALLOW_SOURCE_BUILD=true`.

For an existing future3 installation, rerun the installer and select Spotify
support. This is preferred over only editing YAML because the librespot
binary and systemd units must also be installed.

Reboot after installation, or start the services explicitly:

```bash
systemctl --user daemon-reload
systemctl --user restart librespot jukebox-daemon
```

### Connect Librespot

Open an official Spotify app with the same Premium account. In the Spotify
Connect device picker, select the configured Phoniebox device and play or
pause one item. This creates librespot's credential cache and makes the
receiver available to the Web API.

### Connect The Web API

Open the Web App at the same origin used by the configured redirect URI, then
select **Settings > Spotify > Connect** and complete authorization in the
popup.

For a headless Phoniebox without HTTPS, create an SSH tunnel from the computer
running the browser:

```bash
ssh -L 3000:127.0.0.1:80 USER@PHONIEBOX_HOST
```

Keep the tunnel open, browse to <http://127.0.0.1:3000>, and select
**Connect**. Both the Spotify developer app and `jukebox.yaml` must use
`http://127.0.0.1:3000/api/v1/spotify/oauth/callback`. Choose another local
port in all three places if port 3000 is already in use.

### Verify The Services

```bash
systemctl --user status pipewire-pulse librespot jukebox-daemon
journalctl --user -b -u librespot
journalctl --user -b -u jukebox-daemon
```

The librespot log should show a successful Spotify session. The Web App
should report the account as connected and show the configured Spotify
Connect device name.

## Docker Development Setup

The Docker environment is intended for development, not deployment on a
Raspberry Pi. Complete the general
[Docker development setup](../developers/docker.md) first, including creation
of `shared/settings/jukebox.yaml`.

### Configure Spotify

Add or update this section in `shared/settings/jukebox.yaml`:

```yaml
players:
  spotify:
    enabled: true
    client_id: YOUR_SPOTIFY_CLIENT_ID
    redirect_uri: http://127.0.0.1:3000/api/v1/spotify/oauth/callback
    device_name: Phoniebox
    token_file: ../../shared/settings/spotify_tokens.json
    library_file: ../../shared/settings/spotify_library.json
```

The Docker librespot image advertises itself as `Phoniebox`, so
`device_name` must keep that value unless the container command is customized.
Restart the `jukebox` container after changing this file.

The Docker image uses the same verified release archive as the physical
installer. Forks that publish their own `librespot-builds` release can set
`LIBRESPOT_SOURCE_REPOSITORY=OWNER/RPi-Jukebox-RFID` before running Compose;
the upstream repository remains the fallback.

### Prepare Host Audio

MPD and librespot use the same host audio server. Spotify does not require a
second audio stack when MPD audio already works.

On macOS, install and start PulseAudio before starting Compose:

```bash
brew install pulseaudio
./docker/start_pulseaudio_mac.sh
```

Run the helper after each host reboot. It is idempotent and loads the TCP
module used by all three audio-aware containers.

On Linux, the Compose override mounts the current user's PulseAudio-compatible
socket. Run Compose as the logged-in desktop user, not with `sudo`, and verify
the socket before starting:

```bash
test -S "${XDG_RUNTIME_DIR}/pulse/native"
```

On Windows, configure PulseAudio as described in the
[Docker runbook](../developers/docker.md#windows). The base Compose file
connects through `host.docker.internal`.

### Start The Stack

Use the command for the host operating system.

macOS:

```bash
docker compose \
  -f docker/docker-compose.yml \
  -f docker/docker-compose.mac.yml \
  --profile spotify up -d --build
```

Linux:

```bash
docker compose \
  -f docker/docker-compose.yml \
  -f docker/docker-compose.linux.yml \
  --profile spotify up -d --build
```

Windows:

```bash
docker compose \
  -f docker/docker-compose.yml \
  --profile spotify up -d --build
```

Open <http://127.0.0.1:3000> after the containers are healthy.

### Authorize The Librespot Container

The first Docker start requires one interactive librespot authorization:

1. Read the receiver log and open its `Browse to:` URL:

   ```bash
   docker logs spotify
   ```

2. Complete Spotify login. The browser eventually redirects to an unserved
   `http://127.0.0.1/login?...` address. The failed page is expected. Copy the
   complete URL from the address bar; it contains a short-lived credential
   and should not be shared.
3. Attach with a simple custom detach key, paste the complete redirect URL,
   and press Enter:

   ```bash
   docker attach --detach-keys="ctrl-]" spotify
   ```

4. Press `Ctrl-]` to detach. Do not press `Ctrl-C`, which stops librespot.
5. Confirm that the log contains `Authenticated as`, then select
   **Phoniebox** once in an official Spotify app.

The interactive step is not repeated while the `spotify-cache` volume is
preserved.

### Connect The Web API

Open <http://127.0.0.1:3000>, select
**Settings > Spotify > Connect**, and complete the second authorization.
This authorization belongs to the Phoniebox Web API and is separate from the
librespot receiver authorization.

If **Connect** remains disabled after editing YAML, restart the backend:

```bash
docker restart jukebox
```

### Docker Persistence And Shutdown

The two authorization states are persisted separately:

- `spotify-cache` is a Docker volume containing librespot credentials.
- `shared/settings/spotify_tokens.json` contains the Web API refresh token.
- `shared/settings/spotify_library.json` contains curated entries and the
  selected library mode.

Normal container restarts, rebuilds, and `docker compose down` preserve these
files. `docker compose down -v` deletes the librespot credential volume and
requires receiver authorization again. Removing the JSON files from
`shared/settings` resets the corresponding Web App state.

Use the same Compose file selection used to start the stack when stopping it,
for example on macOS:

```bash
docker compose \
  -f docker/docker-compose.yml \
  -f docker/docker-compose.mac.yml \
  --profile spotify down
```

## Library And RFID Cards

The Web App separates the library into **Overview**, **Local**, and
**Spotify**. Local content has Albums and Folders views. Spotify content has
Albums, Playlists, and Tracks views.

Select the Spotify library mode under **Settings > Spotify**:

- **Account library** shows saved Spotify albums, owned or followed
  playlists, and Liked Songs.
- **Curated library** shows only albums, playlists, and tracks explicitly
  added with an `open.spotify.com` share link or Spotify URI.

In curated mode, use **Add link** and **Select** in the Spotify library to
manage the compilation. Switching modes, disconnecting OAuth, or restarting
Phoniebox does not delete curated entries or RFID card assignments.

Starting Liked Songs plays its first 100 tracks because Spotify limits a
single Web API playback request to 100 explicit track URIs.

Playing or assigning an item stores its provider and stable Spotify URI.
Existing MPD RFID cards remain valid because provider information is optional
on the existing commands.

## Configuration Reference

```yaml
players:
  spotify:
    enabled: true
    client_id: YOUR_SPOTIFY_CLIENT_ID
    redirect_uri: YOUR_EXACT_REDIRECT_URI
    device_name: Phoniebox
    token_file: ../../shared/settings/spotify_tokens.json
    library_file: ../../shared/settings/spotify_library.json
```

- `enabled` registers the Spotify player and catalog backend.
- `client_id` identifies the user-owned Spotify developer app.
- `redirect_uri` must exactly match the developer app and browser origin.
- `device_name` must exactly match the name advertised by librespot.
- `token_file` stores the Web API refresh token with owner-only permissions.
- `library_file` stores the account/curated mode and curated metadata.

Changing `client_id`, `redirect_uri`, or `device_name` requires a
`jukebox-daemon` or `jukebox` container restart.

## Troubleshooting

### Spotify Connect Device Is Not Available

Verify all of the following:

- librespot is running and authenticated;
- `players.spotify.device_name` exactly matches the advertised device;
- librespot and the Web App are connected to the same Spotify account;
- the device has been selected once in an official Spotify app.

Physical Phoniebox:

```bash
journalctl --user -b -u librespot
systemctl --user restart librespot jukebox-daemon
```

Docker:

```bash
docker ps --filter name=spotify
docker logs spotify
docker restart spotify jukebox
```

### Connect Is Disabled Or OAuth Fails

- Confirm `players.spotify.enabled` is `true`.
- Confirm the Client ID is correct; no client secret is required.
- Compare the redirect URI in the Spotify dashboard, `jukebox.yaml`, and the
  browser address character by character.
- Restart the backend after configuration changes.
- If the stored authorization is no longer valid, disconnect and reconnect
  under **Settings > Spotify**.

### Spotify Plays But Has No Sound

Check whether MPD also has sound. Both players use the same audio server.

Physical Phoniebox:

```bash
systemctl --user status pipewire-pulse
wpctl status
journalctl --user -b -u librespot
```

Docker on macOS:

```bash
./docker/start_pulseaudio_mac.sh
pactl list modules short | grep module-native-protocol-tcp
docker logs spotify
```

Docker on Linux:

```bash
test -S "${XDG_RUNTIME_DIR}/pulse/native"
docker logs spotify
```

Librespot should report `Using PulseAudioSink`. Restart the audio service or
container after correcting connectivity.

## Pinned Librespot Version

The installer and Docker image currently pin the post-0.8.0 recovery changes
from [librespot PR 1692](https://github.com/librespot-org/librespot/pull/1692).
Released 0.8.0 can lose its Spotify session after an idle server disconnect,
leaving a stale Connect device that fails on the next playback request.
