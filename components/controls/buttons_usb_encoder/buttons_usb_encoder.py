#!/usr/bin/env python3

import sys

sys.path.append(".")  # This command should be before imports of components

import logging
from evdev import categorize, ecodes, KeyEvent
from io_buttons_usb_encoder import button_map, current_device
from components.gpio_control.function_calls import phoniebox_function_calls

sys.path.append(".")

logger = logging.getLogger(__name__)

try:
    button_map = button_map()
    function_calls = phoniebox_function_calls()
    for event in current_device().read_loop():
        if event.type == ecodes.EV_KEY:
            keyevent = categorize(event)
            if keyevent.keystate == KeyEvent.key_down:
                button_string = keyevent.keycode
                if type(button_string) is list:
                    button_string = '-'.join(sorted(button_string))
                try:
                    function_name = button_map[button_string]
                    function_args = button_map[button_string + "_args"]
                    try:
                        getattr(function_calls, function_name)(function_args)
                    except Exception:
                        logger.warning(
                            "Function " + function_name
                            + " not found in function_calls.py (mapped from button: " + button_string + ")")
                except KeyError:
                    logger.warning("Button " + button_string + " not mapped to any function.")
except Exception:
    logger.error("An error with Buttons USB Encoder occurred.")
