# RPi-Jukebox-RFID Version 3
# Copyright (c) See file LICENSE in project root folder
"""
Provides all supported input devices for the GPIOZ plugin.

Input devices are based on GPIOZero devices. So for certain configuration parameters, you should
their documentation.

All callback handlers are replaced by GPIOZ callback handlers. These are usually configured
by using the :func:`set_rpc_actions` each input device exhibits.

For examples how to use the devices from the configuration files, see
[GPIO: Input Devices](../../builders/gpio.md#input-devices).
"""

import functools
import threading
from enum import Enum
from typing import Callable

import gpiozero
from abc import ABC, abstractmethod
import logging
import jukebox.utils

logger = logging.getLogger('jb.gpioz')


class NameMixin(ABC):
    """
    Provides name property and RPC decode function

    :meta private:
    """
    def __init__(self, *args, name, **kwargs):
        super().__init__(*args, **kwargs)
        self._name = 'Unnamed' if name is None else name
        # Warn if unbound function appear in _decode_rpc_action
        # e.g. for button where you expect all action functions to be assigned
        self._warn_on_no_func = True

    @property
    def name(self):
        return self._name

    def _decode_rpc_action(self, action_name, action_config):
        if action_config is None:
            logger.warning(f"Set RPC for '{self._name}.{action_name}': Zero actions defined in action configuration!")
        if action_config.get(action_name) is None:
            if self._warn_on_no_func is False:
                logger.debug(f"Set RPC for '{self._name}.{action_name}': Action is None.")
                return None
            else:
                logger.warning(f"Set RPC for '{self._name}.{action_name}': Action is None!")

        if logger.isEnabledFor(logging.DEBUG):
            rpc_as_string = jukebox.utils.rpc_call_to_str(jukebox.utils.decode_rpc_command(action_config.get(action_name)),
                                                          with_args=True)
            logger.debug(f"Set RPC for '{self._name}.{action_name}': {rpc_as_string}")
        try:
            func = jukebox.utils.bind_rpc_command(action_config.get(action_name), dereference=True, logger=logger)
        except Exception as e:
            # Could not find function: replace it with a function that logs an error when called, to give
            # log entries at the end for easier debugging of configuration by user
            msg = f"RPC command not set due error! Action '{action_name}' for '{self.name}': {e.__class__.__name__}: {e}"
            logger.error(msg)
            func = jukebox.utils.bind_rpc_command({'package': 'misc', 'plugin': 'empty_rpc_call', 'method': None,
                                                   'kwargs': None,
                                                   'args': msg}, dereference=True, logger=logger)

        return func

    @abstractmethod
    def set_rpc_actions(self, action_config) -> None:
        """
        Set all input device callbacks from :attr:`action_config`

        :param action_config: Dictionary with one
            [RPC Commands](../../builders/rpc-commands.md) definition entry for every device callback
        """
        pass


class EventProperty:
    """
    Event callback property

    :meta private:
    """
    def __init__(self, doc=''):
        self.__doc__ = doc

    def __set_name__(self, owner, name):
        self.private_name = '_' + name

    def __set__(self, instance, value):
        instance.__dict__[self.private_name] = value

    def __get__(self, instance, owner):
        return instance.__dict__.get(self.private_name)


class ButtonBase(ABC):
    """
    Common stuff for single button devices

    :meta private:
    """
    def __init__(
            self, pin=None, pull_up=True, active_state=None,
            bounce_time=None,
            pin_factory=None):
        super().__init__()
        self._button = gpiozero.Button(
            pin, pull_up=pull_up, active_state=active_state,
            bounce_time=bounce_time, pin_factory=pin_factory)

    @property
    def value(self):
        """
        Returns 1 if the button is currently pressed, and 0 if it is not.
        """
        return self._button.value

    @property
    def pin(self):
        """
        Returns the underlying pin class from GPIOZero.
        """
        return self._button.pin

    @property
    def pull_up(self):
        """
        If :data:`True`, the device uses an internal pull-up resistor to set the GPIO pin “high” by default.
        """
        return self._button.pull_up

    def close(self):
        """
        Close the device and release the pin
        """
        self._button.close()

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()


