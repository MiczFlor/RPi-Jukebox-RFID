"""
Support for the RDM6300 serial RFID module

1.) Connect the RDM6300 module
------------------------------
Connect the RDM6300 module to the serial GPIO pins 14 and 15.

2.) Enable GPIO serial port
---------------------------
Edit the /boot/config.txt (sudo nano /boot/config.txt) and add the following line:
    enable_uart=1

3.) Install dependecies
-----------------------
Be aware not to install the "serial" module, install "pyserial" instead and the RPi.GPIO module:
    pip install pyserial RPi.GPIO

4.) Replace the default Reader.py
---------------------------------
Replace the Reader.py file with the Reader_RDM6300.py:
mv Reader.py Reader_default.py; mv Reader_RDM6300.py Reader.py
"""


import RPi.GPIO as GPIO
import serial
import string


class Reader:
    def __init__(self):
        GPIO.setmode(GPIO.BCM)
        self.rfid_serial = serial.Serial('/dev/ttyS0', 9600)

    def readCard(self):
        while True:
            card_id = ''
            read_byte = self.rfid_serial.read()
            if read_byte == b'\x02':
                while read_byte != b'\x03':
                    read_byte = self.rfid_serial.read()
                    card_id += read_byte.decode('utf-8')
                card_id = ''.join(x for x in card_id if x in string.printable)
                return card_id
