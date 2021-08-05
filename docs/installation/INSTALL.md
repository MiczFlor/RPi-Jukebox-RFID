Installing Phoniebox future3
============================

## 1. Install Raspberry Pi OS Lite

Before you can install the Phoniebox software, you need to prepare your Raspberry Pi and install 

1. Connect your Micro SD card (through a card reader) to your computer
1. [Download](https://www.raspberrypi.org/software/) the [Raspberry Pi Imager](https://www.raspberrypi.org/blog/raspberry-pi-imager-imaging-utility/) and open it
1. Select **Raspberry Pi OS Lite** (without desktop environment) as the operating system
1. Select your Micro SD card (your card will be formatted)
1. Click `Write`
1. Wait for the imaging process to be finished (it'll take a few minutes)

---

## 2. Initial Boot

You will need a terminal, like PuTTY for Windows or the Terminal for Mac to proceed with the next steps.

1. Open a terminal of your choice
1. Insert your card again if it has been ejected automatically
1. Navigate to your SC card e.g., `cd /Volumes/boot` for Mac or `D:` for Windows
1. Enable SSH by adding a simple file
    ```
    $ touch ssh
    ```
1. Set up your Wifi connection
    * Mac
        ```
        $ nano wpa_supplicant.conf
        ```
    * Windows
        ```
        D:\> notepad wpa_supplicant.conf
        ```
1. Insert the following content, update your country, Wifi credentials and save the file.
    ```
    country=DE
    ctrl_interface=DIR=/var/run/wpa_supplicant GROUP=netdev
    update_config=1

    network={
        ssid="network-name"
        psk="network-password"
    }
    ```
1. Eject your SD card and insert it into your Raspberry Pi
1. Start your Raspberry Pi by attaching a power supply
1. Login into your Raspberry Pi, username is `pi` and password is `raspberry`. If `raspberrypi.local` does not work, find out your Raspberry Pi's IP address from your router.

## 3. Install Phoniebox software

Run the following command in your SSH terminal and follow the instructions

```
cd; bash <(wget -qO- https://raw.githubusercontent.com/MiczFlor/RPi-Jukebox-RFID/future3/develop/installation/install-jukebox.sh)
```
