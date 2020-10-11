# GPIO CONTROL

This service enables the control of different GPIO input & output devices for controlling the Phoniebox.
It uses to a configuration file to configure the active devices.

## How to create and run the service?
* The service can be activated during installation with the installscript.
* If the service was not activated during installation, you can alternatively use `sudo install.sh` in this folder.

## How to edit configuration files?
The configuration file is located here: `~/RPi-Jukebox-RFID/settings/gpio_settings.ini` 
Editing the configuration file and restarting the service will activate the new settings.

In the following the different devices are described. 
Each device can have actions which correspond to function calls.
Up to now the following input devices are implemented:
* **Button**: 
   A simple button which has a hold and repeat functionality as well as a delayed action. 
   It can be configured using the keywords: Pin, hold_time, functionCall

* **RotaryEncoder**:
    Control of a rotary encoder, for example KY040, see also in 
    [Wiki](https://github.com/chbuehlmann/RPi-Jukebox-RFID/wiki/Audio-RotaryKnobVolume)
    it can be configured using pinA, pinB, functionCallIncr, functionCallDecr, timeBase=0.1

* **TwoButtonControl**:
    This Device uses two Buttons and implements a third action if both buttons are pressed together.
