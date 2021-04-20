#!/usr/bin/env python3

import os.path
import sys
import json

from evdev import InputDevice, list_devices

path = os.path.dirname(os.path.realpath(__file__))
device_name_path = path + '/deviceName.txt'
button_map_path = path + '/buttonMap.json'


def all_devices():
    return [InputDevice(fn) for fn in list_devices()]


def current_device():
    if not os.path.isfile(device_name_path):
        sys.exit('Please run register_buttons_usb_encoder.py first')
    else:
        with open(device_name_path, 'r') as f:
            device_name = f.read()
        devices = all_devices()
        for device in devices:
            if device.name == device_name:
                _current_device = device
                break
        try:
            _current_device
        except:
            sys.exit('Could not find the device %s\n. Make sure it is connected' % device_name)
        return _current_device


def write_current_device(name):
    with open(device_name_path, 'w') as f:
        f.write(name)
        f.close()


def button_map():
    if not os.path.isfile(button_map_path):
        sys.exit('Please run map_buttons_usb_encoder.py first')
    else:
        with open(button_map_path, 'r') as json_file:
            button_map = json.load(json_file)
            if (len(button_map) == 0):
                sys.exit("No buttons mapped to a function")
            return button_map


def write_button_map(button_map):
    with open(button_map_path, 'w') as fp:
        json.dump(button_map, fp)
        fp.close()
