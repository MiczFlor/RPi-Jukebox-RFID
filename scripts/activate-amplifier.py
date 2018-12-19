#!/usr/bin/python3

import sys
import time
from signal import pause
import RPi.GPIO as GPIO

# script to activate and deactivate an amplifier, power led, etc. using a GPIO pin on power up / down

# change this value based on which GPIO port the amplifier is connected to
# Flexible Pinout
ampGPIO = 26
# Classic Pinout
# ampGPIO = 23

# we do not cleanup the GPIO because we want the pin low = off after program exit
# the resulting warning can be ignored
GPIO.setwarnings(False)
GPIO.setmode(GPIO.BCM)
GPIO.setup(ampGPIO, GPIO.OUT)

def set_amplifier(status):
    if status:
        print("Setting amplifier: ON")
        GPIO.output(ampGPIO, GPIO.HIGH)
    else:
        print("Setting amplifier: OFF")
        GPIO.output(ampGPIO, GPIO.LOW)


def toggle_amplifier():
    print("toggling amplifier")
    amplifier.toggle()

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

