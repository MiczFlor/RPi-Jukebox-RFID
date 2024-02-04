# Copyright (c) See file LICENSE in project root folder
"""
Provides all supported output devices for the GPIOZ plugin.

For each device all constructor parameters can be set via the configuration file. Only exceptions
are the :attr:`name` and :attr:`pin_factory` which are set by internal mechanisms.

The devices a are a relatively thin wrapper around the GPIOZero devices with the same name.
We add a name property to be used for error log message and similar and a :func:`flash` function
to all devices. This function provides a unified API to all devices. This means it can be called for every device
with parameters for this device and optional parameters from another device. Unused/unsupported parameters
are silently ignored. This is done to reduce the amount of coding required for connectivity functions.

For examples how to use the devices from the configuration files, see
[GPIO: Output Devices](../../builders/gpio.md#output-devices).
"""

from typing import Optional, List

import gpiozero
from gpiozero.threads import GPIOThread
from gpiozero.tones import Tone
from itertools import repeat


class NameMixin(object):
    def __init__(self, *args, name, **kwargs):
        super().__init__(*args, **kwargs)
        self._name = 'Unnamed' if name is None else name

    @property
    def name(self):
        return self._name


class LED(NameMixin, gpiozero.LED):
    """
    A binary LED

    :param pin: The GPIO pin which the LED is connected

    :param active_high: If :data:`true` the output pin will have a high logic level when the device is turned on.

    :param pin_factory: The GPIOZero pin factory. This parameter cannot be set through the configuration file

    :type name: str
    :param name: The name of the button for use in error messages. This parameter cannot be set explicitly
        through the configuration file
    """
    def __init__(self, pin=None, active_high=True, initial_value=False,
                 pin_factory=None, name=None):
        super().__init__(pin=pin, active_high=active_high, initial_value=initial_value, pin_factory=pin_factory, name=name)

    def flash(self, on_time=1, off_time=1, n=1, *, background=True, **ignored_kwargs):
        """Exactly like :func:`blink` but restores the original state after flashing the device

        :param float on_time:
            Number of seconds on. Defaults to 1 second.

        :param float off_time:
            Number of seconds off. Defaults to 1 second.

        :param n:
            Number of times to blink; :data:`None` means forever.

        :param bool background:
            If :data:`True` (the default), start a background thread to
            continue blinking and return immediately. If :data:`False`, only
            return when the blink is finished

        :param ignored_kwargs: Ignore all other keywords so this function can be called with identical
            parameters also for all other output devices
        """
        self._stop_blink()
        self._blink_thread = GPIOThread(
            self._flash_device, (on_time, off_time, n)
        )
        self._blink_thread.start()
        if not background:
            self._blink_thread.join()
            self._blink_thread = None

    def _flash_device(self, *args, **kwargs):
        current_value = self.value
        self._blink_device(*args, **kwargs)
        self._write(current_value)


class Buzzer(NameMixin, gpiozero.Buzzer):
    def __init__(self, pin=None, active_high=True, initial_value=False,
                 pin_factory=None, name=None):
        super().__init__(pin=pin, active_high=active_high, initial_value=initial_value, pin_factory=pin_factory, name=name)

    def flash(self, on_time=1, off_time=1, n=1, *, background=True, **ignored_kwargs):
        """Flash the device and restore the previous value afterwards"""
        self.blink(on_time, off_time, n, background=background)


class PWMLED(NameMixin, gpiozero.PWMLED):
    def __init__(
            self, pin=None, active_high=True, initial_value=0, frequency=100,
            pin_factory=None, name=None):
        super(PWMLED, self).__init__(pin=pin, active_high=active_high, initial_value=initial_value, frequency=frequency,
                                     pin_factory=pin_factory, name=name)

    def flash(self, on_time=1, off_time=1, n=1, *, fade_in_time=0, fade_out_time=0, background=True, **ignored_kwargs):
        """Flash the LED and restore the previous value afterwards"""
        self._stop_blink()
        self._blink_thread = GPIOThread(
            self._flash_device,
            (on_time, off_time, fade_in_time, fade_out_time, n)
        )
        self._blink_thread.start()
        if not background:
            self._blink_thread.join()
            self._blink_thread = None

    def _flash_device(self, *args, **kwargs):
        current_value = self.value
        self._blink_device(*args, **kwargs)
        self._write(current_value)


