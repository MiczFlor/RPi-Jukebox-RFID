"""@package py532lib.frame
This module contains classes and functions related to communication frames for the PN532 NFC Chip.

@author:  DanyO <me@danyo.ca>
@license: The source code within this file is licensed under the BSD 2 Clause license.
          See LICENSE file for more information.

"""

import os
import sys
lib_path = os.path.abspath('../')
sys.path.append(lib_path)

from py532lib.i2c import *
from py532lib.frame import *
from py532lib.constants import *


class Pn532Frame:
    """Pn532Frame represents a single communication frame for
    communication with the PN532 NFC Chip.

    """
    def __init__(
        self, frame_type=PN532_FRAME_TYPE_DATA,
        preamble=PN532_PREAMBLE,
        start_code_1=PN532_START_CODE_1,
        start_code_2=PN532_START_CODE_2,
        frame_identifier=0xD4,
        data=bytearray(),
            postamble=PN532_POSTAMBLE):
        """Constructor for the Pn532Frame class.

        Arguments:
        @param[in]  frame_type      Type of current frame.
                                    (default = PN532_FRAME_TYPE_DATA)

        @param[in]  preamble        Preamble to be used.
                                    (default = PN532_PREAMBLE)

        @param[in]  start_code_1    First byte of frame's start code.
                                    (default = PN532_START_CODE_1)

        @param[in]  start_code_2    Last byte of frame's start code.
                                    (default = PN532_START_CODE_2)

        @param[in]  frame_identifier Frame Identifier.
                                     (default = PN532_IDENTIFIER_HOST_TO_PN532)

        @param[in]  data            Frame's data in a bytearray().

        @param[in]  postamble       Postamble to be used.
                                    (default = PN532_PREAMBLE)

        """
        self._frame_type = frame_type
        self._preamble = preamble
        self._startCode1 = start_code_1
        self._startCode2 = start_code_2
        self._frameIdentifier = frame_identifier
        self._data = data
        self._postamble = postamble

    def get_length(self):
        """Gets the frame's data length."""
        return len(self._data) + 1

    def get_length_checksum(self):
        """Gets the checksum of get_length()."""
        return (~self.get_length() & 0xFF) + 0x01

    def get_data(self):
        """Gets the frame's data."""
        return self._data

    def get_data_checksum(self):
        """Gets a checksum for the frame's data."""
        byte_array = bytearray()

        for byte in self._data:
            byte_array.append(byte)

        byte_array.append(self._frameIdentifier)

        inverse = (~sum(byte_array) & 0xFF) + 0x01

        if inverse > 255:
            inverse = inverse - 255

        return inverse

    def get_frame_type(self):
        """Gets the frame's type."""
        return self._frame_type

    def to_tuple(self):
        byte_array = bytearray()

        if self._frame_type == PN532_FRAME_TYPE_ACK:
            byte_array.append(PN532_PREAMBLE)
            byte_array.append(PN532_START_CODE_1)
            byte_array.append(PN532_START_CODE_2)
            byte_array.append(PN532_START_CODE_1)
            byte_array.append(PN532_START_CODE_2)
            byte_array.append(PN532_POSTAMBLE)

            return (byte_array)

        byte_array.append(self._preamble)
        byte_array.append(self._startCode1)
        byte_array.append(self._startCode2)
        byte_array.append(self.get_length())
        byte_array.append(self.get_length_checksum())
        byte_array.append(self._frameIdentifier)

        for byte in self._data:
            byte_array.append(byte)

        byte_array.append(self.get_data_checksum())
        byte_array.append(self._postamble)

        return (byte_array)

    @staticmethod
    def from_response(response):
        """Fractory that generates a Pn532Frame from a response from the PN532."""
        if Pn532Frame.is_valid_response(response) is not True:
            raise RuntimeError("Invalid Response")

        if Pn532Frame.is_ack(response):
            return Pn532Frame(frame_type=PN532_FRAME_TYPE_ACK,
                              frame_identifier=0x00)

        if Pn532Frame.is_error(response):
            return Pn532Frame(frame_type=PN532_FRAME_TYPE_ERROR,
                             frame_identifier=0x7F,data=b'\x81')

        response_length = response[0][PN532_FRAME_POSITION_LENGTH] + 1
        data = bytearray(
            response[0][PN532_FRAME_POSITION_DATA_START:PN532_FRAME_POSITION_DATA_START + response_length - 2])

        return Pn532Frame(
            preamble=response[0][PN532_FRAME_POSITION_PREAMBLE],
            start_code_1=response[0][PN532_FRAME_POSITION_START_CODE_1],
            start_code_2=response[0][PN532_FRAME_POSITION_START_CODE_2],
            frame_identifier=response[0][
                PN532_FRAME_POSITION_FRAME_IDENTIFIER],
            data=data,
            postamble=response[0][PN532_FRAME_POSITION_DATA_START + response_length + 2])

    @staticmethod
    def is_valid_response(response):
        """Checks if a response from the PN532 is valid."""
        if (response[0][0] & 0x01) == 0x01:
            if response[0][PN532_FRAME_POSITION_PREAMBLE] == PN532_PREAMBLE:
                if response[0][PN532_FRAME_POSITION_START_CODE_1] == PN532_START_CODE_1:
                    if response[0][PN532_FRAME_POSITION_START_CODE_2] == PN532_START_CODE_2:
                        return True

        return False

    @staticmethod
    def is_ack(response):
        """Checks if the response is an ACK frame."""
        if response[0][PN532_FRAME_POSITION_LENGTH] == 0x00:
            if response[0][PN532_FRAME_POSITION_LENGTH_CHECKSUM] == 0xFF:
                if response[0][PN532_FRAME_POSITION_FRAME_IDENTIFIER] == 0x00:
                    return True

        return False

    @staticmethod
    def is_error(response):
        """ Checks if the response is an error frame."""
        if response[0][PN532_FRAME_POSITION_LENGTH] == 0x01:
            if response[0][PN532_FRAME_POSITION_LENGTH_CHECKSUM] == 0xFF:
                if response[0][PN532_FRAME_POSITION_FRAME_IDENTIFIER] == 0x7F:
                    if response[0][PN532_FRAME_POSITION_DATA_START] == 0x81:
                        return True

        return False
