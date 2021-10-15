import logging
import serial

import misc.inputminus as pyil
from misc.simplecolors import Colors
from components.rfid import ReaderBaseClass
import jukebox.cfghandler

from .description import DESCRIPTION

# Create logger
logger = logging.getLogger('jb.rfid.rdm6300')
cfg = jukebox.cfghandler.get_handler('rfid')

NUMBER_FORMAT = ['card_id_dec',
                 'card_id_raw',
                 'card_id_float']
NUMBER_FORMAT_HELP = ['A 10 digit card ID e.g. 0006762840 (default)',
                      'The raw (un-decoded) card ID e.g. 070067315809',
                      'The card ID as fraction e.g. 103,12632']
NUMBER_FORMAT_HINT = ['This number is often printed on the back of the card and identical to the read-out from an USB reader',
                      'Previously the only option of the RDM6300 reader. Choose this if you want to use an existing database',
                      '']


def query_customization() -> dict:
    config = {'device': '/dev/ttyS0',
              'baudrate': 9600,
              'serial_timeout': 0.1,
              'log_all_cards': False}
    prompt_color = Colors.lightgreen
    print(f"RDM6300:\n"
          f"I am configuring everything for the default UART, i.e. using '{config['device']}' with "
          f"'{config['baudrate']}' baud\n. "
          "If you need something else, simply change the yaml configuration file by hand!\n")
    print("Select number format:")
    for idx, val in enumerate(NUMBER_FORMAT):
        print(f" {Colors.lightgreen}{idx:2d}{Colors.reset}: {Colors.lightcyan}{Colors.bold}{val:15}{Colors.reset}: "
              f"{NUMBER_FORMAT_HELP[idx]}")
        print(f"                      {Colors.lightgrey}{NUMBER_FORMAT_HINT[idx]}{Colors.reset}")
    dev_id = pyil.input_int("Number format?", blank=0, min=0, max=len(NUMBER_FORMAT) - 1,
                            prompt_color=prompt_color, prompt_hint=True)
    config['number_format'] = NUMBER_FORMAT[dev_id]
    return config


def decode(raw_card_id: bytearray, number_format: int) -> str:
    """Decode the RDM6300 data format into actual card ID"""
    # Length: 12 characters
    #    ... which are ASCII characters
    #       ... which encode a hexadecimal value with 6 bytes (2 ascii char encode 1 byte)
    # Byte   0: Version number / Manufacturer code
    # Byte 1-4: Card ID
    # Byte   5: Checksum = XOR(byte[0:-1])
    if len(raw_card_id) != 12:
        raise ValueError(f"Incorrect length of raw card ID: {raw_card_id} with length = {len(raw_card_id)}!")

    # Decode the ASCI characters to actual bytes:
    real_bytes = int(raw_card_id, 16).to_bytes(6, byteorder='big')
    # Calculate checksum with XOR over all bytes: check_sum = functools.reduce(lambda x, y: x ^ y, real_bytes[0:5])
    # But we are faster if we code it explicitly for these 5 bytes:
    check_sum = real_bytes[0] ^ real_bytes[1] ^ real_bytes[2] ^ real_bytes[3] ^ real_bytes[4]

    if check_sum != real_bytes[5]:
        raise ValueError("Checksum does not match")

    if number_format == 0:
        # Convert byte-array of card id into actual integer:
        card_id = int.from_bytes(real_bytes[1:5], byteorder='big')
        # The actual, decoded 10 digit card ID e.g. 0006762840
        card_str = '{0:010d}'.format(card_id)
    elif number_format == 2:
        # Card ID as fraction e.g. 103,12632
        card_str = '{0:d},{1:05d}'.format(((real_bytes[1] << 8) + real_bytes[2]), ((real_bytes[3] << 8) + real_bytes[4]))
    elif number_format == 1:
        # The un-decoded card ID e.g. 070067315809
        card_str = raw_card_id.decode('ascii')
    else:
        raise ValueError(f"Unknown number format: '{number_format}")

    return card_str


class ReaderClass(ReaderBaseClass):
    def __init__(self, reader_cfg_key):
        self._logger = logging.getLogger(f'jb.rfid.rdm({reader_cfg_key})')
        super().__init__(reader_cfg_key=reader_cfg_key, description=DESCRIPTION, logger=self._logger)

        with cfg:
            config = cfg.setndefault('rfid', 'readers', reader_cfg_key, 'config', value={})
            if 'number_format' not in config:
                self._logger.warning("Missing configuration parameter: 'number_format'. Defaulting to 'card_id_dec'")
            number_format_str = config.setdefault('number_format', default='card_id_dec')
            self.device = config.setdefault('device', default='/dev/ttyS0')
            self.baudrate = config.setdefault('baudrate', default=9600)
            self.serial_timeout = config.setdefault('serial_timeout', default=0.1)
            self.log_all_cards = config.setdefault('log_all_cards', default=False)

        if number_format_str not in NUMBER_FORMAT:
            self._logger.error(f"Unknown value in option: 'number_format={number_format_str}'. "
                               f"Defaulting to '{NUMBER_FORMAT[0]}'!")
            number_format_str = NUMBER_FORMAT[0]
        self.number_format = NUMBER_FORMAT.index(number_format_str)

        try:
            self.rfid_serial = serial.Serial(self.device, self.baudrate, timeout=self.serial_timeout)
        except serial.SerialException as e:
            self._logger.error(f"{e.__class__.__name__}: {e}")
            raise e
        self._keep_running = True

    def cleanup(self):
        if self._keep_running is True:
            self._logger.error("_keep_running True, while closing down. Forgot to call stop() first?")
        self.rfid_serial.close()

    def stop(self):
        self._keep_running = False

    def read_card(self) -> str:
        byte_card_id = bytearray()

        wait_for_start_byte = True
        read_byte = self.rfid_serial.read()
        while self._keep_running:
            if wait_for_start_byte and read_byte == b'\x02':
                # Start receiving an ID
                wait_for_start_byte = False
            elif not wait_for_start_byte and read_byte != b'\x03':
                # Continue receiving ID elements
                byte_card_id.extend(read_byte)
                # We could get stuck here, if terminating char never appears
                # Case A) More chars than expected length -> Simple length check
                # Case B) Less chars then expected length -> Nothing happens until card is read out again,
                #         then length overflows and we get a clean card read-out restart
                if len(byte_card_id) > 12:
                    logger.error("ID length exceeded")
                    self.rfid_serial.reset_input_buffer()
                    return ''
            elif not wait_for_start_byte and read_byte == b'\x03':
                # End receiving an ID
                self.rfid_serial.reset_input_buffer()

                try:
                    card_id = decode(byte_card_id, self.number_format)
                except Exception as e:
                    logger.error(f"{e.__class__.__name__}: {e}")
                    card_id = ''

                if self.log_all_cards:
                    self._logger.debug(f"Card detected with ID = '{card_id}'")

                return card_id

            read_byte = self.rfid_serial.read()

        self._logger.debug("Raising StopIteration")
        raise StopIteration
