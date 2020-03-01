"""This module provides convenient tools for the communication with
Mifare cards via the PN532.

Some knowledge of a Mifare card's layout and general access procedure
is needed to use this class effectively. Special care needs to be
taken when modifying trailer blocks because you may shut yourself
out of your card! Google "MF1S703x" for a good introduction to
Mifare cards.

A typical scenario would be:

card = Mifare()
card.SAMconfigure()
card.set_max_retries(MIFARE_SAFE_RETRIES)
uid = card.scan_field()
if uid:
    address = card.mifare_address(0,1)
    card.mifare_auth_a(address,MIFARE_FACTORY_KEY)
    data = card.mifare_read(address)
    card.in_deselect() # In case you want to authorize a different sector.
    
"""

import py532lib.i2c as i2c
from py532lib.frame import Pn532Frame as Pn532Frame
from py532lib.constants import *
import logging
import math

MIFARE_COMMAND_AUTH_A = 0x60
MIFARE_COMMAND_AUTH_B = 0x61
MIFARE_COMMAND_READ = 0x30
MIFARE_COMMAND_WRITE_16 = 0xA0
MIFARE_COMMAND_WRITE_4 = 0xA2
MIFARE_FACTORY_KEY = b"\xFF\xFF\xFF\xFF\xFF\xFF"
MIFARE_WAIT_FOR_ENTRY = 0xFF # MxRtyPassiveActivation value: wait until card enters field.
MIFARE_SAFE_RETRIES = 5 # This number of retries seems to detect most cards properlies.

