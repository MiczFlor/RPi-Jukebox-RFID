# Phoniebox Runbook

This document describes how to set up a local development environment based on different hosts.

## Run Phoniebox in Docker image

Depending on your host environment (Mac, Linux or Windows), you might need to adapt some of those commands a little bit.

1. Pull the Phoniebox repository
1. Change into the root folder of your repository
1. Change into the `shared` folder and create a folder called `audiofolders`
1. Copy a set of MP3 files into this folder
1. Build the Docker image
    ```
    $ docker build -t phoniebox .
    ```
1. Once built, you need to execute `docker run` with some specific parameters depending on your host.
1. The command below connects your local files to the docker environment, so each update you do automatically reflects within the container.

### Mac

#### Prerequisites

```
$ brew install pulseaudio
$ brew services start pulseaudio
```

#### `docker run`

```
$ docker run -it --rm \
    -p 8080:80 \
    -v $(PWD)/htdocs:/home/pi/RPi-Jukebox-RFID/htdocs \
    -v $(PWD)/Phoniebox:/home/pi/RPi-Jukebox-RFID/Phoniebox \
    -v $(PWD)/shared/audiofolders:/home/pi/RPi-Jukebox-RFID/shared/audiofolders \
    -v ~/.config/pulse:/home/pi/RPi-Jukebox-RFID/.config/pulse \
    -v /usr/local/Cellar/pulseaudio/14.2/etc/pulse/:/etc/pulse \
    -e PULSE_SERVER=docker.for.mac.localhost \
    --name phoniebox-app phoniebox
```

## Test

The Dockerfile is defined to start all Phoniebox related services. It also directly opens
a tunnel into the Container with a `bash` commend. You can perform any kind of commands
there. Navigate to [http://localhost:8080](http://localhost:8080) which should show the 
Phoniebox WebUI.

## Resources & Troubleshooting

* https://stackoverflow.com/questions/54702179/how-to-access-mac-os-x-microphone-inside-docker-container
* https://stackoverflow.com/questions/40136606/how-to-expose-audio-from-docker-container-to-a-mac
* https://github.com/jessfraz/dockerfiles/blob/master/pulseaudio/Dockerfile

### Further resources

* https://github.com/mviereck/x11docker/wiki/Container-sound:-ALSA-or-Pulseaudio