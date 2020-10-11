#!/usr/bin/env python3

import sys
from signal import pause
import RPi.GPIO as GPIO

# script to activate and deactivate an amplifier, power led, etc. using a GPIO
# pin on power up / down

# see for an example implementation with a PAM8403 digital amplifier
# (PAM pin 12 connected to GPIO 26)
# https://github.com/chbuehlmann/RPi-Jukebox-RFID/wiki/Hardware-Hack-PAM8403-Poweroff

# change this value based on which GPIO port the amplifier or other devices are connected to
# Flexible Pinout
AMP_GPIO = 26
# Classic Pinout
# AMP_GPIO = 23

# setup RPi lib to control output pin
# we do not cleanup the GPIO because we want the pin low = off after program exit
# the resulting warning can be ignored
GPIO.setwarnings(False)
GPIO.setmode(GPIO.BCM)
GPIO.setup(AMP_GPIO, GPIO.OUT)


def set_amplifier(status):
    if status:
        print("Setting amplifier: ON")
        GPIO.output(AMP_GPIO, GPIO.HIGH)
    else:
        print("Setting amplifier: OFF")
        GPIO.output(AMP_GPIO, GPIO.LOW)


if __name__ == "__main__":
    try:
        set_amplifier(True)
        pause()
    except KeyboardInterrupt:
        # turn the relay off
        set_amplifier(False)
        print("\nExiting amplifier control\n")
        # exit the application
        sys.exit(0)
