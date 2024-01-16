# Installing Phoniebox future3

## Install Raspberry Pi OS Lite

> [!IMPORTANT]
>  All Raspberry Pi models are supported. For sufficient performance, **we recommend Pi 2, 3 or Zero 2** (`ARMv7` models). Because Pi 1 or Zero 1 (`ARMv6` models) have limited resources, they are slower (during installation and start up procedure) and might require a bit more work! Pi 4 and 5 are an excess ;-)

Before you can install the Phoniebox software, you need to prepare your Raspberry Pi.

1. Connect a Micro SD card to your computer (preferable an SD card with high read throughput)
2. Download the [Raspberry Pi Imager](https://www.raspberrypi.com/software/) and run it
3. Click on "Raspberry Pi Device" and select "No filtering"
4. Select **Raspberry Pi OS Lite (32-bit)** (without desktop environment) as the operating system. `future3` does not support 64bit kernels (`aarch64`).
5. Select your Micro SD card (your card will be formatted)
6. After you click `Next`, a prompt will ask you if you like to customize the OS settings
    * Click `Edit Settings`
    * Switch to the `General` tab
        * Provide a hostname. (When on Mac, you will be able to use it to connect via SSH)
        * Username
        * Password
        * Wifi
        * Set locale settings
    * Switch to the `Services` tab. Enable SSH with "Use password authentication"
    * Click `Save`
7. In the same dialog, click `Yes`
8. Confirm the next warning about erasing the SD card with `Yes`
9. Wait for the imaging process to be finished (it'll take a few minutes)


### Pre-boot preparation
<details>

<summary>In case you forgot to customize the OS settings, follow these instructions after RPi OS has been written to the SD card.</summary>

You will need a terminal, like PuTTY for Windows or the Terminal app for Mac to proceed with the next steps.

1. Open a terminal of your choice.
2. Insert your card again if it has been ejected automatically.
3. Navigate to your SD card e.g., `cd /Volumes/boot` for Mac or `D:` for Windows.
4. Enable SSH by adding a simple file.

    ```bash
    $ touch ssh
    ```

5. Set up your Wifi connection.

    *Mac*

    ```bash
    $ nano wpa_supplicant.conf
    ```

    *Windows*

    ```bash
    D:\> notepad wpa_supplicant.conf
    ```

6. Insert the following content, update your country, Wifi credentials and save the file.

    ```text
    country=DE
    ctrl_interface=DIR=/var/run/wpa_supplicant GROUP=netdev
    update_config=1

    network={
        ssid="network-name"
        psk="network-password"
    }
    ```

7. Eject your SD card and insert it into your Raspberry Pi.
8. Start your Raspberry Pi by attaching a power supply.
9. Login into your Raspberry Pi
   If `raspberrypi.local` does not work, find out your Raspberry Pi's IP address from your router.

</details>

### Pre-install preparation / workarounds

#### Workaround for network related features on Bookworm
<details>
With Bookworm the network settings have changed. Now "NetworkManager" is used instead of "dhcpcd".
This breaks breaks network related features like "Static IP", "Wifi Setup" and "Autohotspot".
Before running the installation, the network config has to be changed via raspi-config, to use the "old" dhcpcd network settings.

> [!IMPORTANT]
> If the settings are changed, your network will reset and Wifi will not be configured, so you lose ssh access via wireless network.
> So make sure you perform the following steps in a local terminal with a connected monitor and keyboard.

Change network config
* run `sudo raspi-config`
* select `6 - Advanced Options`
* select `AA - Network Config`
* select `dhcpcd`

If you need Wifi, add the information now
* select `1 - System Options`
* select `1 - Wireless LAN`
* enter Wifi information
</details>

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