class Mifare(i2c.Pn532_i2c):

    """This class allows for the communication with Mifare cards via
    the PN532.

    Compared to its superclass, this class provides a bit more
    sophisticated tools such as reading the contents of a Mifare
    card or writing to them, access restrictions, and key management.
    """

    def __init__(self):
        """Set up and configure PN532."""
        i2c.Pn532_i2c.__init__(self)
        self._uid = False

    def set_max_retries(self,mx_rty_passive_activation):
        """Configure the PN532 for the number of retries attempted
        during the InListPassiveTarget operation (set to
        MIFARE_SAFE_RETRIES for a safe one-time check, set to
        MIFARE_WAIT_FOR_ENTRY so it waits until entry of a card).
        """
        # We set MxRtyPassiveActivation to 5 because it turns out that one
        # try sometimes does not detect the card properly.
        frame = Pn532Frame(frame_type=PN532_FRAME_TYPE_DATA,
                           data=bytearray([PN532_COMMAND_RFCONFIGURATION,
                                           PN532_RFCONFIGURATION_CFGITEM_MAXRETRIES,
                                           0xFF,0x01,mx_rty_passive_activation]))
        self.send_command_check_ack(frame)
        self.read_response()

    def scan_field(self):
        """Scans the PN532's field for a Mifare card using the
        InListPassiveTarget operation.

        Returns the card's UID (a bytearray) if a card was in the field
        or False if no card was in the field. Only one card is
        detected at a time (the PN532 can handle two but this is not
        implemented here). False is never returned if the number of
        retries (see set_max_retries()) is set to MIFARE_WAIT_FOR_ENTRY.
        """
        frame = Pn532Frame(frame_type=PN532_FRAME_TYPE_DATA,
                           data=bytearray([PN532_COMMAND_INLISTPASSIVETARGET, 0x01, 0x00]))
        self.send_command_check_ack(frame)
        response = self.read_response().get_data()
        target_count = response[1]
        if not target_count:
            self._uid = False
            return False
        uid_length = response[6]
        self._uid = response[7:7 + uid_length]
        return self._uid

    def in_data_exchange(self,data):
        """Sends a (Mifare) command to the currently active target.

        The "data" parameter contains the command data as a bytearray.
        Returns the data returned by the command (as a bytearray).
        Raises an IOError if the command failed.
        """
        logging.debug("InDataExchange sending: " + " ".join("{0:02X}".format(k) for k in data))
        logging.debug(data)
        frame = Pn532Frame(frame_type=PN532_FRAME_TYPE_DATA, data=bytearray([PN532_COMMAND_INDATAEXCHANGE, 0x01]) + data)
        self.send_command_check_ack(frame)
        response_frame = self.read_response()
        if response_frame.get_frame_type() == PN532_FRAME_TYPE_ERROR:
            raise IOError("InDataExchange failed (error frame returned)")
        response = response_frame.get_data()
        logging.debug("InDataExchange response: " + " ".join("{0:02X}".format(k) for k in response))
        if response[1] != 0x00:
            # Only the status byte was returned. There was an error.
            if response[1] == 0x14:
                raise IOError("Mifare authentication failed")
            else:
                raise IOError("InDataExchange returned error status: {0:#x}".format(response[1]))
        return response[2:]

    def in_deselect(self):
        """Deselects the current target."""
        logging.debug("InDeselect sending...")
        frame = Pn532Frame(frame_type=PN532_FRAME_TYPE_DATA, data=bytearray([PN532_COMMAND_INDESELECT, 0x01]))
        self.send_command_check_ack(frame)
        response_frame = self.read_response()
        if response_frame.get_frame_type() == PN532_FRAME_TYPE_ERROR:
            raise IOError("InDeselect failed (error frame returned)")
        response = response_frame.get_data()
        logging.debug("InDeselect response: " + " ".join("{0:02X}".format(k) for k in response))
        if response[1] != 0x00:
            # Only the status byte was returned. There was an error.
            raise IOError("InDataExchange returned error status: {0:#x}".format(response[1]))

    def mifare_address(self,sector,block):
        """Returns a one byte address for the given Mifare sector and block."""
        if sector < 32:
            if sector < 0 or block > 3 or block < 0:
                raise IndexError("Invalid sector / block: {0} / {1}".format(sector,block))
            return sector * 4 + block
        else:
            if sector > 39 or block < 0 or block > 15:
                raise IndexError("Invalid sector / block: {0} / {1}".format(sector,block))
            return 32 * 4 + (sector - 32) * 16 + block

    def mifare_sector_block(self,address):
        """Returns a tuple (sector,block) for the given address."""
        if address > 255 or address < 0:
            raise IndexError("Invalid Mifare block address: {0}".format(address))
        if address < 128:
            return (address >> 2,address & 3)
        else:
            return (32 + ((address - 128) >> 4),(address - 128) & 15)

    def mifare_auth_a(self,address,key_a):
        """Authenticate the Mifare card with key A.

        The "key_a" parameter is a bytearray that contains key A.
        You may specify an address directly or use the mifare_address()
        function to calculate it. Raises an IOError if authentication failed.
        """
        if self._uid == False:
            raise RuntimeError("No Mifare card currently activated.")
        if len(self._uid) == 4:
            uid = self._uid
        elif len(self._uid) == 7: # 10-byte UID cards don't exist yet.
            uid = self._uid[3:7] # Sequence 1, keep it simple.
        self.in_data_exchange(bytearray([MIFARE_COMMAND_AUTH_A,address]) + key_a + uid)

    def mifare_auth_b(self,address,key_b):
        """Authenticate the Mifare card with key B.

        The "key_a" parameter is a bytearray that contains key B.
        You may specify an address directly or use the mifare_address()
        function to calculate it. Raises an IOError if authentication failed.
        """
        if self._uid == False:
            raise RuntimeError("No Mifare card currently activated.")
        if len(self._uid) == 4:
            uid = self._uid
        elif len(self._uid) == 7: # 10-byte UID cards don't exist yet.
            uid = self._uid[3:7] # Sequence 1, keep it simple.
        self.in_data_exchange(bytearray([MIFARE_COMMAND_AUTH_B,address]) + key_b + uid)

    def mifare_read(self,address):
        """Read and return 16 bytes from the data block at the given address."""
        return self.in_data_exchange(bytearray([MIFARE_COMMAND_READ,address]))

    def mifare_write_standard(self,address,data):
        """Write 16 bytes to the data block on a Mifare Standard card
        at the given address."""
        if len(data) > 16:
            raise IndexError("Data cannot exceed 16 bytes (is {0} bytes)".format(len(data)))
        self.in_data_exchange(bytearray([MIFARE_COMMAND_WRITE_16,address]) + data + (b'\x00' * (16 - len(data))))

    def mifare_write_ultralight(self,address,data):
        """Write 4 bytes to the data block on a Mifare Ultralight card
        at the given address."""
        if len(data) > 4:
            raise IndexError("Data cannot exceed 4 bytes (is {0} bytes)".format(len(data)))
        self.in_data_exchange(bytearray([MIFARE_COMMAND_WRITE_4,address]) + data + (b'\x00' * (4 - len(data))))

    def mifare_read_access(self,address):
        """Returns the access conditions for the block at the given address
        in a three-tuple of booleans (C1,C2,C3)."""
        sector, index = self.mifare_sector_block(address)
        if address < 128:
            data = self.mifare_read(address | 3)
        else:
            data = self.mifare_read(address | 15)
            index = math.floor(index / 5)
        return (data[7] & 1 << 4 + index > 0,data[8] & 1 << index > 0,data[8] & 1 << 4 + index > 0)

    def mifare_write_access(self,address,c1,c2,c3,key_a,key_b):
        """Changes the access conditions for the block at the given address
        to the three booleans c1,c2,c3.

        YOU SHOULD REALLY KNOW WHAT YOU'RE DOING HERE! With the wrong,
        settings, you may shut yourself out of your card. The keys A
        and B must also be provided because they cannot be read and
        may therefore be overwritten by zeroes (as returned by a
        regular read on the trailer sector).
        """
        sector, index = self.mifare_sector_block(address)
        if address < 128:
            trailer_address = address | 3
        else:
            trailer_address = address | 15
            index = math.floor(index / 5)
        data = self.mifare_read(trailer_address)
        if c1:
            data[7] |= 1 << 4 + index
            data[6] &= ~(1 << index)
        else:
            data[7] &= ~(1 << 4 + index)
            data[6] |= 1 << index
        if c2:
            data[8] |= 1 << index
            data[6] &= ~(1 << 4 + index)
        else:
            data[8] &= ~(1 << index)
            data[6] |= 1 << 4 + index
        if c3:
            data[8] |= 1 << 4 + index
            data[7] &= ~(1 << index)
        else:
            data[8] &= ~(1 << 4 + index)
            data[7] |= 1 << index
        data = key_a + data[6:10] + key_b
        self.mifare_write_standard(trailer_address,data)

    def mifare_change_keys(self,address,key_a,key_b):
        """Changes the authorization keys A and B for the block at
        the given address.

        KEYS MAY NOT BE READABLE SO MAKE SURE YOU WRITE THEM DOWN!
        If you forget a key (especially key A), you may not be able
        to authenticate a block anymore and therefore not read it
        or write to it. The factory preset for keys is always
        b'\xFF\xFF\xFF\xFF\xFF\xFF' as defined in MIFARE_FACTORY_KEY.
        """
        if address < 128:
            trailer_address = address | 3
        else:
            trailer_address = address | 15
        data = self.mifare_read(trailer_address)
        data = key_a + data[6:10] + key_b
        self.mifare_write_standard(trailer_address,data)
