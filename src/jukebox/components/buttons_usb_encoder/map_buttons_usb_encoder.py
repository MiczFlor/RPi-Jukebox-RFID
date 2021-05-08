#!/usr/bin/env python3

import sys

sys.path.append(".")

from evdev import categorize, ecodes, KeyEvent
from io_buttons_usb_encoder import current_device, write_button_map
import components.gpio_control.function_calls

try:
    functions = list(
        filter(lambda function_name: function_name.startswith("functionCall"),
               dir(components.gpio_control.function_calls)))
    button_map = {}

    print("")
    print("During the next step you can map your buttons to one of the following available functions:")
    print(list(map(lambda function_name: function_name.replace("functionCall", ""), functions)))
    print("")
    if input('Ready to continue? (y/n)') != 'y':
        sys.exit("Aborted mapping buttons to functions")

    for function_name in functions:
        function_name_short = function_name.replace("functionCall", "")
        print("")
        print("Press button to map " + function_name_short + " or press ctrl+c to skip this function")
        try:
            for event in current_device().read_loop():
                if event.type == ecodes.EV_KEY:
                    keyevent = categorize(event)
                    if keyevent.keystate == KeyEvent.key_down:
                        button_map[keyevent.keycode] = function_name
                        print("Button " + keyevent.keycode + " is now mapped to " + function_name_short)
                        break
        except KeyboardInterrupt:
            continue
    if len(button_map) == 0:
        print("Warning: No buttons mapped to a function!")
    else:
        write_button_map(button_map)
except KeyboardInterrupt:
    sys.exit("Aborted mapping buttons to functions")
