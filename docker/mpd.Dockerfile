FROM debian:bullseye-slim

RUN set -eux ; \
    apt-get update && apt-get install -y \
    alsa-utils \
    libasound2-dev \
    libasound2-plugins \
    pulseaudio \
    pulseaudio-utils \
    mpd mpc \
    --no-install-recommends \
	; \
	rm -rf /var/lib/apt/lists/*

ENV HOME /root

RUN mkdir ${HOME}/.config ${HOME}/.config/mpd ; \
    touch ${HOME}/.config/mpd/state
RUN mkdir -p /home/pi/RPi-Jukebox-RFID/shared/audiofolders

RUN usermod -aG audio,pulse,pulse-access root

VOLUME ${HOME}/.config/mpd

EXPOSE 6600

CMD [ ! -s ~/.config/mpd/pid ] && mpd --stdout --no-daemon ${HOME}/.config/mpd/mpd.conf
