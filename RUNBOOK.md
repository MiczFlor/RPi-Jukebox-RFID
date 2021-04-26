# Phoniebox Runbook

This document describes how to set up a local development environment based on different hosts.

## Run Phoniebox in Docker image

Depending on your host environment (Mac, Linux or Windows), you might need to adapt some of those commands a little bit.

1. Pull the Phoniebox repository
1. `cd` into the root folder of your repository
1. Build the Docker image
    ```
    $ docker build -t phoniebox .
    ```
1. Once built, you need to execute `docker run` with some specific parameters depending on your host.

### Mac

```
$ brew install pulseaudio
$ brew services start pulseaudio

$ docker run -it --rm \
    -v ~/.config/pulse:/home/phoniebox/.config/pulse \
    -v /usr/local/Cellar/pulseaudio/14.2/etc/pulse/:/etc/pulse \
    -e PULSE_SERVER=docker.for.mac.localhost \
    --name phoniebox-app phoniebox
```

#### Resources & Troubleshooting

* https://stackoverflow.com/questions/54702179/how-to-access-mac-os-x-microphone-inside-docker-container
* https://stackoverflow.com/questions/40136606/how-to-expose-audio-from-docker-container-to-a-mac
* https://github.com/jessfraz/dockerfiles/blob/master/pulseaudio/Dockerfile

### Further resources

* https://github.com/mviereck/x11docker/wiki/Container-sound:-ALSA-or-Pulseaudio