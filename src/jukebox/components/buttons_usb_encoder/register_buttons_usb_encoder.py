#!/usr/bin/env python3
import sys

from io_buttons_usb_encoder import all_devices, write_current_device

try:
    devices = all_devices()
    i = 0
    print("")
    print("Choose the Buttons USB Encoder device from the list")
    for dev in devices:
        print(i, dev.name)
        i += 1

    dev_id = int(input('Device Number: '))

    write_current_device(devices[dev_id].name)
except KeyboardInterrupt:
    sys.exit("Aborted to register Buttons USB Encoder.")