class RGBLED(NameMixin, gpiozero.RGBLED):
    def __init__(self, red=None, green=None, blue=None, active_high=True,
                 initial_value=(0, 0, 0), pwm=True, pin_factory=None, name=None):
        super().__init__(red=red, green=green, blue=blue, active_high=active_high,
                         initial_value=initial_value, pwm=pwm, pin_factory=pin_factory, name=name)

    def flash(
            self, on_time=1, off_time=1, *, fade_in_time=0, fade_out_time=0,
            on_color=(1, 1, 1), off_color=(0, 0, 0), n=None, background=True, **igorned_kwargs):
        """Flash the LED with :attr:`on_color` and restore the previous value afterwards"""

        if isinstance(self._leds[0], LED):
            if fade_in_time:
                raise ValueError('fade_in_time must be 0 with non-PWM RGBLEDs')
            if fade_out_time:
                raise ValueError('fade_out_time must be 0 with non-PWM RGBLEDs')
        self._stop_blink()
        self._blink_thread = GPIOThread(
            self._flash_device,
            (
                on_time, off_time, fade_in_time, fade_out_time,
                on_color, off_color, n
            )
        )
        self._blink_thread.start()
        if not background:
            self._blink_thread.join()
            self._blink_thread = None

    def _flash_device(self, *args, **kwargs):
        current_value = self.value
        self._blink_device(*args, **kwargs)
        for led, v in zip(self._leds, current_value):
            led._write(v)


class TonalBuzzer(NameMixin, gpiozero.TonalBuzzer):
    def __init__(self, pin=None, initial_value=None, mid_tone=Tone("A5"),
                 octaves=2, pin_factory=None, name=None):
        super().__init__(pin=pin, initial_value=initial_value, mid_tone=mid_tone, octaves=octaves,
                         pin_factory=pin_factory, name=name)
        self._blink_thread = None
        self._controller = None

    def flash(self, on_time=1, off_time=1, n=1, *, tone=None, background=True, **ignored_kwargs):
        """Play the tone :data:`tone` for :attr:`n` times"""
        tone = tone if tone is not None else self.mid_tone
        self._stop_blink()
        self._blink_thread = GPIOThread(
            self._flash_device, (on_time, off_time, n, tone)
        )
        self._blink_thread.start()
        if not background:
            self._blink_thread.join()
            self._blink_thread = None

    def _stop_blink(self):
        if getattr(self, '_controller', None):
            self._controller._stop_blink(self)
        self._controller = None
        if getattr(self, '_blink_thread', None):
            self._blink_thread.stop()
        self._blink_thread = None

    def _flash_device(self, on_time, off_time, n, tone):
        iterable = repeat(0) if n is None else repeat(0, n)
        for _ in iterable:
            self.play(tone)
            if self._blink_thread.stopping.wait(on_time):
                break
            self.stop()
            if self._blink_thread.stopping.wait(off_time):
                break

    def melody(self, on_time=0.2, off_time=0.05, *, tone: Optional[List[Tone]] = None, background=True):
        """Play a melody from the list of tones in :attr:`tone`"""
        if tone is None:
            tone = ['A4', 'C5', 'D5']
        self._stop_blink()
        self._blink_thread = GPIOThread(
            self._melody_device, (on_time, off_time, tone)
        )
        self._blink_thread.start()
        if not background:
            self._blink_thread.join()
            self._blink_thread = None

    def _melody_device(self, on_time, off_time, tone):
        for idx in tone:
            self.play(idx)
            if self._blink_thread.stopping.wait(on_time):
                break
            self.stop()
            if self._blink_thread.stopping.wait(off_time):
                break