class Button(NameMixin, ButtonBase):
    """
    A basic Button that runs a single actions on button press

    :type pull_up: bool
    :param pull_up: If :data:`True`, the device uses an internal pull-up resistor to set the GPIO pin “high” by default.
        If :data:`False` the internal pull-down resistor is used. If :data:`None`, the pin will be floating and an external
        resistor must be used and the :attr:`active_state` must be set.

    :type active_state: bool or None
    :param active_state:
        If :data:`True`, when the hardware pin state is ``HIGH``, the software
        pin is ``HIGH``. If :data:`False`, the input polarity is reversed: when
        the hardware pin state is ``HIGH``, the software pin state is ``LOW``.
        Use this parameter to set the active state of the underlying pin when
        configuring it as not pulled (when *pull_up* is :data:`None`). When
        *pull_up* is :data:`True` or :data:`False`, the active state is
        automatically set to the proper value.

    :type bounce_time: float or None
    :param bounce_time:
        Specifies the length of time (in seconds) that the component will
        ignore changes in state after an initial change. This defaults to
        :data:`None` which indicates that no bounce compensation will be
        performed.

    :type hold_repeat: bool
    :param hold_repeat: If :data:`True` repeat the :attr:`on_press` every :attr:`hold_time` seconds. Else action
        is run only once independent of the length of time the button is pressed for.

    :type hold_time: float
    :param hold_time: Time in seconds to wait between invocations of :attr:`on_press`.

    :param pin_factory: The GPIOZero pin factory. This parameter cannot be set through the configuration file

    :type name: str
    :param name: The name of the button for use in error messages. This parameter cannot be set explicitly
        through the configuration file

    .. copied from GPIOZero's documentation: active_state, bounce_time
    .. Copyright Ben Nuttall / SPDX-License-Identifier: BSD-3-Clause
    """
    def __init__(
            self, pin=None, *, pull_up=True, active_state=None,
            bounce_time=None,
            hold_time=1, hold_repeat=False,
            pin_factory=None,
            name=None):
        super().__init__(
            pin=pin, pull_up=pull_up, active_state=active_state,
            bounce_time=bounce_time, pin_factory=pin_factory, name=name)
        self._button.hold_time = hold_time
        self._button.hold_repeat = hold_repeat

    @property
    def on_press(self):
        """
        The function to run when the device has been pressed
        """
        return self._button.when_pressed

    @on_press.setter
    def on_press(self, func):
        self._button.when_pressed = func
        if self._button.hold_repeat:
            self._button.when_held = func
        elif self._button.when_held:
            self._button.when_held = None

    @property
    def hold_time(self):
        return self._button.hold_time

    @property
    def hold_repeat(self):
        return self._button.hold_repeat

    def set_rpc_actions(self, action_config):
        self.on_press = self._decode_rpc_action('on_press', action_config)


class LongPressButton(NameMixin, ButtonBase):
    """
    A Button that runs a single actions only when the button is pressed long enough

    :param pull_up: See #Button

    :param active_state: See #Button

    :param bounce_time: See #Button

    :param hold_repeat: If :data:`True` repeat the :attr:`on_press` every :attr:`hold_time` seconds. Else only action
        is run only once independent of the length of time the button is pressed for.

    :param hold_time: The minimum time, the button must be pressed be running :attr:`on_press` for the first time.
        Also the time in seconds to wait between invocations of :attr:`on_press`.

    """
    def __init__(
            self, pin=None, *, pull_up=True, active_state=None,
            bounce_time=None,
            hold_time=1, hold_repeat=False,
            pin_factory=None,
            name=None):
        super().__init__(
            pin=pin, pull_up=pull_up, active_state=active_state,
            bounce_time=bounce_time, pin_factory=pin_factory, name=name)
        self._button.hold_time = hold_time
        self._button.hold_repeat = hold_repeat

    @property
    def on_press(self):
        return self._button.when_held

    @on_press.setter
    def on_press(self, func):
        """
        The function to run when the device has been pressed for longer than :attr:`hold_time`
        """
        self._button.when_held = func

    @property
    def hold_time(self):
        return self._button.hold_time

    @property
    def hold_repeat(self):
        return self._button.hold_repeat

    def set_rpc_actions(self, action_config):
        self.on_press = self._decode_rpc_action('on_press', action_config)


