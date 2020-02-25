# GPIO CONTROL

This service enables the control of different GPIO input & output devices for controlling the Phoniebox.
It uses to a configuration file to configure the active devices.

In the following the different devices are described. 
Each device can have actions which correspond to function calls.
Up to now the following input devices are implemented:
* **Button**: 
   A simple button which has a hold and repeat functionality as well as a delayed action. 
   It can be configured using the keywords: Pin, hold_time, functionCall

* **RotaryEncoder**:
    Control of a rotary encoder, for example KY040, see also in 
    [Wiki](https://github.com/MiczFlor/RPi-Jukebox-RFID/wiki/Audio-RotaryKnobVolume)
    it can be configured using pinA, pinB, functionCallIncr, functionCallDecr, timeBase=0.1

* **TwoButtonControl**:
    This Device uses two Buttons and implements a thrid action if both buttons are pressed together.
    
    

## How to create and run the service?
* The configuration file needs to be placed in ~/.config/phoniebox/gpio_settings.ini
* The gpio_control.py needs to be started as a service. TODO

Editing the configuration file and restarting the service will activate the new settings

how to create a config file
what options can be used for what config vars
how to create tests and run them
milestones you would see for this component
often those who start something new, know best what would be nice to have and in what order. 
Because while they build it, they are cutting corners :) 
what is it that you think would be nice to have?

## How to edit configuration files?

### Which options do I have
The following
## Could this later be switched on and off in the web app? (see milestones below)
A nice
