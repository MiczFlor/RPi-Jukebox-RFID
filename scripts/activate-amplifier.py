#!/usr/bin/python

import sys
import time
from signal import pause
import RPi.GPIO as GPIO

# script to activate and deactivate an amplifier using a GPIO pin

# change this value based on which GPIO port the amplifier is connected to
PIN = 26

GPIO.setwarnings(False)
GPIO.setmode(GPIO.BCM)
GPIO.setup(PIN, GPIO.OUT)


def set_amplifier(status):
    if status:
        print("Setting amplifier: ON")
        GPIO.output(PIN, GPIO.HIGH)
    else:
        print("Setting amplifier: OFF")
        GPIO.output(PIN, GPIO.LOW)


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
        print("\nExiting application\n")
        # exit the application
        sys.exit(0)

