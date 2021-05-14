#!/usr/bin/env python3
# This alternative Reader.py script was meant to cover not only USB readers but more.
# It can be used to replace Reader.py if you have readers such as
# RDM6300
import logging

logger = logging.getLogger(__name__)


class Rdm6300Reader:
    def __init__(self, param=None):
        import serial
        device = '/dev/ttyS0'
        baudrate = 9600
        ser_timeout = 0.1
        self.last_card_id = ''
        try:
            self.rfid_serial = serial.Serial(device, baudrate, timeout=ser_timeout)
            self.serial_SerialException = serial.SerialException
        except serial.SerialException as e:
            logger.error(e)
            exit(1)

        self.number_format = ''
        if param is not None:
            nf = param.get("numberformat")
            if nf is not None:
                self.number_format = nf

    def convert_to_weigand26_when_checksum_ok(self, raw_card_id):
        weigand26 = []
        xor = 0
        for i in range(0, len(raw_card_id) >> 1):
            val = int(raw_card_id[i * 2: i * 2 + 2], 16)
            if (i < 5):
                xor = xor ^ val
                weigand26.append(val)
            else:
                chk = val
        if (chk == val):
            return weigand26
        else:
            return None

    def readCard(self):
        byte_card_id = bytearray()

        try:
            while True:
                try:
                    wait_for_start_byte = True
                    while True:
                        read_byte = self.rfid_serial.read()

                        if (wait_for_start_byte):
                            if read_byte == b'\x02':
                                wait_for_start_byte = False
                        else:
                            if read_byte != b'\x03':        # could stuck here, check len? check timeout by len == 0??
                                byte_card_id.extend(read_byte)
                            else:
                                break

                    raw_card_id = byte_card_id.decode('ascii')
                    byte_card_id.clear()
                    self.rfid_serial.reset_input_buffer()

                    if len(raw_card_id) == 12:
                        w26 = self.convert_to_weigand26_when_checksum_ok(raw_card_id)
                        if (w26 is not None):
                            # print ("factory code is ignored" ,w26[0])

                            if self.number_format == 'card_id_dec':
                                # this will return a 10 Digit card ID e.g. 0006762840
                                card_id = '{0:010d}'.format((w26[1] << 24) + (w26[2] << 16) + (w26[3] << 8) + w26[4])
                            elif self.number_format == 'card_id_float':
                                # this will return a fractional card ID e.g. 103,12632
                                card_id = '{0:d},{1:05d}'.format(((w26[1] << 8) + w26[2]), ((w26[3] << 8) + w26[4]))
                            else:
                                # this will return the raw (original) card ID e.g. 070067315809
                                card_id = raw_card_id

                            if card_id != self.last_card_id:
                                self.last_card_id = card_id
                                return self.last_card_id

                except ValueError as ve:
                    logger.error(ve)

        except self.serial_SerialException as se:
            logger.error(se)

    def cleanup(self):
        self.rfid_serial.close()