class ShortLongPressButton(NameMixin, ButtonBase):
    """
    A single button that runs two different actions depending if the button is pressed for a short or long time.

    The shortest possible time is used to ensure a unique identification to an action can be made. For example a short press
    can only be identified, when a button is released before :attr:`hold_time`, i.e. not directly on button press.
    But a long press can be identified as soon as :attr:`hold_time` is reached and there is no need to wait for the release
    event. Furthermore, if there is a long hold, only the long hold action is executed - the short press action is not run
    in this case!

    :param pull_up: See #Button

    :param active_state: See #Button

    :param bounce_time: See #Button

    :param hold_time: The time in seconds to differentiate if it is a short or long press. If the button is released before
        this time, it is a short press. As soon as the button is held for :attr:`hold_time` it is a long press and the
        short press action is ignored

    :param hold_repeat: If :data:`True` repeat the long press action every :attr:`hold_time` seconds after first long press
        action

    :param pin_factory: See #Button

    :param name: See #Button
    """
    def __init__(
            self, pin=None, *, pull_up=True, active_state=None, bounce_time=None,
            hold_time=1, hold_repeat=False, pin_factory=None, name=None):
        super().__init__(
            pin=pin, pull_up=pull_up, active_state=active_state,
            bounce_time=bounce_time, pin_factory=pin_factory, name=name)
        self._button.hold_time = hold_time
        self._button.hold_repeat = hold_repeat

        self._is_long_press = False
        self._button.when_pressed = self._on_activation
        self._button.when_held = self._on_long_activation
        self._button.when_released = self._on_deactivation

        self._short_press_callback = None
        self._long_press_callback = None

    def _on_activation(self):
        self._is_long_press = False

    def _on_long_activation(self):
        self._is_long_press = True
        if self._long_press_callback:
            self._long_press_callback()

    def _on_deactivation(self):
        if not self._is_long_press and self._short_press_callback:
            self._short_press_callback()

    @property
    def on_short_press(self):
        return self._short_press_callback

    @on_short_press.setter
    def on_short_press(self, func: Callable):
        self._short_press_callback = func

    @property
    def on_long_press(self):
        return self._short_press_callback

    @on_long_press.setter
    def on_long_press(self, func: Callable):
        self._long_press_callback = func

    @property
    def hold_time(self):
        return self._button.hold_time

    @property
    def hold_repeat(self):
        return self._button.hold_repeat

    def set_rpc_actions(self, action_config):
        self.on_short_press = self._decode_rpc_action('on_short_press', action_config)
        self.on_long_press = self._decode_rpc_action('on_long_press', action_config)


class RotaryEncoder(NameMixin):
    """
    A rotary encoder to run one of two actions depending on the rotation direction.

    :param bounce_time: See #Button

    :param pin_factory: See #Button

    :param name: See #Button
    """
    def __init__(self, a, b, *, bounce_time=None, pin_factory=None, name=None):
        super().__init__(name=name)
        self._rotary = gpiozero.RotaryEncoder(a, b, bounce_time=bounce_time, pin_factory=pin_factory,
                                              wrap=False, max_steps=16, threshold_steps=(0, 0))

    @property
    def pin_a(self):
        """
        Returns the underlying pin A
        """
        return self._rotary.a.pin

    @property
    def pin_b(self):
        """
        Returns the underlying pin B
        """
        return self._rotary.b.pin

    @property
    def on_rotate_clockwise(self):
        """
        The function to run when the encoder is rotated clockwise
        """
        return self._rotary.when_rotated_clockwise

    @on_rotate_clockwise.setter
    def on_rotate_clockwise(self, func: Callable):
        self._rotary.when_rotated_clockwise = func

    @property
    def on_rotate_counter_clockwise(self):
        """
        The function to run when the encoder is rotated counter clockwise
        """
        return self._rotary.when_rotated_clockwise

    @on_rotate_counter_clockwise.setter
    def on_rotate_counter_clockwise(self, func: Callable):
        self._rotary.when_rotated_counter_clockwise = func

    def set_rpc_actions(self, action_config):
        self.on_rotate_clockwise = self._decode_rpc_action('on_rotate_clockwise', action_config)
        self.on_rotate_counter_clockwise = self._decode_rpc_action('on_rotate_counter_clockwise', action_config)

    def close(self):
        """
        Close the device and release the pin
        """
        self._rotary.close()


