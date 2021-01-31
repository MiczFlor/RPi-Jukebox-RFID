#!/usr/bin/env python3

import sys

sys.path.append(".")

import logging
from evdev import categorize, ecodes, KeyEvent
import components.gpio_control.function_calls
from io_buttons_usb_encoder import button_map, current_device

logger = logging.getLogger(__name__)

try:
    button_map = button_map()
    for event in current_device().read_loop():
        if event.type == ecodes.EV_KEY:
            keyevent = categorize(event)
            if keyevent.keystate == KeyEvent.key_down:
                button_string = keyevent.keycode
                if type(button_string) is list:
                    button_string = '-'.join(sorted(button_string))
                try:
                    function_name = button_map[button_string]
                    try:
                        getattr(components.gpio_control.function_calls, function_name)()
                    except:
                        logger.warning(
                            "Function " + function_name + " not found in function_calls.py (mapped from button: " + button_string + ")")
                except KeyError:
                    logger.warning("Button " + button_string + " not mapped to any function.")
except:
    logger.error("An error with Buttons USB Encoder occurred.")
