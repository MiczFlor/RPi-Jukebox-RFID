#!/usr/bin/env python3
# There are a variety of RFID readers out there, USB and non-USB variants.
# This might create problems in recognizing the reader you are using.
# We haven't found the silver bullet yet. If you can contribute to this
# quest, please comment in the issue thread or create pull requests.
# ALTERNATIVE SCRIPTS:
# If you encounter problems with this script Reader.py
# consider and test one of the alternatives in the same scripts folder.
# Replace the Reader.py file with one of the following files:
# * Reader.py.experimental
#     This alternative Reader.py script was meant to cover not only USB readers but more.
#     It can be used to replace Reader.py if you have readers such as
#     MFRC522, RDM6300 or PN532.
# * Reader.py.kkmoonRFIDreader
#     KKMOON RFID Reader which appears twice in the devices list as HID 413d:2107
#     and this required to check "if" the device is a keyboard.

import os.path
import sys
import nfc
from nfc.clf import RemoteTarget


def get_devices() -> str:
    return 'usb:072f:2200'


class Reader:
    reader = None

    def __init__(self):
        self.reader = self
        self.keys = "X^1234567890XXXXqwertzuiopXXXXasdfghjklXXXXXyxcvbnmXXXXXXXXXXXXXXXXXXXXXXX"
        self.clf = nfc.ContactlessFrontend()

    def readCard(self) -> str:
        self.clf.open('usb:072f:2200')
        tag = self.clf.connect(rdwr={'on-connect': lambda tag: False})
        self.clf.close()
        return str(tag.identifier).replace(" ", "").strip()
