# How to set up a Phoniebox from scratch

1. [What you need](#1-what-you-need)
1. [Install Raspberry Pi OS](#2-install-raspberry-pi-os)
1. [Initial Boot](#3-initial-boot)
    * [a) with Terminal](#3a-with-terminal)
    * [b) with Desktop, Mouse & Keyboard](#3b-with-desktop-mouse--keyboard)
1. [Prepare hardware](#4-prepare-hardware)
1. [Audio](#5-audio)
    * [a) On-board headphone](#5a-on-board-headphone)
    * [b) USB sound card](#5b-usb-sound-card)
1. [Install Phoniebox software](#6-install-phoniebox-software)
1. [Verify Phoniebox setup](#7-verify-phoniebox-setup)

---

## 1. What you need

All parts marked with a star (*) are optional but improve the overall experience. All linked components are examples but have proven to work together. You are free to choose different equipment.

1. [Micro SD Card](https://amzn.to/3do7KJr) (e.g. 32 GB)
1. Raspberry Pi
    * [Model 3 B+](https://amzn.to/2NGL7Fa) - recommended
    * [Model 4 B](https://amzn.to/2M0xtfJ) - could be a little overhead
    * (Model 1, 2, 3 and Zero are possible, but they are slower...)
1. [USB RFID Reader](https://amzn.to/3s47Iun)
1. [RFID Chips](https://amzn.to/3k78F2j) or [RFID Cards](https://amzn.to/3dplljG)
1. [Speakers with 3.5mm jack](https://amzn.to/3dnhmnV)

To improve the sound, we recommend:

* [Ground Loop Isolator](https://amzn.to/37nyZjK) *

Alternatively you can use an external sound card, but sometimes that doesn't seem to improve much:

* [USB Sound Card](https://amzn.to/3djaKqC) * - [Alternative](https://amzn.to/3u8guth)

---

## 2. Install Raspberry Pi OS

Before you can install the Phoniebox software, you need to prepare your Raspberry Pi and install 

1. Connect your Micro SD card (through a card reader) to your computer
1. [Download](https://www.raspberrypi.org/software/) the [Raspberry Pi Imager](https://www.raspberrypi.org/blog/raspberry-pi-imager-imaging-utility/) and open it
1. Select **Raspberry Pi OS** as the operating system
1. Select your Micro SD card (your card will be formatted)
1. Click `Write`
1. Wait for the imaging process to be finished (it'll take a few minutes)

---

## 3. Initial Boot

If you are familiar with your computer's terminal, like PuTTY for Windows or the Terminal for Mac, we suggest to take this approach. Follow path [A] in this documentation.

If you don't know what all this means, you'll need a few other things for a one time set up only and follow path [B].

### 3a. with Terminal

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
1. Login into your Raspberry, username is `pi` and password is `raspberry`. If `raspberrypi.local` does not work, find out your Raspberry's IP address from your router.
    ```
    $ ssh pi@raspberrypi.local
    ```
1. Update the Pi's software. This may take a bit
    ```
    $ sudo apt update && sudo apt full-upgrade
    ```
1. Reboot with `sudo reboot`
1. Login again with SSH and open the Raspberry config
    ```
    $ sudo raspi-config
    ```
1. Update the following settings
    ```
    1 System Options
        S5 Boot / Auto Login -> B2 Console Autologin
        S6 Network at Boot -> Yes
    ```
1. Close the settings panel with `<Finish>`

### 3b. with Desktop, Mouse & Keyboard

1. Grab the following hardware
    1. Second computer (Linux, Mac or Windows)
    1. USB Mouse and USB Keyboard
    1. Micro SD Card Reader
    1. Screen with HDMI connection
1. Safely eject your SD card from your computer
1. Connect a USB mouse, a keyboard and a screen through HDMI
1. Insert the Micro SD card
1. Start your Raspberry Pi by attaching a power supply
1. Walk through the "Welcome to Raspberry Pi" wizard (the content of this wizard might have changed after this tutorial was created!)
    1. Set your locale
    1. Change your password
    1. Proceed with with screen settings
    1. Select your Wifi Network (You are being asked in the Phoniebox install routine whether you want to set up your Wifi again, we will skip this step then)
    1. Software Update (optional, recommended, takes a while)
    1. Reboot
1. Let's enable a few more settings
    1. Launch `Raspberry Pi Configuration` from the `Preferences` menu
    1. A window opens with the `System` tab selected
    1. Select `To CLI` for `Boot` option
    1. Select `Login as user 'pi'` for `Auto login` option
    1. Select `Wait for network` for `Network at Boot` option (optional, required for Spotify+ version)
    1. Navigate to the `Interfaces` tab
    1. Select `Enabled` next to `SSH`
    1. Click `OK`
1. Optional: If you like, you can **turn off Bluetooth** to reduce energy consumption (unless you want to use any Bluetooth devices with your Phoniebox)
1. Shutdown your Raspberry Pi (`Application > Logout > Shutdown`)
1. Disconnect mouse, keyboard and HDMI

---

## 4. Prepare hardware

If you want to install the **Spotify+ version**, [read this first](https://github.com/MiczFlor/RPi-Jukebox-RFID/wiki/Spotify-FAQ).

1. Connect the RFID Reader
1. Conntect USB Sound Card if available
1. Plug in the 3.5" speakers with the Ground Loop Isolator in between. If you have chosen the example speakers from above, you can power them either through the Raspberry Pi or through an external power source.
1. Boot your Raspberry Pi
1. Open a terminal in your second computer and login via SSH using the `pi` user and default password `raspberry`. If you see a question about authentication and fingerprint, type `yes` and hit `enter`
    ```
    ssh pi@raspberrypi.local
    ```

---

## 5. Audio

### 5a. On-board headphone

Installing with an external monitor (HDMI) can create a problem if you use the mini-jack audio out. The problem is that if you plug in a HDMI monitor an additional sound output is added and the index changes. This bothering behavior was introduced, when Raspberry Pi separated headphones jack and HDMI into two different devices in May 2020.
Also see [Troubleshooting: headphone audio unavailable after unplugging HDMI](https://github.com/MiczFlor/RPi-Jukebox-RFID/discussions/1300)

### 5b. USB sound card

1. Open the Raspberry config
    ```
    $ sudo raspi-config
    ```

1. Update the following settings
    ```
    1 System Options
        S2 Audio -> 1 USB Audio
    ```
1. Close the settings panel with `<Finish>`
1. Make your soundcard the primary sound device. To update the sound card priority order, edit the following file:
    ```
    $ sudo nano /usr/share/alsa/alsa.conf
    ```
1. Find the following variables and change their value from `0` to `1`
    ```
    defaults.ctl.card 0
    defaults.pcm.card 0

    // to

    defaults.ctl.card 1
    defaults.pcm.card 1
    ```
1. Reboot
1. Test your audio! Check if you hear white noise in stereo when running the following command from your connected speakers. If not, refer to this [resource](https://learn.adafruit.com/usb-audio-cards-with-a-raspberry-pi/instructions) to troubleshoot.
    ```
    speaker-test -c2
    ```

---

## 6. Install Phoniebox software

Run the following command in your SSH terminal and follow the instructions

```
cd; rm buster-install-*; wget https://raw.githubusercontent.com/MiczFlor/RPi-Jukebox-RFID/master/scripts/installscripts/buster-install-default.sh; chmod +x buster-install-default.sh; ./buster-install-default.sh
```

1. `Yes` to `Continue interactive installation`
1. `No` to the `Wifi Setting step` - it's already set!
1. `Speaker` to `CONFIGURE AUDIO INTERFACE (iFace)`
1. Setup Spotify (optional)
    1. You need to generate your personal Spotify client ID and secret
    1. Visit the [Mopidy Spotify Authentication Page](https://mopidy.com/ext/spotify/#authentication)
    1. Click the button `Authenticate Mopidy with Spotify`
    1. Login to Spotify with your credentials
    1. Once logged in, the code snippet on the website is updated with your `client_id` and `client_secret`
    1. Provide your Spotify `username`, `password` and paste your `client_id` and `client_secret` into your terminal
1. `Yes` to `CONFIGURE MPD`
1. `Yes` to `FOLDER CONTAINING AUDIO FILES`
1. Optional: In this scenario, we do not install GPIO buttons, so feel free to choose `No`
1. `Yes` to `Do you want to start the installation?`
1. ... Wait a bit for the installation to happen ...
1. `Yes` to `Have you connected your RFID reader?`
1. `1` to select `1. USB-Reader`
1. Choose the `#` that resonates with your RFID reader, in our case `HXGCoLtd Keyboard`
1. `Yes` to `Would you like to reboot now?`

---

## 7. Verify Phoniebox setup

1. Open a browser in your computer and navigate to your static IP: `http://raspberrypi.local`
1. You should see the Phoniebox UI
1. In your navigation, choose `Card ID`
1. Swipe one card near your RFID reader. If `Last used Chip ID` is automatically updated (you might hear a beep) and shows a number, your reader works
1. Verify Spotify (optional)
    1. Click `Spotify+` in the menu
    1. Mopidy opens, a second web player which was also installed
    1. You should be able to search and play Spotify content here
