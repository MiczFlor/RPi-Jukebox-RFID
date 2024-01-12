# Installing Phoniebox future3

## Install Raspberry Pi OS Lite

> [!IMPORTANT]
> Currently, the installation does only work on Raspberry Pi's with ARMv7 and ARMv8 architecture, so 2, 3 and 4! Pi 1 and Zero's are currently unstable and will require a bit more work! Pi 4 and 5 are an excess ;-)

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

<details>

<summary>In case you forgot to customize the OS settings, follow these instructions after RPi OS has been written to the SD card.</summary>

### Pre-boot preparation

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

## Install Phoniebox software

Run a following command in your SSH terminal and follow the instructions.
After successful installation, continue with [configuring your Phoniebox](configuration.md).

> [!TIP]
> Depending on your hardware, this installation might last
around 60 minutes (usually it's faster). It updates OS
packages, installs Phoniebox dependencies and registers
settings. Be patient and don't let your computer go to
sleep. It might disconnect your SSH connection causing
the interruption of the installation process.
Consider starting the installation in a terminal
multiplexer like 'screen' or 'tmux' to avoid this.

### Stable Release
This will install the latest **stable release** from the branch *future3/main*.

```bash
cd; bash <(wget -qO- https://raw.githubusercontent.com/MiczFlor/RPi-Jukebox-RFID/future3/main/installation/install-jukebox.sh)
```



### Pre-Release
This will install the latest **pre-release** from the branch *future3/develop*.

```bash
cd; GIT_BRANCH='future3/develop' bash <(wget -qO- https://raw.githubusercontent.com/MiczFlor/RPi-Jukebox-RFID/future3/develop/installation/install-jukebox.sh)
```

### Development
To install directly from a specific branch and/or a different repository specify the variables like this. Make sure you also update the URL accordingly to the branch and fork used.
> [!IMPORTANT]
>A fork repository must be named '*RPi-Jukebox-RFID*' like the official repository

```bash
cd; GIT_USER='MiczFlor' GIT_BRANCH='future3/develop' bash <(wget -qO- https://raw.githubusercontent.com/MiczFlor/RPi-Jukebox-RFID/future3/develop/installation/install-jukebox.sh)
```

> [!NOTE]
> For all branches *except* the current Release `future3/main`, the Web App needs to be build locally on the Pi. This is part of the installation process.
> If you make changes to the Web App sources you need to rebuild it manually. See the developers [Web App](../developers/webapp.md) documentation.

### Logs
If you suspect an error you can monitor the installation process with

```bash
cd; tail -f INSTALL-<fullname>.log
```

