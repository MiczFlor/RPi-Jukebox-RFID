# How to set up a Phoniebox from scratch

## What you need

All parts marked with a star (*) are optional but improve the overall experience. All linked components are examples but have proven to work together. You are free to choose different equipment.

1. [Micro SD Card](https://www.amazon.de/gp/product/B073JWXGNT) (e.g. 32 GB)
1. [Raspberry Pi]((https://www.amazon.de/gp/product/B07BDR5PDW)) (Model 1, 2, 3, 4, Zero)
1. [USB RFID Reader]((https://www.amazon.de/gp/product/B018OYOR3E))
1. [RFID Chips](https://www.amazon.de/gp/product/B078WRNLQZ) or [RFID Cards](https://www.amazon.de/gp/product/B00REFN24A)
1. [Speakers with 3.5mm jack](https://www.amazon.de/gp/product/B00JRW0M32)
1. [USB Sound Card](https://www.amazon.de/gp/product/B00C7LXUDY) * - [Alternative](https://www.amazon.de/gp/product/B00IRVQ0F8)
1. [Ground Loop Isolator](https://www.amazon.de/gp/product/B01LX0H29W) *

You'll need a few other things for the one time set up only.

1. Second computer (Linux, Max or Windows)
1. USB Mouse and USB Keyboard
1. Micro SD Card Reader
1. Screen with HTMI connection

Alternative: If you are able to connect your Raspberry Pi via a wired network interface (LAN), you can set it up via terminal (SSH) only.

## Install Raspberry Pi OS on a Micro SD card

Before you can install the Phoniebox software, you need to prepare your Raspberry Pi and install 

1. Connect your Micro SD card (through a card reader) to your computer
1. [Download](https://www.raspberrypi.org/software/) the [Raspberry Pi Imager](https://www.raspberrypi.org/blog/raspberry-pi-imager-imaging-utility/) and open it
1. Select an Operating System: **Raspberry Pi OS** (Recommended)
1. Select your Micro SD card (The card will be formatted)
1. Click "Write"
1. Wait for the imaging process to be finished (it'll take a few minutes) and eject your SD card

## Initial boot - Set up Wifi connection

1. Connect a USB mouse, a keyboard and a screen through HDMI
1. Insert the Micro SD card
1. Start your Raspberry Pi by attaching a power supply
1. Walk through the "Welcome to Raspberry Pi" wizard (the content of this wizard might have changed after this tutorial was created)
    1. Set your locale
    1. Change your password
    1. Proceed with with screen settings
    1. Select your Wifi Network (You are being asked in the Phoniebox install routine whether you want to set up your Wifi again, we will skip this step then)
    1. Software Update (optional, takes a while)
    1. Restart
1. Let's enable a few more settings
    1. Launch `Raspberry Pi Configuration` from the `Preferences` menu
    1. A window opens with the `System` tab selected
    1. Select `To CLI` for `Boot` option
    1. Select `Login as user 'pi'` for `Auto login` option
    1. Select `Wait for network` for `Network at Boot` option (optional, required for Spotify+ version)
    1. Navigate to the `Interfaces` tab
    1. Select `Enabled` next to `SSH`
    1. Click OK
1. Optional, but recommended: **Set up a static IP**
    1. Right click on the Wifi sympbol in the upper right corner of your application bar and choose `Wifi & Wired Network Settings`
    1. Configure `interface` and `wlan0`
    1. Check `Disabled IPv6` unless you want to provide a static IPv6 address
    1. Fill out `IPv4` abd `Router` (Gateway) options (keep `DNS Servers` and `DNS Search` empty)
    1. Click `Apply` and `Close`
1. Optional: If you like, you can **turn off Bluetooth** to reduce energy consumption (unless you want to use any Bluetooth devices with your Phoniebox)
1. Shutdown your Raspberry Pi (`Application > Logout > Shutdown`)

## Install Phoniebox software

If you want to install the **Spotify+ version**, [read this first](https://github.com/MiczFlor/RPi-Jukebox-RFID/blob/develop/docs/SPOTIFY-INTEGRATION.md).

1. While shut down, disconnect mouse, keyboard and HDMI
1. Connect RFID Reader
1. Conntect USB Sound Card, plug in the 3.5" speakers with the Ground Loop Isolator in between. If you have chose the example speakers from above, you can power them either through the Raspberry or through an external power source.
1. Boot your Raspberry Pi
1. Open a terminal in your second computer and login via SSH using the `pi` user and your static IP address. If you see a question about authentication and fingerprint, type `yes` and hit `enter`
    ```
    ssh pi@192.168.1.123
    ```

### Configure USB sound card

1. Configure your **USB sound card** ([Resource](https://learn.adafruit.com/usb-audio-cards-with-a-raspberry-pi/instructions)). Check if your sound card has been detected
    ```
    cat /proc/asound/modules

    // returns

    0 snd_bcm2835
    1 snd_usb_audio
    ```
1. Update the sound card priority order, edit the following file
    ```
    sudo nano /etc/modprobe.d/alsa-base.conf
    ```
1. Find the following lines and set their value to `1`
    ```
    defaults.ctl.card 0
    defaults.pcm.card 0

    // to

    defaults.ctl.card 1
    defaults.pcm.card 1
    ```
1. Reboot
1. Test your audio! Check if you hear white noise in stereo when running the following command from your connected speakers. If not, return to the resource linked above to troubleshoot.
    ```
    speaker-test -c2
    ```

### Phoniebox Install Script

Run the following command in your SSH terminal and follow the instructions

```
cd; rm buster-install-*; wget https://raw.githubusercontent.com/MiczFlor/RPi-Jukebox-RFID/master/scripts/installscripts/buster-install-default.sh; chmod +x buster-install-default.sh; ./buster-install-default.sh
```

1. `Yes` to `Continue interactive installation`
1. `No` to the `Wifi Setting step` - it's already set!
1. `Master` to `CONFIGURE AUDIO INTERFACE (iFace)`
1. Optional: Setup Spotify
    1. You need to generate your personal Spotify client id and secret
    1. Visit the [Mopidy Spotify Authentication Page](https://mopidy.com/ext/spotify/#authentication)
    1. Ignore the install guide and click the button `Authenticate Mopidy with Spotify`
    1. Login to Spotify with your credentials
    1. Once logged in, the code snippet on the website is updated with your `client_id` and `client_secret`
    1. Enter your Spotify `username`, `password`, `client_id` and `client_secret` into your terminal
1. `Yes` to `CONFIGURE MPD`
1. `Yes` to `FOLDER CONTAINING AUDIO FILES`
1. Optional: In this scenario, we do not install GPIO buttons, so feel free to choose `No`
1. `Yes` to `Do you want to start the installation?`
1. `Yes` to `Have you connected your RFID reader?`
1. `1` to select `1. USB-Reader`
1. Choose the `#` that resonates with your RFID reader, e.g. `HXGCoLtd Keyboard`
1. `Yes` to `Would you like to reboot now?`

## Verify Phoniebox installation

1. Open a browser in your computer and navigate to your static IP: `http://192.168.1.123`
1. You should see the Phoniebox UI
1. In your navigation, choose `Card ID`
1. Swipe one card near your RFID reader. If `Last used Chip ID` is automatically updated (you might hear a beep) and shows a number, your reader works