class TwinButton(NameMixin):
    """
    A two-button device which can run up to six different actions, a.k.a the six function beast.

    Per user press "input" of the TwinButton, only a single callback is executed (but this callback
    may be executed several times).
    The shortest possible time is used to ensure a unique identification to an action can be made. For example a short press
    can only be identified, when a button is released before :attr:`hold_time`, i.e. not directly on button press.
    But a long press can be identified as soon as :attr:`hold_time` is reached and there is no need to wait for the release
    event. Furthermore, if there is a long hold, only the long hold action is executed - the short press action is not run
    in this case!

    It is not necessary to configure all actions.

    :param pull_up: See #Button

    :param active_state: See #Button

    :param bounce_time: See #Button

    :param hold_time: The time in seconds to differentiate if it is a short or long press. If the button is released before
        this time, it is a short press. As soon as the button is held for :attr:`hold_time` it is a long press and the
        short press action is ignored.

    :param hold_repeat: If :data:`True` repeat the long press action every :attr:`hold_time` seconds after first long press
        action. A long dual press is never repeated independent of this setting

    :param pin_factory: See #Button

    :param name: See #Button
    """

    class StateVar(Enum):
        """
        State encoding of the Mealy FSM

        :meta private:
        """
        IDLE = 0
        HOLD_A = 1
        CONT_A = 2
        HOLD_B = 3
        CONT_B = 4
        CONT_AB_WAIT_A = 5
        CONT_AB_WAIT_B = 6
        WAIT4RELEASE = 7

    def __init__(self, a, b, *, pull_up=True, active_state=None, bounce_time=None,
                 hold_time=1, hold_repeat=1, pin_factory=None, name=None):
        super().__init__(name=name)
        self._pin_a = gpiozero.Button(a, pull_up=pull_up, active_state=active_state,
                                      bounce_time=bounce_time, pin_factory=pin_factory)
        self._pin_b = gpiozero.Button(b, pull_up=pull_up, active_state=active_state,
                                      bounce_time=bounce_time, pin_factory=pin_factory)
        self._pin_a.hold_time = hold_time
        self._pin_b.hold_time = hold_time
        self._pin_a.hold_repeat = hold_repeat
        self._pin_b.hold_repeat = hold_repeat
        self._state = TwinButton.StateVar.IDLE
        self._pin_a.when_activated = functools.partial(self._change_state, edge_a=1, edge_b=0, hold_a=0, hold_b=0)
        self._pin_b.when_activated = functools.partial(self._change_state, edge_a=0, edge_b=1, hold_a=0, hold_b=0)
        self._pin_a.when_deactivated = functools.partial(self._change_state, edge_a=0, edge_b=0, hold_a=0, hold_b=0)
        self._pin_b.when_deactivated = functools.partial(self._change_state, edge_a=0, edge_b=0, hold_a=0, hold_b=0)
        self._pin_a.when_held = functools.partial(self._change_state, edge_a=0, edge_b=0, hold_a=1, hold_b=0)
        self._pin_b.when_held = functools.partial(self._change_state, edge_a=0, edge_b=0, hold_a=0, hold_b=1)
        self._on_short_press_a = None
        self._on_short_press_b = None
        self._on_short_press_ab = None
        self.on_long_press_a = None
        self.on_long_press_b = None
        self.on_long_press_ab = None
        self._warn_on_no_func = False
        self._state_lock = threading.Lock()

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()

    def close(self):
        """
        Close the device and release the pins
        """
        self._pin_a.close()
        self._pin_b.close()

    def _change_state(self, edge_a=0, edge_b=0, hold_a=0, hold_b=0):  # noqa: C901
        # IMPORTANT: Due to the functions assignments to  the button actions,
        # the values for edge_X are always zero, when a hold_X is 1!
        # For the state change logic this means, when hold_X is 1 do not rely on edge_X
        # which is simply implemented, by prioritization of held_X over any edge_X in if-else logic
        with self._state_lock:
            # print(f"{TwinButton.StateVar(self._state)} : {edge_a}, {edge_b}, {hold_a}, {hold_b}")
            if self._state == TwinButton.StateVar.IDLE:
                if edge_a == 1:
                    self._state = TwinButton.StateVar.HOLD_A
                elif edge_b == 1:
                    self._state = TwinButton.StateVar.HOLD_B

            elif self._state == TwinButton.StateVar.HOLD_A:
                if hold_a == 1:
                    # Button A hold time has been reached, without B being pressed ...
                    # ... which acts as a timeout for dual press action ...
                    if self.on_long_press_a:
                        # ... if there is a held callback, triggers when_held and goes to checking for held_repeat
                        self._state = TwinButton.StateVar.CONT_A
                        self._fire_hold_a()
                    else:
                        # ... if there is no held callback, trigger the short_press and wait for release
                        self._fire_press_a()
                        self._state = TwinButton.StateVar.WAIT4RELEASE
                elif edge_b == 1:
                    # Dual press detected ...
                    if self.on_long_press_ab:
                        # ... if there is a held callback registered, we need to wait
                        # to see if the button is held long or released to differentiate between long/short press
                        self._state = TwinButton.StateVar.CONT_AB_WAIT_B
                    else:
                        # ... if there is not held callback, we can
                        # directly run the short press callback on second button activation
                        self._state = TwinButton.StateVar.WAIT4RELEASE
                        self._fire_press_ab()
                elif edge_a == 0:
                    # Button A is released before hold time is reached: this is a short press
                    self._state = TwinButton.StateVar.IDLE
                    self._fire_press_a()
            elif self._state == TwinButton.StateVar.CONT_A:
                # We are only here, if it is a single button press that has already timed through when_held once
                # Case A: hold_a stays one (only for held_repeat = true) to which re-triggers
                # Case B: all other button changes abort the hold pattern and go to wait for release
                if hold_a == 1:
                    self._fire_hold_a()
                elif self._pin_a.value == 0 and self._pin_b.value == 0:
                    # This if is required because edge_X do not reflect the active state of the button
                    # but indicate which edge has changed!
                    # Since we get here by having only BTN A pressed, and that is released, there will be
                    # no further event (like release B) to bring the state machine back to IDLE
                    self._state = TwinButton.StateVar.IDLE
                else:
                    # We could also get here by pressing A for a long time (triggering A held callback),
                    # then press B in addition
                    # this is certainly not an AB press, and also breaks the pattern of single button long press
                    # --> Abort
                    self._state = TwinButton.StateVar.WAIT4RELEASE

            elif self._state == TwinButton.StateVar.HOLD_B:
                if hold_b == 1:
                    if self.on_long_press_b:
                        self._state = TwinButton.StateVar.CONT_B
                        self._fire_hold_b()
                    else:
                        self._fire_press_b()
                        self._state = TwinButton.StateVar.WAIT4RELEASE

                elif edge_a == 1:
                    if self.on_long_press_ab:
                        self._state = TwinButton.StateVar.CONT_AB_WAIT_A
                    else:
                        self._state = TwinButton.StateVar.WAIT4RELEASE
                        self._fire_press_ab()
                elif edge_b == 0:
                    self._state = TwinButton.StateVar.IDLE
                    self._fire_press_b()
            elif self._state == TwinButton.StateVar.CONT_B:
                if hold_b == 1:
                    self._fire_hold_b()
                elif self._pin_a.value == 0 and self._pin_b.value == 0:
                    self._state = TwinButton.StateVar.IDLE
                else:
                    self._state = TwinButton.StateVar.WAIT4RELEASE

            elif self._state == TwinButton.StateVar.CONT_AB_WAIT_A:
                # Btn A and B are pressed together (B first, A a little later)
                # and we have a potential for a hold press or a release before hold press is reached
                if hold_a == 1:
                    # Wait for the later pressed button (A) to trigger hold callback
                    # to ensure proper hold time length
                    self._state = TwinButton.StateVar.WAIT4RELEASE
                    self._fire_hold_ab()
                elif hold_b == 1:
                    # Hold B is to time out before hold A: stay here and wait for hold or release
                    self._state = TwinButton.StateVar.CONT_AB_WAIT_A
                elif edge_b == 0 or edge_a == 0:
                    # In case no hold has been reached, but any button is released, treat as
                    # short press and prevent any re-triggering
                    self._state = TwinButton.StateVar.WAIT4RELEASE
                    self._fire_press_ab()

            elif self._state == TwinButton.StateVar.CONT_AB_WAIT_B:
                if hold_b == 1:
                    self._state = TwinButton.StateVar.WAIT4RELEASE
                    self._fire_hold_ab()
                elif hold_a == 1:
                    self._state = TwinButton.StateVar.CONT_AB_WAIT_B
                elif edge_b == 0 or edge_a == 0:
                    self._state = TwinButton.StateVar.WAIT4RELEASE
                    self._fire_press_ab()

            elif self._state == TwinButton.StateVar.WAIT4RELEASE:
                # Ensure that both buttons are released before going back to idle
                # to prevent transient states
                if self._pin_a.value == 0 and self._pin_b.value == 0:
                    self._state = TwinButton.StateVar.IDLE
            # print(f"New state: {self._state}")

    def _fire_press_a(self):
        if self._on_short_press_a:
            self._on_short_press_a()

    def _fire_press_b(self):
        if self._on_short_press_b:
            self._on_short_press_b()

    def _fire_press_ab(self):
        if self._on_short_press_ab:
            self._on_short_press_ab()

    def _fire_hold_ab(self):
        if self.on_long_press_ab:
            self.on_long_press_ab()

    def _fire_hold_a(self):
        if self.on_long_press_a:
            self.on_long_press_a()

    def _fire_hold_b(self):
        if self.on_long_press_b:
            self.on_long_press_b()

    on_short_press_a = EventProperty(
        """
        The function to run when button A has been pressed for any period shorter than :attr:`held_time`
        """)

    on_short_press_b = EventProperty(
        """
        The function to run when button B has been pressed for any period shorter than :attr:`held_time`
        """)

    on_short_press_ab = EventProperty(
        """
        The function to run when button A and B have been pressed simultaneously any period
        for shorter than :attr:`held_time`
        """)

    on_long_press_a = EventProperty(
        """
        The function to run when button A has been pressed for longer than :attr:`held_time`
        """)

    on_long_press_b = EventProperty(
        """
        The function to run when button B has been pressed for longer than :attr:`held_time`
        """)

    on_long_press_ab = EventProperty(
        """
        The function to run when button A and B have been pressed simultaneously for longer than :attr:`held_time`
        """)

    @property
    def value(self):
        """2 bit integer indicating if and which button is currently pressed. Button A is the LSB."""
        return (self._pin_b.value << 1) | self._pin_a.value

    @property
    def is_active(self):
        """:data:`True` if one or both buttons are currently pressed"""
        return self._pin_b.is_active | self._pin_a.is_active

    @property
    def hold_repeat(self):
        return self._pin_a.hold_repeat

    @property
    def hold_time(self):
        return self._pin_a.hold_time

    def set_rpc_actions(self, action_config):
        self.on_short_press_a = self._decode_rpc_action('on_short_press_a', action_config)
        self.on_short_press_b = self._decode_rpc_action('on_short_press_b', action_config)
        self.on_short_press_ab = self._decode_rpc_action('on_short_press_ab', action_config)
        self.on_long_press_a = self._decode_rpc_action('on_long_press_a', action_config)
        self.on_long_press_b = self._decode_rpc_action('on_long_press_b', action_config)
        self.on_long_press_ab = self._decode_rpc_action('on_long_press_ab', action_config)
