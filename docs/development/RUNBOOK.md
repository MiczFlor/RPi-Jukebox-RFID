# Phoniebox Runbook

This document describes how to set up a local development environment based on different hosts.

Depending on your host environment (Mac, Linux or Windows), you might need to adapt some of those commands a little bit.

## Prerequisites

1. Install required software
    * Linux: [Docker](https://docs.docker.com/engine/install/debian/), [Compose](https://docs.docker.com/compose/install/)
    * Mac: [Docker & Compose](https://docs.docker.com/docker-for-mac/install/), [pulseaudio](https://devops.datenkollektiv.de/running-a-docker-soundbox-on-mac.html)
    * Windows: [Docker & Compose](https://docs.docker.com/docker-for-windows/install/), [pulseaudio](https://www.freedesktop.org/wiki/Software/PulseAudio/Ports/Windows/Support/)
1. Pull the Phoniebox repository
1. Change into the root folder of your repository
1. Change into the `shared` folder and create a folder called `audiofolders`
1. Copy a set of MP3 files into this folder

## Run development environment

In contrairy to how everything is set up on the Raspberry, it's good practice to isolate different components in different Docker images. They can be run individually or in combination. To do that, we use `docker-compose` (newer versions of Docker can also use `docker compose`)

Run all Docker containers at once. Based on your host system, you need to load the override as well.

### Linux

```
// Build Images
$ docker compose -f docker/docker-compose.yml -f docker/docker-compose.linux.yml build

// Run Docker Environment
$ docker compose -f docker/docker-compose.yml -f docker/docker-compose.linux.yml up

// Shuts down Docker containers and Docker network
$ docker compose -f docker/docker-compose.yml -f docker/docker-compose.linux.yml down
```

### Mac

Remember, pulseaudio is a prerequisite.

```
// Build Images
$ docker compose -f docker/docker-compose.yml -f docker/docker-compose.mac.yml build

// Run Docker Environment
$ docker compose -f docker/docker-compose.yml -f docker/docker-compose.mac.yml up

// Shuts down Docker containers and Docker network
$ docker compose -f docker/docker-compose.yml -f docker/docker-compose.mac.yml down
```

### Windows

1. Download [pulseaudio](https://www.freedesktop.org/wiki/Software/PulseAudio/Ports/Windows/Support/)
1. Uncompress somewhere in your user folder
1. Edit `$INSTALL_DIR/etc/pulse/default.pa`
1. Add the following line
    ```
    load-module module-native-protocol-tcp auth-ip-acl=127.0.0.1
    ```
1. Edit `$INSTALL_DIR/etc/pulse//etc/pulse/daemon.conf`, find the following line and change it to: 
    ```
    exit-idle-time = -1
    ```
1. Execute `$INSTALL_DIR/bin/pulseaudio.exe`
1. Run `cocker-compose`

```
// Build Images
$ docker compose -f docker/docker-compose.yml -f docker/docker-compose.mac.yml build

// Run Docker Environment
$ docker compose -f docker/docker-compose.yml -f docker/docker-compose.mac.yml up

// Shuts down Docker containers and Docker network
$ docker compose -f docker/docker-compose.yml -f docker/docker-compose.mac.yml down
```

## Test & Develop

The Dockerfile is defined to start all Phoniebox related services. 
At the moment, the `jukebox` container just starts into a `bash` state. You need to
tunnel into the container and start the jukebox daemon manually.

Navigate to [`http://localhost:8000`](http://localhost:8000) which should show the 
WebUI.

---

## Appendix

### Individual Docker Image

Run an indidual Docker container, e.g. `jukebox`. Similarly you could run `mpd` or `webui`.

The following command can be run on a Mac.

```
$ docker build -f docker/jukebox.Dockerfile -t jukebox .
$ docker run -it --rm \
    -v $(PWD)/src/jukebox:/home/pi/RPi-Jukebox-RFID/src/jukebox \
    -v $(PWD)/shared/audiofolders:/home/pi/RPi-Jukebox-RFID/shared/audiofolders \
    -v ~/.config/pulse:/root/.config/pulse \
    -v /usr/local/Cellar/pulseaudio/14.2/etc/pulse/:/etc/pulse \
    -e PULSE_SERVER=tcp:host.docker.internal:4713 \
    --name jukebox jukebox
```

### Resources

#### Mac

* https://stackoverflow.com/questions/54702179/how-to-access-mac-os-x-microphone-inside-docker-container
* https://stackoverflow.com/questions/40136606/how-to-expose-audio-from-docker-container-to-a-mac
* https://github.com/jessfraz/dockerfiles/blob/master/pulseaudio/Dockerfile

#### Windows

* https://stackoverflow.com/questions/52890474/how-to-get-docker-audio-and-input-with-windows-or-mac-host#
* https://arnav.jain.se/2020/enable-audio--video-in-docker-container/
* https://x410.dev/cookbook/wsl/enabling-sound-in-wsl-ubuntu-let-it-sing/
* https://research.wmz.ninja/articles/2017/11/setting-up-wsl-with-graphics-and-audio.html

#### Audio
* https://github.com/mviereck/x11docker/wiki/Container-sound:-ALSA-or-Pulseaudio
* https://mpd.fandom.com/wiki/PulseAudio
* https://stmllr.net/blog/streaming-audio-with-mpd-and-icecast2-on-raspberry-pi/

#### MPD
* https://stmllr.net/blog/streaming-audio-with-mpd-and-icecast2-on-raspberry-pi/
* https://github.com/Tob1asDocker/rpi-mpd
* https://github.com/vimagick/dockerfiles/tree/master/mpd

#### ZMQ

* https://codeblog.dotsandbrackets.com/using-zeromq-with-docker/