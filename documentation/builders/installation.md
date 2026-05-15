# Installing Phoniebox future3

## Install Raspberry Pi OS Lite

> [!IMPORTANT]
> All Raspberry Pi models are supported. For sufficient performance, **we recommend Pi 2, 3 or Zero 2** (`ARMv7` models). Because Pi 1 or Zero 1 (`ARMv6` models) have limited resources, they are slower (during installation and start up procedure) and might require a bit more work! Pi 4 and 5 are an excess ;-)

Before you can install the Phoniebox software, you need to prepare your Raspberry Pi.

This instruction uses the official [Raspberry Pi Imager](https://www.raspberrypi.com/software/). We recommend using the latest **Raspberry Pi OS Lite** image - Trixie.

### Raspberry Pi Imager

1. Connect a Micro SD card to your computer (preferable an SD card with high read throughput)
1. Start the Raspberry Pi Imager
1. Model: select "No filtering"
1. OS: select **Raspberry Pi OS (other)** and then **Raspberry Pi OS Lite** (64 bit, 32 bit should also work) - the version without Desktop environment
1. Storage: Select your Micro SD card (your card will be formatted)
1. Customize:
    * Hostname: choose hostname for the network (e.g. "phoniebox")
    * Localization: choose according to your location
    * User: choose a username and a password
    * Wifi: provide your wifi settings
    * Remote: enable SSH with "Use password authentication"
1. Click `Write`
1. Confirm the next warning about erasing the SD card with `Yes`
1. Wait for the imaging process to be finished (it'll take a few minutes)
1. Plug the SD into your Pi and optionally connect keyboard, monitor and mouse.

## Install Phoniebox software

Choose a version, run the corresponding install command in your SSH terminal and follow the instructions.

* [Stable Release](#stable-release)
* [Pre-Release](#pre-release)
* [Development](#development)

After a successful installation, [configure your Phoniebox](configuration.md).

> [!TIP]
> Depending on your hardware, this installation might last around 60 minutes (usually it's faster, 20-30 min). It updates OS packages, installs Phoniebox dependencies and applies settings. Be patient and don't let your computer go to sleep. It might disconnect your SSH connection causing the interruption of the installation process. Consider starting the installation in a terminal multiplexer like 'screen' or 'tmux' to avoid this.

### Stable Release

This will install the latest **stable release** from the *future3/main* branch.

```bash
cd; bash <(wget -qO- https://raw.githubusercontent.com/MiczFlor/RPi-Jukebox-RFID/future3/main/installation/install-jukebox.sh)
```

### Pre-Release

This will install the latest **pre-release** from the *future3/develop* branch.

```bash
cd; GIT_BRANCH='future3/develop' bash <(wget -qO- https://raw.githubusercontent.com/MiczFlor/RPi-Jukebox-RFID/future3/develop/installation/install-jukebox.sh)
```

### Development

You can also install a specific branch and/or a fork repository. Update the variables to refer to your desired location. (The URL must not necessarily be updated, unless you have actually updated the file being downloaded.)

> [!IMPORTANT]
> A fork repository must be named '*RPi-Jukebox-RFID*' like the official repository

```bash
cd; GIT_USER='MiczFlor' GIT_BRANCH='future3/develop' bash <(wget -qO- https://raw.githubusercontent.com/MiczFlor/RPi-Jukebox-RFID/future3/develop/installation/install-jukebox.sh)
```

> [!NOTE]
> The Installation of the official repository's release branches ([Stable Release](#stable-release) and [Pre-Release](#pre-release)) will deploy a pre-build bundle of the Web App.
> If you install another branch or from a fork repository, the Web App needs to be built locally. This is part of the installation process. See the the developers [Web App](../developers/webapp.md) documentation for further details.

### Logs

To follow the installation closely, use this command in another terminal.

```bash
cd; tail -f INSTALL-<fullname>.log
```
