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
> Depending on your hardware, this installation might last around 60 minutes (usually it's faster, 20-30 min). It refreshes the package index, installs Phoniebox dependencies and applies settings. Be patient and don't let your computer go to sleep. It might disconnect your SSH connection causing the interruption of the installation process. Consider starting the installation in a terminal multiplexer like 'screen' or 'tmux' to avoid this.

The Web App can upload files or complete folder trees, organize the audio
library, and delete files or folders, so Samba is disabled by default during
installation. Choose Samba when you also want direct network access to the
complete `shared` directory, including configuration files. See
[Samba](samba.md) for details.

Current Raspberry Pi OS images normally do not need a full operating system upgrade immediately after imaging, so the installer skips it by default. To opt in to `apt-get full-upgrade` and `autoremove`, prefix an installation command with:

```bash
UPDATE_RASPI_OS=true
```

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

The installer uses HTTPS and fetches only the selected branch with shallow history. Set `GIT_USE_SSH=true` to opt in to SSH access. The installed checkout remains a normal tracking branch, so `git pull` works as usual.

Developers who later need all branches, history and tags can fetch them explicitly:

```bash
git fetch --unshallow origin
git fetch origin --tags
```

> [!NOTE]
> The Installation of the official repository's release branches ([Stable Release](#stable-release) and [Pre-Release](#pre-release)) will deploy a pre-build bundle of the Web App.
> For another branch or a fork repository, the installer first looks for a CI bundle matching the exact commit and otherwise downloads the latest applicable pre-built release bundle. A local build is optional and disabled by default. See the developers [Web App](../developers/webapp.md) documentation for further details.

### Logs

To follow the installation closely, use this command in another terminal.

```bash
cd; tail -f INSTALL-<fullname>.log
```
