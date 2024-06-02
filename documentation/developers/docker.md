# Phoniebox Development Runbook for Docker environments

This document describes how to set up a local development environment
with Docker. It is useful to develop certain parts of the Phoniebox
application that do not directly require the Raspberry Pi hardware such
as GPIO. *Raspberry Pi OS* is based on Debian but comes with a lot of
special packages and a unique graphical interface. It is difficult to
mock a Raspberry Pi whithin a Docker container but we try to keep both
environments as close as possible. The Docker environment is not meant
to be deployed on the Raspberry Pi directly for performance reasons.

Depending on your host environment (Mac, Linux or Windows), you might
need to adapt some of those commands to your needs.

## Prerequisites

1. Install required software: Docker, Compose and pulseaudio
    * Check installation guide for [Mac](#mac), [Windows](#windows) or [Linux](#linux)

2. Pull the Jukebox repository:

    ```bash
    git clone https://github.com/MiczFlor/RPi-Jukebox-RFID.git
    ```

3. Create a jukebox.yaml file
    * Copy the `./resources/default-settings/jukebox.default.yaml` to `./shared/settings` and rename the file to `jukebox.yaml`.

    ```bash
    cp ./resources/default-settings/jukebox.default.yaml ./shared/settings/jukebox.yaml
    ```

    * Override/Merge the values from the following [Override file](../../docker/config/jukebox.overrides.yaml) in your `jukebox.yaml`.
    * **\[Currently required\]** Update all relative paths (`../..`) in to `/home/pi/RPi-Jukebox-RFID`.

4. Change directory into the `./shared/audiofolders`
    and copy a set of MP3 files into this folder (for more fun when
    testing).

## Run development environment

In contrary to how everything is set up on the Raspberry Pi, it's good
practice to isolate different components in different Docker images.
They can be run individually or in combination. To do that, we use
`docker-compose`.

### Mac

<details>

<summary>See details</summary>

1. [Install Docker & Compose (Mac)](https://docs.docker.com/docker-for-mac/install/)
1. Install pulseaudio
    1. Use Homebrew to install

        ```bash
        brew install pulseaudio
        ```

    1. Enable pulseaudio network capabilities. In an editor, open `/opt/homebrew/Cellar/pulseaudio/16.1/etc/pulse/default.pa` (you might need to adapt this path to your own system settings). Uncomment the following line:

        ```text
        load-module module-native-protocol-tcp
        ```

    1. Restart the pulseaudio service

        ```bash
        brew services restart pulseaudio
        ```

    1. If you have trouble with your audio, try these resources to troubleshoot: [[1]](https://gist.github.com/seongyongkim/b7d630a03e74c7ab1c6b53473b592712), [[2]](https://devops.datenkollektiv.de/running-a-docker-soundbox-on-mac.html), [[3]](https://stackoverflow.com/a/50939994/1062438)

1. Run `docker-compose`

    > [!NOTE]
    > In order for Pulseaudio to work properly with Docker on your Mac, you need to start Pulseaudio in a specific way. Otherwise MPD will throw an exception. See [Pulseaudio issues on Mac](#pulseaudio-issue-on-mac) for more info.

    1. Build libzmq for your host machine

        ```bash
        docker build -f docker/Dockerfile.libzmq -t libzmq:local .
        ```

    1. Build Images

        ```bash
        docker-compose -f docker/docker-compose.yml -f docker/docker-compose.mac.yml build
        ```

    1. Run Docker Environment -> Runs the entire Phoniebox environment

        ```bash
        docker-compose -f docker/docker-compose.yml -f docker/docker-compose.mac.yml up
        ```

    * Shuts down Docker containers and Docker network

        ```bash
        docker-compose -f docker/docker-compose.yml -f docker/docker-compose.mac.yml down
        ```

</details>

### Windows

<details>

<summary>See details</summary>

1. Install [Docker & Compose (Windows)](https://docs.docker.com/docker-for-windows/install/)

1. Download [pulseaudio](https://www.freedesktop.org/wiki/Software/PulseAudio/Ports/Windows/Support/)

1. Uncompress somewhere in your user folder

1. Edit `$INSTALL_DIR/etc/pulse/default.pa`

1. Add the following line

    ``` bash
    load-module module-native-protocol-tcp auth-ip-acl=127.0.0.1
    ```

1. Edit `$INSTALL_DIR/etc/pulse/daemon.conf`, find the
    following line and change it to:

    ``` bash
    exit-idle-time = -1
    ```

1. Execute `$INSTALL_DIR/bin/pulseaudio.exe`

1. Make sure Docker is running (e.g. start Docker Desktop)

1. Run `docker-compose`

    1. Build libzmq for your host machine

        ```bash
        docker build -f docker/Dockerfile.libzmq -t libzmq:local .
        ```

    1. Build Images

        ```bash
        docker-compose -f docker/docker-compose.yml build
        ```

    1. Run Docker Environment -> Runs the entire Phoniebox environment

        ```bash
        docker-compose -f docker/docker-compose.yml up
        ```

    * Shuts down Docker containers and Docker network

        ```bash
        docker-compose -f docker/docker-compose.yml down
        ```

</details>

### Linux

<details>

<summary>See details</summary>

1. Install Docker & Compose
    * [Docker](https://docs.docker.com/engine/install/debian/)
    * [Compose](https://docs.docker.com/compose/install/)
1. Make sure you don\'t use `sudo` to run your `docker-compose`. Check out
Docker\'s [post-installation guide](https://docs.docker.com/engine/install/linux-postinstall/) for more information.

1. Run `docker-compose`

    1. Build libzmq for your host machine

        ```bash
        docker build -f docker/Dockerfile.libzmq -t libzmq:local .
        ```

    1. Build Images

        ```bash
        docker-compose -f docker/docker-compose.yml -f docker/docker-compose.linux.yml build
        ```

    1. Run Docker Environment -> Runs the entire Phoniebox environment

        ```bash
        docker-compose -f docker/docker-compose.yml -f docker/docker-compose.linux.yml up
        ```

    * Shuts down Docker containers and Docker network

        ```bash
        docker-compose -f docker/docker-compose.yml -f docker/docker-compose.linux.yml down
        ```

</details>

## Test & Develop

The Dockerfile is defined to start all Phoniebox related services.

Open <http://localhost:3000> in your browser to see the Web App.

While the `webapp` container does not require a reload while working on
it (hot-reload is enabled), you will have to restart your `jukebox`
container whenever you make a change (in the Python code). Instead of
stopping and starting the `docker-compose` command, you can individually
restart your `jukebox` container. Update the below path with your
specific host environment.

``` bash
docker-compose -f docker/docker-compose.yml -f docker/docker-compose.[ENVIRONMENT].yml restart jukebox
```

## Known issues

The docker environment only exists to make development easier and
possible without a physical device. It won\'t replace it though.
Therefore, we currently accept certain issues related to the individual
Docker containers. Here is a list of known errors or weird behaviour
which you can easily ignore unless they prevent you from progressing. If
would be of course useful to get rid of them, but currently we make a
trade-off between a development environment and solving the specific
details.

### `mpd` container

#### Pulseaudio issue on Mac

If you notice the following exception while running MPD in Docker, it refers to a incorrect setup of your Mac host Pulseaudio.

```text
mpd      | ALSA lib pulse.c:242:(pulse_connect) PulseAudio: Unable to connect: Connection refused
mpd      | exception: Failed to read mixer for 'Global ALSA->Pulse stream': failed to attach to pulse: Connection refused
```

To fix the issue, try the following.

1. Stop your Pulseaudio service

    ```bash
    brew service stop pulseaudio
    ```

1. Start Pulseaudio with this command

    ```bash
    pulseaudio --load=module-native-protocol-tcp --exit-idle-time=-1 --daemon
    ```

1. Check if daemon is working

    ```bash
    pulseaudio --check -v
    ```

Everything else should have been set up properly as a [prerequisite](#mac)

* [Source](https://gist.github.com/seongyongkim/b7d630a03e74c7ab1c6b53473b592712)

#### `mpd` issues on Linux

If you have `mpd` running on your system, you need to stop it using:

``` bash
sudo systemctl stop mpd.socket
sudo mpd --kill
```

Otherwise you might get the error message:

``` bash
docker-compose -f docker-compose.yml -f docker-compose.linux.yml up
Starting mpd ...
Starting mpd ... error
(...)
Error starting userland proxy: listen tcp4 0.0.0.0:6600: bind: address already in use
```

Read these threads for details: [thread 1](https://unix.stackexchange.com/questions/456909/socket-already-in-use-but-is-not-listed-mpd) and [thread 2](https://stackoverflow.com/questions/5106674/error-address-already-in-use-while-binding-socket-with-address-but-the-port-num/5106755#5106755)

#### Other error messages

When starting the `mpd` container, you will see the following errors.
You can ignore them, MPD will run.

``` bash
mpd | exception: bind to '0.0.0.0:6600' failed (continuing anyway, because binding to '[::]:6600' succeeded): Failed to bind socket: Address already in use
mpd | exception: Failed to open '/root/.config/mpd/database': No such file or directory
mpd | exception: RTIOThread could not get realtime scheduling, continuing anyway: sched_setscheduler failed: Operation not permitted
mpd | avahi: Failed to create client: Daemon not running
```

You might also notice the following errors after the `mpd` Docker ran
for a while. Specifically the first error could fill up your console,
sometimes it stops with the second error message. It\'s not a problem,
sound continues to work. As a side effect, your CPU usage increases.
Just kill the process and restart.

``` bash
mpd | alsa_mixer: snd_mixer_handle_events() failed: Input/output error
mpd | exception: Failed to read mixer for 'My ALSA Device': snd_mixer_handle_events() failed: Input/output error
```

### `jukebox` container

Many features of the Phoniebox are based on the Raspberry Pi hardware.
This hardware can\'t be mocked in a virtual Docker environment. As a
result, a few plugins like RFID, GPIO or CPU temperature will throw
errors because they can\'t start successfully. Unless you want to
develop such plugins, you will be able to ignore these errors. The
plugin system is built in a way that the Jukebox daemon will come up. If
you want to develop plugins that require hardware support, you will have
to work on the hardware directly.

Typical errors and following exceptions to be ignored in the Docker
`jukebox` container are:

``` bash
jukebox    | 634:plugs.py           - jb.plugin            - MainThread      - ERROR    - Ignoring failed package load finalizer: 'rfid.finalize()'
jukebox    | 635:plugs.py           - jb.plugin            - MainThread      - ERROR    - Reason: FileNotFoundError: [Errno 2] No such file or directory: '/home/pi/RPi-Jukebox-RFID/shared/settings/rfid.yaml'
...
jukebox    | 171:__init__.py        - jb.host.lnx          - MainThread      - ERROR    - Error reading temperature. Canceling temperature publisher. FileNotFoundError: [Errno 2] No such file or directory: '/sys/class/thermal/thermal_zone0/temp'
...
jukebox    | 319:server.py          - jb.pub.server        - host.timer.cputemp - ERROR    - Publish command from different thread 'host.timer.cputemp' than publisher was created from 'MainThread'!
```

#### Pulseaudio and Volume issues

If you encounter the following error, refer to [Pulseaudio issues on Mac](#pulseaudio-issue-on-mac).

``` bash
jukebox  | 21.12.2023 08:50:09 -  629:plugs.py           - jb.plugin            - MainThread      - ERROR    - Ignoring failed package load finalizer: 'volume.finalize()'
jukebox  | 21.12.2023 08:50:09 -  630:plugs.py           - jb.plugin            - MainThread      - ERROR    - Reason: NameError: name 'pulse_control' is not defined
```

## Appendix

### Individual Docker Image

Run an individual Docker container, e.g. `jukebox`. Similarly you could
run `mpd` or `webapp`.

The following command can be run on a Mac.

``` bash
docker build -f docker/Dockerfile.jukebox -t jukebox .
docker run -it --rm \
    -v $(PWD)/src/jukebox:/home/pi/RPi-Jukebox-RFID/src/jukebox \
    -v $(PWD)/shared/audiofolders:/home/pi/RPi-Jukebox-RFID/shared/audiofolders \
    -v ~/.config/pulse:/root/.config/pulse \
    -v /usr/local/Cellar/pulseaudio/14.2/etc/pulse/:/etc/pulse \
    -e PULSE_SERVER=tcp:host.docker.internal:4713 \
    --name jukebox jukebox
```

## Testing ``evdev`` devices in Linux

To test the [event device capabilities](../builders/event-devices.md) in docker, the device needs to be made available to the container.

Mount the device into the container by configuring the appropriate device in a `devices` section of the `jukebox` service in the docker compose file. For example:

```yaml
  jukebox:
    ...
    devices:
      - /dev/input/event3:/dev/input/event3
```

### Resources

#### Mac

* <https://stackoverflow.com/questions/54702179/how-to-access-mac-os-x-microphone-inside-docker-container>
* <https://stackoverflow.com/questions/40136606/how-to-expose-audio-from-docker-container-to-a-mac>
* <https://github.com/jessfraz/dockerfiles/blob/master/pulseaudio/Dockerfile>

#### Windows

* <https://stackoverflow.com/questions/52890474/how-to-get-docker-audio-and-input-with-windows-or-mac-host#>
* <https://arnav.jain.se/2020/enable-audio--video-in-docker-container/>
* <https://x410.dev/cookbook/wsl/enabling-sound-in-wsl-ubuntu-let-it-sing/>
* <https://research.wmz.ninja/articles/2017/11/setting-up-wsl-with-graphics-and-audio.html>

#### Audio

* <https://github.com/mviereck/x11docker/wiki/Container-sound:-ALSA-or-Pulseaudio>
* <https://mpd.fandom.com/wiki/PulseAudio>
* <https://stmllr.net/blog/streaming-audio-with-mpd-and-icecast2-on-raspberry-pi/>

#### MPD

* <https://stmllr.net/blog/streaming-audio-with-mpd-and-icecast2-on-raspberry-pi/>
* <https://github.com/Tob1asDocker/rpi-mpd>
* <https://github.com/vimagick/dockerfiles/tree/master/mpd>

#### ZMQ

* <https://codeblog.dotsandbrackets.com/using-zeromq-with-docker/>
