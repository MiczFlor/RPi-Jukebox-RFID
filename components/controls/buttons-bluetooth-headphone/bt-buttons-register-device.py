#!/usr/bin/env python3
"""
Presents available input devices to user for selection of bluetooth device
"""

import evdev as ev
import os.path

# Filename for storing the device name, relative to this script's location
filename_device_selection = '../../../settings/bluetooth-input-device-name.txt'


def bt_register_device(filename) -> str:
    """Presents available input devices to user for selection of bluetooth device

    Selected device name is stored in 'filename'

    :param filename:  Filename for storing the device name, relative to this script's location
    :return str: Selected device name
    """
    sq = input("Ensure bluetooth devices is turned on and connected. Ready? [Y/n] ")
    if sq != "Y" and sq != "y" and sq != "":
        print("Exiting ...")
        return ''

    all_devices = [ev.InputDevice(path) for path in ev.list_devices()]
    if len(all_devices) == 0:
        print("#" * 60)
        print("# NO INPUT DEVICES FOUND!")
        print("#" * 60)
        print("Exiting ...")
        return ''

    for idx in range(len(all_devices)):
        print(f"{str(idx)}: {all_devices[idx].name}")
    devid = int(input("Device number: "))

    filename_abs = os.path.dirname(os.path.realpath(__file__)) + '/' + filename
    with open(filename_abs, 'w') as f:
        f.write(all_devices[devid].name)

    return all_devices[devid].name


if __name__ == '__main__':
    bt_register_device(filename_device_selection)
