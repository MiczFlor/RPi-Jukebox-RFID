from typing import Callable

import gpiozero
from abc import ABC, abstractmethod
import logging
import jukebox.utils

logger = logging.getLogger('jb.gpioz')


class NameMixin(ABC):
    def __init__(self, *args, name, **kwargs):
        super().__init__(*args, **kwargs)
        self._name = 'Unnamed' if name is None else name

    @property
    def name(self):
        return self._name

    def _decode_rpc_action(self, action_name, action_config):
        if logger.isEnabledFor(logging.DEBUG):
            rpc_as_string = jukebox.utils.rpc_call_to_str(jukebox.utils.decode_rpc_command(action_config.get(action_name)),
                                                          with_args=True)
            logger.debug(f"Set RPC for '{self._name}.{action_name}': {rpc_as_string}")
        if action_config is None:
            logger.warning(f"Set RPC for '{self._name}.{action_name}': Action is None!")
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
    def set_rpc_actions(self, action_config):
        pass


class ButtonBase(ABC):
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
        return self._button.value

    @property
    def pin(self):
        return self._button.pin

    @property
    def pull_up(self):
        return self._button.pull_up

    def close(self):
        self._button.close()


class Button(NameMixin, ButtonBase):
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
        return self._button.when_pressed

    @on_press.setter
    def on_press(self, func):
        self._button.when_pressed = func
        if self._button.hold_repeat:
            self._button.when_held = func

    def set_rpc_actions(self, action_config):
        self.on_press = self._decode_rpc_action('on_press', action_config)


class LongPressButton(NameMixin, ButtonBase):
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
        print(f"Activate {self}")
        self._is_long_press = False

    def _on_long_activation(self):
        print(f"Long {self}")
        self._is_long_press = True
        if self._long_press_callback:
            self._long_press_callback()

    def _on_deactivation(self):
        print(f"Deactivate {self._is_long_press}")
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
    def __init__(self, a, b, *, bounce_time=None, pin_factory=None, name=None):
        super().__init__(name=name)
        self._rotary = gpiozero.RotaryEncoder(a, b, bounce_time=bounce_time, pin_factory=pin_factory,
                                              wrap=False, max_steps=16, threshold_steps=(0, 0))

    @property
    def pin_a(self):
        return self._rotary.a.pin

    @property
    def pin_b(self):
        return self._rotary.b.pin

    @property
    def on_rotate_clockwise(self):
        return self._rotary.when_rotated_clockwise

    @on_rotate_clockwise.setter
    def on_rotate_clockwise(self, func: Callable):
        self._rotary.when_rotated_clockwise = func

    @property
    def on_rotate_counter_clockwise(self):
        return self._rotary.when_rotated_clockwise

    @on_rotate_counter_clockwise.setter
    def on_rotate_counter_clockwise(self, func: Callable):
        self._rotary.when_rotated_counter_clockwise = func

    def set_rpc_actions(self, action_config):
        self.on_rotate_clockwise = self._decode_rpc_action('on_rotate_clockwise', action_config)
        self.on_rotate_counter_clockwise = self._decode_rpc_action('on_rotate_counter_clockwise', action_config)

    def close(self):
        self._rotary.close()
