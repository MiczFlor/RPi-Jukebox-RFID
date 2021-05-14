#!/usr/bin/env python3
# This alternative Reader.py script was meant to cover not only USB readers but more.
# It can be used to replace Reader.py if you have readers such as
# MFRC522, RDM6300 or PN532.
# Please use the github issue threads to share bugs and improvements
# or create pull requests.

import sys

import logging

from jukebox.rpc.client import RpcClient

from evdev import InputDevice, ecodes, list_devices

logger = logging.getLogger("jb.rfid")


def get_devices():
    devices = [InputDevice(fn) for fn in list_devices()]
    devices.append(NonUsbDevice('MFRC522'))
    devices.append(NonUsbDevice('RDM6300'))
    devices.append(NonUsbDevice('PN532'))
    return devices


class NonUsbDevice(object):
    name = None

    def __init__(self, name):
        self.name = name


class UsbReader(object):
    def __init__(self, device):
        self.keys = "X^1234567890XXXXqwertzuiopXXXXasdfghjklXXXXXyxcvbnmXXXXXXXXXXXXXXXXXXXXXXX"
        self.dev = device

    def readCard(self):
        from select import select
        stri = ''
        key = ''
        while key != 'KEY_ENTER':
            select([self.dev], [], [])
            for event in self.dev.read():
                if event.type == 1 and event.value == 1:
                    stri += self.keys[event.code]
                    key = ecodes.KEY[event.code]
        return stri[:-1]


class RFID_Reader(object):
    def __init__(self, device_name, param=None, zmq_context=None):

        if device_name == 'MFRC522':
            from .RfidReader_RC522 import Mfrc522Reader
            self.reader = Mfrc522Reader()
        elif device_name == 'RDM6300':
            from .RfidReader_RDM6300 import Rdm6300Reader
            self.reader = Rdm6300Reader(param)
        elif device_name == 'PN532':
            from .RfidReader_PN532 import Pn532Reader
            self.reader = Pn532Reader()
        elif device_name == 'Fake':
            from .FakeRfidReader import FakeReader
            self.reader = FakeReader()
        else:
            try:
                device = [device for device in get_devices() if device.name == device_name][0]
                self.reader = UsbReader(device)
            except IndexError:
                sys.exit('Could not find the device %s.\n Make sure it is connected' % device_name)

        self.PhonieboxRpc = RpcClient()
        self.PhonieboxRpc.connect(zmq_context=zmq_context)
        self._keep_running = True
        self.cardnotification = None
        self.valid_cardnotification = None
        self.invalid_cardnotification = None

    def set_cardid_db(self, cardid_db):
        if cardid_db is not None:
            self.cardid_db = cardid_db

    def get_card_assignment(self, cardid):
        return self.cardid_db.get(cardid)

    def get_last_card_id(self):
        return self.last_card_id

    def set_cardnotification(self, callback):
        if callable(callback):
            self.cardnotification = callback

    def set_valid_cardnotification(self, callback):
        if callable(callback):
            self.valid_cardnotification = callback

    def set_invalid_cardnotification(self, callback):
        if callable(callback):
            self.invalid_cardnotification = callback

    def terminate(self):
        self._keep_running = False

    def run(self):

        self._keep_running = True

        while self._keep_running:               # since readCard is a blocking call, this will not work
            cardid = self.reader.readCard()
            self.last_card_id = cardid

            if self.cardnotification is not None:
                self.cardnotification(cardid)

            card_assignment = self.get_card_assignment(cardid)

            if card_assignment is not None:

                # probably deal with 2nd swipe here

                if self.valid_cardnotification is not None:
                    self.valid_cardnotification()
                resp = self.PhonieboxRpc.enqueue(card_assignment)
                logger.debug(resp)
            else:
                if self.invalid_cardnotification is not None:
                    self.invalid_cardnotification()
        return 1
