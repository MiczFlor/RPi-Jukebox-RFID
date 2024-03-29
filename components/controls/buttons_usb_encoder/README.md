# Buttons USB Encoder

Supports functionality of buttons which are connected via USB Encoder. The USB Encoder is the easy solution for anyone
who doesn't want to solder, but also wants arcade buttons.

Tested Devices:

* [IGames Zero Verzögerung USB Encoder](https://www.amazon.de/gp/product/B01N0GZQZI)
* [EG STARTS Nullverzögerung USB Encoder](https://www.amazon.de/gp/product/B075DFNK24)
* [Dragonrise inc. generic usb joystick](https://de.aliexpress.com/item/1005001700497245.html)

## Installation

1. Plug in your USB Encoder. You don't need to install any drivers. After plugging in, the USB encoder acts like an
   input device.
2. Navigate to your RPi-Jukebox home directory and run the script `setup-buttons-usb-encoder.sh` to set up your USB Encoder. Then choose the device and map the buttons.

   `cd ~/RPi-Jukebox-RFID`

   `./components/controls/buttons_usb_encoder/setup-buttons-usb-encoder.sh`

If you make a mistake at the first install you can "remap" the buttons:

* Stop the service: `sudo systemctl stop phoniebox-buttons-usb-encoder.service`
* Run the installation script again: `./components/controls/buttons_usb_encoder/setup-buttons-usb-encoder.sh`
* Restart the service: `sudo systemctl start phoniebox-buttons-usb-encoder.service`

### Possible Button Mappings

See the [GPIO documentation](../../gpio_control/README.md#functions) for possible mappings of functions and args.

## Schematics

![USB Encoder schematics](buttons-usb-encoder.jpg)

## Issues & Discussions

* <https://github.com/MiczFlor/RPi-Jukebox-RFID/issues/1156>
* <https://github.com/MiczFlor/RPi-Jukebox-RFID/discussions/2013>
