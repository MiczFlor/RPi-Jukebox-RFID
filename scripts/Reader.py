# Forked from Francisco Sahli's https://github.com/fsahli/music-cards/blob/master/Reader.py
import os.path
import sys
import serial
import string
import RPi.GPIO as GPIO

from evdev import InputDevice, categorize, ecodes, list_devices
import MFRC522


def get_devices():
    devices = [InputDevice(fn) for fn in list_devices()]
    devices.append(NonUsbDevice('MFRC522'))
    devices.append(NonUsbDevice('RDM6300'))
    return devices


class NonUsbDevice(object):
    name = None

    def __init__(self, name):
        self.name = name


class UsbReader(object):
    def __init__(self, device):
        self.keys = "X^1234567890XXXXqwertzuiopXXXXasdfghjklXXXXXyxcvbnmXXXXXXXXXXXXXXXXXXXXXXX"
        self.dev = device

    def read_card(self):
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


class Mfrc522Reader(object):
    def __init__(self):
        self.device = MFRC522.MFRC522()

    def read_card(self):
        # Scan for cards
        status, tag_type = self.device.MFRC522_Request(self.device.PICC_REQIDL)

        # If a card is found
        if status == self.device.MI_OK:
            print "Card detected"

        # Get the UID of the card
        (status, uid) = self.device.MFRC522_Anticoll()

        # If we have the UID, continue
        if status == self.device.MI_OK:
            return ''.join((str(x) for x in uid))
        else:
            print "No Device ID found."
            return None

    @staticmethod
    def cleanup():
        GPIO.cleanup()


class Rdm6300Reader:
    def __init__(self):
        device = '/dev/ttyS0'
        baudrate = 9600
        ser_timeout = 0.1
        self.last_card_id = ''
        try:
            self.rfid_serial = serial.Serial(device, baudrate, timeout=ser_timeout)
        except serial.SerialException as e:
            print(e)
            exit(1)

    def read_card(self):
        byte_card_id = b''

        try:
            while True:
                try:
                    read_byte = self.rfid_serial.read()

                    if read_byte == b'\x02':    # start byte
                        while read_byte != b'\x03':     # end bye
                            read_byte = self.rfid_serial.read()
                            byte_card_id += read_byte

                        card_id = byte_card_id.decode('utf-8')
                        byte_card_id = ''
                        card_id = ''.join(x for x in card_id if x in string.printable)

                        # Only return UUIDs with correct length
                        if len(card_id) == 12 and card_id != self.last_card_id:
                            self.last_card_id = card_id
                            self.rfid_serial.reset_input_buffer()
                            return self.last_card_id

                        else:   # wrong UUID length or already send that UUID last time
                            self.rfid_serial.reset_input_buffer()

                except ValueError as ve:
                    print(ve)

        except serial.SerialException as se:
            print(se)

    def cleanup(self):
        self.rfid_serial.close()


class Reader(object):
    def __init__(self):
        path = os.path.dirname(os.path.realpath(__file__))
        if not os.path.isfile(path + '/deviceName.txt'):
            sys.exit('Please run config.py first')
        else:
            with open(path + '/deviceName.txt', 'r') as f:
                device_name = f.read()

            if device_name == 'MFRC522':
                self.reader = Mfrc522Reader()
            elif device_name == 'RDM6300':
                self.reader = Rdm6300Reader()
            else:
                try:
                    device = [device for device in get_devices() if device.name == device_name][0]
                    self.reader = UsbReader(device)
                except IndexError:
                    sys.exit('Could not find the device %s.\n Make sure it is connected' % device_name)
