# RPi-Jukebox-RFID Version 3
# Copyright (c) See file LICENSE in project root folder
"""
Changes to the GPIOZero devices for using with the Mock RFID Reader
"""

import gpiozero


def rewrite(self, value):
    self._write_orig(value)
    if self.on_change_callback:
        self.on_change_callback(value)


def patch_mock_outputs_with_callback():
    """Monkey Patch LED + Buzzer to get a callback when state changes

    This targets to represent the state in the TK GUI.
    Other output devices cannot be represented in the GUI and are silently ignored.

    > [!NOTE]
    > Only for developing purposes!"""
    gpiozero.LED._write_orig = gpiozero.LED._write
    gpiozero.LED._write = rewrite
    gpiozero.LED.on_change_callback = None

    gpiozero.Buzzer._write_orig = gpiozero.Buzzer._write
    gpiozero.Buzzer._write = rewrite
    gpiozero.Buzzer.on_change_callback = None

    gpiozero.PWMLED._write_orig = gpiozero.PWMLED._write
    gpiozero.PWMLED._write = rewrite
    gpiozero.PWMLED.on_change_callback = None
