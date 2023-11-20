# Base Target to build and install all needed base configuration and packages. Specifie the needed platform with the docker '--platform XXX' option
ARG DEBIAN_CODENAME=bookworm
ARG BASE_TEST_IMAGE=test-code
FROM debian:${DEBIAN_CODENAME}-slim as base
ARG DEBIAN_CODENAME

ENV CI_RUNNING=true TERM=xterm

# create pi configs to test installation
RUN touch /boot/config.txt
RUN echo "logo.nologo" > /boot/cmdline.txt

RUN export DEBIAN_FRONTEND=noninteractive \
  && echo "--- install packages (1) ---" \
  && apt-get update \
  && apt-get -y install \
    apt-utils \
    curl \
    gnupg \
  && echo "--- add sources ---" \
  && curl -fsSL http://raspbian.raspberrypi.org/raspbian.public.key | gpg --dearmor > /usr/share/keyrings/raspberrypi-raspbian-keyring.gpg \
  && curl -fsSL http://archive.raspberrypi.org/debian/raspberrypi.gpg.key | gpg --dearmor > /usr/share/keyrings/raspberrypi-archive-debian-keyring.gpg \
  && echo "deb [signed-by=/usr/share/keyrings/raspberrypi-raspbian-keyring.gpg] http://raspbian.raspberrypi.org/raspbian/ ${DEBIAN_CODENAME} main contrib non-free rpi" > /etc/apt/sources.list.d/raspi.list \
  && echo "deb [signed-by=/usr/share/keyrings/raspberrypi-archive-debian-keyring.gpg] http://archive.raspberrypi.org/debian/ ${DEBIAN_CODENAME} main" >> /etc/apt/sources.list.d/raspi.list \
  && echo "--- install packages (2) ---" \
  && apt-get update \
  && apt-get -y upgrade \
  && apt-get -y install \
    alsa-utils \
    build-essential \
    locales \
    openssh-client \
    sudo \
    systemd \
    wireless-tools \
    wget \
    wpasupplicant \
  && rm -rf /var/lib/apt/lists/*
# ------

# Base Target for setting up the default user. user can be selected with the docker '--user YYY' option
FROM base as user
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


# Target for setting up an alternativ user 'hans:wurst'. user can be selected with the docker '--user YYY' option
FROM user as test-user

RUN export USER_ALT=hans \
  && export USER_ALT_GROUP=wurst \
  && groupadd --gid 1001 $USER_ALT_GROUP \
  && useradd -u 1001 -g $USER_ALT_GROUP -G sudo,$TEST_USER_GROUP -d /home/$USER_ALT -m -s /bin/bash -p '$1$iV7TOwOe$6ojkJQXyEA9bHd/SqNLNj0' $USER_ALT \
  && echo "$USER_ALT ALL=(ALL) NOPASSWD: ALL" > /etc/sudoers.d/$USER_ALT
# ------


# Target for adding envs and scripts from the repo to test installation
FROM test-user as test-code
ARG GIT_BRANCH
ARG GIT_USER

ENV GIT_BRANCH=$GIT_BRANCH GIT_USER=$GIT_USER

# COPY --chown=root:$TEST_USER_GROUP --chmod=770 packages.txt packages-raspberrypi.txt ./

# RUN export DEBIAN_FRONTEND=noninteractive \
#   && echo "--- install internal packages ---" \
#   && apt-get update \
#   # remove resolvconf as installation will fail in container
#   && sed 's/#.*//g' packages.txt | sed 's/resolvconf//' | xargs apt-get -y install \
#   && sed 's/#.*//g' packages-raspberrypi.txt | xargs apt-get -y install \
#   && rm -rf /var/lib/apt/lists/*

ENV INSTALL_SCRIPT_PATH=/code

WORKDIR ${INSTALL_SCRIPT_PATH}
COPY --chown=root:$TEST_USER_GROUP --chmod=770 installation/install-jukebox.sh ./

WORKDIR ${INSTALL_SCRIPT_PATH}/tests
COPY --chown=root:$TEST_USER_GROUP --chmod=770 ci/installation/*.sh ./
# ------


# Target for applying latest updates (should not be cached!)
FROM $BASE_TEST_IMAGE as test-update
RUN export DEBIAN_FRONTEND=noninteractive \
  && apt-get update \
  && apt-get -y upgrade \
  && rm -rf /var/lib/apt/lists/*
# ------
