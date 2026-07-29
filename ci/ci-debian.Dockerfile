# Base Target to build and install all needed base configuration and packages. Specifie the needed platform with the docker '--platform XXX' option
ARG DEBIAN_CODENAME=trixie
ARG BASE_TEST_IMAGE=test-code
FROM debian:${DEBIAN_CODENAME}-slim AS base
ARG DEBIAN_CODENAME

ENV TERM=xterm DEBIAN_FRONTEND=noninteractive
ENV CI_RUNNING=true

# create RPi config files for test installation
RUN mkdir -p /boot/firmware && touch /boot/firmware/config.txt && echo "logo.nologo" > /boot/firmware/cmdline.txt

RUN echo "--- install packages (1) ---" \
  && apt-get update \
  && apt-get -y install \
    apt-utils \
    ca-certificates \
    curl \
  && echo "--- install Raspberry Pi archive keyrings ---" \
  && curl -fsSLo /tmp/raspbian-archive-keyring_20120528.4_all.deb \
    https://archive.raspbian.org/raspbian/pool/main/r/raspbian-archive-keyring/raspbian-archive-keyring_20120528.4_all.deb \
  && curl -fsSLo /tmp/raspberrypi-archive-keyring_2025.1+rpt1_all.deb \
    https://archive.raspberrypi.com/debian/pool/main/r/raspberrypi-archive-keyring/raspberrypi-archive-keyring_2025.1+rpt1_all.deb \
  && echo "eb2bc175ecfad128ece8222b42eefabd0a2846afd14f3af04364f4a047cbc88f  /tmp/raspbian-archive-keyring_20120528.4_all.deb" | sha256sum -c - \
  && echo "2e727149d7acb8cc7f604e66d0049161039c8aa1eaf1175e54f9e69d963d60e4  /tmp/raspberrypi-archive-keyring_2025.1+rpt1_all.deb" | sha256sum -c - \
  && apt-get -y install \
    /tmp/raspbian-archive-keyring_20120528.4_all.deb \
    /tmp/raspberrypi-archive-keyring_2025.1+rpt1_all.deb \
  && rm -f /tmp/raspbian-archive-keyring_20120528.4_all.deb \
    /tmp/raspberrypi-archive-keyring_2025.1+rpt1_all.deb \
  && echo "--- add sources ---" \
  && echo "deb [arch=armhf signed-by=/usr/share/keyrings/raspbian-archive-keyring.gpg] https://archive.raspbian.org/raspbian/ ${DEBIAN_CODENAME} main contrib non-free rpi" > /etc/apt/sources.list.d/raspi.list \
  && echo "deb [signed-by=/usr/share/keyrings/raspberrypi-archive-keyring.gpg] https://archive.raspberrypi.com/debian/ ${DEBIAN_CODENAME} main" >> /etc/apt/sources.list.d/raspi.list \
  && echo "--- install packages (2) ---" \
  && apt-get update \
  && apt-get -y upgrade \
  && apt-get -y install \
    build-essential \
    iproute2 \
    openssh-client \
    sudo \
    systemd \
    wireless-tools \
    wget \
    wpasupplicant \
  && rm -rf /var/lib/apt/lists/*

# Set NonInteractive for sudo usage in container. 'sudo' package needed
RUN echo 'debconf debconf/frontend select Noninteractive' | sudo debconf-set-selections
# ------

# Base Target for setting up a test user. user can be selected with the docker '--user YYY' option
FROM base AS test-user
ARG USER_NAME=pi
ARG USER_GROUP=$USER_NAME
ARG USER_ID=1000

ENV TEST_USER_GROUP=test
RUN groupadd --gid 1002 $TEST_USER_GROUP

RUN groupadd --gid 1000 $USER_GROUP \
  && useradd -u $USER_ID -g $USER_GROUP -G sudo,$TEST_USER_GROUP -d /home/$USER_NAME -m -s /bin/bash -p '$1$iV7TOwOe$6ojkJQXyEA9bHd/SqNLNj0' $USER_NAME \
  && echo "$USER_NAME ALL=(ALL) NOPASSWD: ALL" > /etc/sudoers.d/$USER_NAME

ENV XDG_RUNTIME_DIR=/run/user/$USER_ID DBUS_SESSION_BUS_ADDRESS=unix:path=/run/user/$USER_ID/bus
# ------

# Target for adding envs and scripts from the repo to test installation
FROM test-user AS test-code
ARG GIT_BRANCH
ARG GIT_USER

ENV GIT_BRANCH=$GIT_BRANCH GIT_USER=$GIT_USER

COPY --chown=root:$TEST_USER_GROUP --chmod=770 packages-core.txt ./

RUN echo "--- install internal packages ---" \
   && apt-get update \
   && sed 's/#.*//g' packages-core.txt | xargs apt-get -y install \
   && rm -rf /var/lib/apt/lists/*

ENV INSTALL_SCRIPT_PATH=/code

WORKDIR ${INSTALL_SCRIPT_PATH}
COPY --chown=root:$TEST_USER_GROUP --chmod=770 installation/install-jukebox.sh ./

WORKDIR ${INSTALL_SCRIPT_PATH}/tests
COPY --chown=root:$TEST_USER_GROUP --chmod=770 ci/installation/*.sh ./
# ------


# Target for applying latest updates (should not be cached!)
FROM $BASE_TEST_IMAGE AS test-update
RUN apt-get update \
  && apt-get -y upgrade \
  && rm -rf /var/lib/apt/lists/*
# ------
