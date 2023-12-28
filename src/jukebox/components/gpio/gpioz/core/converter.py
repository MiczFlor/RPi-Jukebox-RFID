# RPi-Jukebox-RFID Version 3
# Copyright (c) See file LICENSE in project root folder
"""
Provides converter functions/classes for various Jukebox parameters to
values that can be assigned to GPIO output devices
"""
from math import floor
from typing import Tuple


class ColorProperty:
    """
    Color descriptor ensuring valid weight ranges

    :meta private:
    """

    def __init__(self, doc=''):
        self.__doc__ = doc

    def __set_name__(self, owner, name):
        self.private_name = '_' + name

    def __set__(self, instance, value):
        if value > 1.0:
            value = 1.0
        if value < 0.0:
            value = 0.0
        instance.__dict__[self.private_name] = value

    def __get__(self, instance, owner):
        return instance.__dict__.get(self.private_name) or 1.0


class VolumeToRGB:
    """
    Converts linear volume level to an RGB color value running through the color spectrum

    :param max_input: Maximum input value of linear input data
    :param offset: Offset in degrees in the color circle. Color circle
        traverses blue (0), cyan(60), green (120), yellow(180), red (240), magenta (340)
    :param section: The section of the full color circle to use in degrees

    Map input :data:`0...100` to color range :data:`green...magenta` and get the color for level 50

        conv = VolumeToRGB(100, offset=120, section=180)
        (r, g, b) = conv(50)

    The three components of an RGB LEDs do not have the same luminosity.
    Weight factors are used to get a balanced color output
    """

    def __init__(self, max_input, offset=0, section=360):
        self._range = max_input
        self._section_length = max_input / (section / 120.0)
        self._offset = offset / 120
        # Initial values for the color weight properties
        self._weight_red = 1.0
        self._weight_green = 0.25
        self._weight_blue = 0.70

    weight_red = ColorProperty(
        """
        Red color weight

        The three components of an RGB LEDs do not have the same luminosity.
        Weight factors for each color component in the range :data:`0.0...1.0`
        can be adjusted to get a balanced color output
        """)

    weight_green = ColorProperty(
        """
        Green color weight

        The three components of an RGB LEDs do not have the same luminosity.
        Weight factors for each color component in the range :data:`0.0...1.0`
        can be adjusted to get a balanced color output
        """)

    weight_blue = ColorProperty(
        """
        Blue color weight

        The three components of an RGB LEDs do not have the same luminosity.
        Weight factors for each color component in the range :data:`0.0...1.0`
        can be adjusted to get a balanced color output
        """)

    def __call__(self, volume) -> Tuple[float, float, float]:
        """
        Perform conversion for single volume level

        :return: Tuple(red, green, blue)
        :meta public:
        """
        y = volume / self._section_length
        x = (y + self._offset) % 3.0
        idx = floor(x)
        v = x - idx
        b = 1.0 - v
        if idx == 1:
            return self.luminize(v, b, 0)
        elif idx == 2:
            return self.luminize(b, 0, v)
        else:
            return self.luminize(0, v, b)

    def luminize(self, r, g, b):
        """Apply the color weight factors to the input color values"""
        return r * self._weight_red, g * self._weight_green, b * self._weight_blue
