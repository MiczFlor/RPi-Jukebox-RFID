# Phoniebox Runbook

This document describes how to set up a local development environment based on different hosts.

## Docker

#### Resources

* https://github.com/mviereck/x11docker/wiki/Container-sound:-ALSA-or-Pulseaudio

### Mac

```
$ brew install pulseaudio
$ brew services start pulseaudio

$ docker run -it --rm \
    -v ~/.config/pulse:/home/phoniebox-daemon/.config/pulse \
    -v /usr/local/Cellar/pulseaudio/14.2/etc/pulse/:/etc/pulse \
    -e PULSE_SERVER=docker.for.mac.localhost \
    --name phoniebox-daemon-app phoniebox-daemon
```

#### Resources

* https://stackoverflow.com/questions/54702179/how-to-access-mac-os-x-microphone-inside-docker-container
* https://stackoverflow.com/questions/40136606/how-to-expose-audio-from-docker-container-to-a-mac
* https://github.com/jessfraz/dockerfiles/blob/master/pulseaudio/Dockerfile