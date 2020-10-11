# How to setup a Pimoroni PirateAudio HAT

These instructions are for the following Pimoroni PirateAudio HATs:

<https://shop.pimoroni.com/?q=pirate+audio>

The PirateAudio HATs use the same DAC as the hifiberry, so some of the instructions
from <https://github.com/chbuehlmann/RPi-Jukebox-RFID/wiki/HiFiBerry-Soundcard-Details> can be applied as well.

The `setup_pirateAudioHAT.sh` script can be used to set it up to work with Phoniebox.

## Install steps in writing

(Discussions regarding *Pirate Audio HAT* should take place in the same thread where the below instructions were taken from: [#950](https://github.com/chbuehlmann/RPi-Jukebox-RFID/issues/950)

NOTE: changes to the installation should find their way into the script `setup_pirateAudioHAT.sh`. Please create pull requests *after* having tested your changes. :)

1. Connect Pirate Audio Hat to your Raspberry Pi
2. Install Phoniebox (develop branch!)
3. Stop and disable the GPIO button service:
   `sudo systemctl stop phoniebox-gpio-buttons.service`
   `sudo systemctl disable phoniebox-gpio-buttons.service`
4. Add the following two lines to /boot/config.txt
   `gpio=25=op,dh`
   `dtoverlay=hifiberry-dac`
5. Add settings to /etc/asound.conf (create it, if it does not exist yet)
   ```
   pcm.hifiberry {
        type            softvol
        slave.pcm       "plughw:CARD=sndrpihifiberry,DEV=0"
        control.name    "Master"
        control.card    1
    }
    pcm.!default {
        type            plug
        slave.pcm       "hifiberry"
    }
    ctl.!default {
        type            hw
        card            1
    }
    ```
6. Add the following section to /etc/mpd.conf
   ```
   audio_output {
            enabled         "yes"
            type            "alsa"
            name            "HiFiBerry DAC+ Lite"
            device          "hifiberry"
            auto_resample   "no"
            auto_channels   "no"
            auto_format     "no"
            dop             "no"
    }
    ```
7. Set mixer_control name in /etc/mpd.conf
    `mixer_control      "Master"`
8. Enable SPI
    `sudo raspi-config nonint do_spi 0`
9. Install Python dependencies
    `sudo apt-get install python3-pil python3-numpy`
10. Install Mopidy plugins
    `sudo pip3 install Mopidy-PiDi pidi-display-pil pidi-display-st7789 mopidy-raspberry-gpio`
11. Add the following sections to /etc/mopidy/mopidy.conf:
    ```
    [raspberry-gpio]
    enabled = true
    bcm5 = play_pause,active_low,150
    bcm6 = volume_down,active_low,150
    bcm16 = next,active_low,150
    bcm20 = volume_up,active_low,150
    
    [pidi]
    enabled = true
    display = st7789
    ```
12. Enable access for modipy user
    `sudo usermod -a -G spi,i2c,gpio,video mopidy`
13. Reboot Raspberry Pi
