FROM debian:bullseye-slim

RUN set -eux ; \
    apt-get update && apt-get install -y \
    pulseaudio \
    pulseaudio-utils \
    mpd mpc \
    --no-install-recommends \
	; \
	rm -rf /var/lib/apt/lists/*


ARG UID
ARG USER
ARG HOME

RUN useradd -m -u ${UID} ${USER} || continue
RUN usermod -aG pulse ${USER}

USER ${USER}
RUN mkdir -p ${HOME}/.config/mpd ; \
    touch ${HOME}/.config/mpd/state

CMD mpd --stdout --no-daemon ${HOME}/.config/mpd/mpd.conf
