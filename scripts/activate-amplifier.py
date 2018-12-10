#!/usr/bin/python

# While running this script the PAM8403 gets a ON signal so amplifier has power. Else it is
# switched of. This helps me
# The application uses the GPIO Zero library (https://gpiozero.readthedocs.io/en/stable/)
# The PAM8403 PIN 12 is connected to one of the Pi's GPIO ports, then is defined as an Output device
# in GPIO Zero: https://gpiozero.readthedocs.io/en/stable/api_output.html#outputdevice

import sys
import time
from signal import pause
import gpiozero

# change this value based on which GPIO port the PAM8403 PIN 12 is connected to
PIN = 23

# create a relay object.
# Triggered by the output pin going low: active_high=False.
# Initially off: initial_value=False
amplifier = gpiozero.OutputDevice(PIN, active_high=True, initial_value=False)


def set_amplifier(status):
    if status:
        print("Setting amplifier: ON")
        amplifier.on()
    else:
        print("Setting amplifier: OFF")
        amplifier.off()


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

