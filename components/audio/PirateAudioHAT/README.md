# How to setup a Pimoroni PirateAudio HAT

These instructions are for the following Pimoroni PirateAudio HATs:

<https://shop.pimoroni.com/?q=pirate+audio>

The PirateAudio HATs use the same DAC as the hifiberry, so some of the instructions
from <https://github.com/MiczFlor/RPi-Jukebox-RFID/wiki/HiFiBerry-Soundcard-Details> can be applied as well.

The `setup_pirateAudioHAT.sh` script can be used to set it up to work with Phoniebox.

Getting the display to work with Phoniebox should not be too difficult, but it's still a work in progress.

## Install steps in writing

(Discussions regarding *Pirate Audio HAT* should take place in the same thread where the below instructions were taken from: [#950](https://github.com/MiczFlor/RPi-Jukebox-RFID/issues/950)

NOTE: changes to the installation should find their way into the script `setup_pirateAudioHAT.sh`. Please create pull requests *after* having tested your changes :)

i have received my Pirate Audio HAT and everything is working (Sound, Display and Buttons).

Here are my installation steps:

1. Install phoniebox develop
2. Enable SPI
`sudo raspi-config nonint do_spi 0`
3. Run `components/audio/PirateAudioHAT/setup_pirateAudioHAT.sh`
4. Install plugins
 `sudo pip3 install Mopidy-PiDi pidi-display-pil pidi-display-st7789 mopidy-raspberry-gpio`
5. Edit mopidy configuration 
`sudo nano /etc/mopidy/mopidy.conf`

Add the following sections:
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
6. Enable access for modipy user
`sudo usermod -a -G spi,i2c,gpio,video mopidy`

7. Reboot

