# Phoniebox Runbook

This document describes how to set up a local development environment based on different hosts.

## Run Phoniebox in Docker image on Linux

Depending on your host environment (Mac, Linux or Windows), you might need to adapt some of those commands a little bit.

1. Pull the Phoniebox repository
1. Change into the root folder of your repository
1. Change into the `shared` folder and create a folder called `audiofolders`
1. Copy a set of MP3 files into this folder

### `docker compose`

Run all Docker containers at once.

```
$ docker compose build
$ docker compose up
...
$ docker compose down
```

The Dockerfile is defined to start all Phoniebox related services. 
At the moment, the `jukebox` container just starts into a `bash` state. You need to
tunnel into the container and start the jukebox daemon manually.

Navigate to [`http://localhost:8080`](http://localhost:8080) which should show the 
WebUI.

## Other hosts

### Mac

#### Prerequisites

```
$ brew install pulseaudio
$ brew services start pulseaudio
```

#### `docker run`

Run an indidual Docker container, e.g. `jukebox`. Similarly you could run `mpd` or `webui`.

```
$ docker build -f jukebox.Dockerfile -t jukebox .
$ docker run -it --rm \
    -v $(PWD)/Phoniebox:/home/pi/RPi-Jukebox-RFID/Phoniebox \
    -v $(PWD)/shared/audiofolders:/home/pi/RPi-Jukebox-RFID/shared/audiofolders \
    -v ~/.config/pulse:/root/.config/pulse \
    -v /usr/local/Cellar/pulseaudio/14.2/etc/pulse/:/etc/pulse \
    -e PULSE_SERVER=docker.for.mac.localhost \
    --name jukebox jukebox
```

#### Resources & Troubleshooting

* https://stackoverflow.com/questions/54702179/how-to-access-mac-os-x-microphone-inside-docker-container
* https://stackoverflow.com/questions/40136606/how-to-expose-audio-from-docker-container-to-a-mac
* https://github.com/jessfraz/dockerfiles/blob/master/pulseaudio/Dockerfile

### Windows

It's complicated

#### Resources

* https://stackoverflow.com/questions/52890474/how-to-get-docker-audio-and-input-with-windows-or-mac-host

## Further resources

### Audio
* https://github.com/mviereck/x11docker/wiki/Container-sound:-ALSA-or-Pulseaudio
* https://mpd.fandom.com/wiki/PulseAudio
* https://stmllr.net/blog/streaming-audio-with-mpd-and-icecast2-on-raspberry-pi/

### MPD
* https://stmllr.net/blog/streaming-audio-with-mpd-and-icecast2-on-raspberry-pi/
* https://github.com/Tob1asDocker/rpi-mpd
* https://github.com/vimagick/dockerfiles/tree/master/mpd

### ZMQ

* https://codeblog.dotsandbrackets.com/using-zeromq-with-docker/