"""
RC522 RFID reader via SPI
"""

# Standard imports from python packages
import os
import logging
import configparser

import RPi.GPIO as GPIO
import pirc522

import base.inputminus as pyil
from base.simplecolors import colors
from base.readerbase import *

from .description import DESCRIPTION


logger = logging.getLogger(os.path.basename(__file__).ljust(25))
logger.setLevel(logging.DEBUG)
logconsole = logging.StreamHandler()
logconsole.setFormatter(logging.Formatter('%(asctime)s - %(name)s - %(levelname)-8s: %(message)s', datefmt='%d.%m.%Y %H:%M:%S'))
logconsole.setLevel(logging.INFO)
logger.addHandler(logconsole)


def query_customization() -> dict:
    prompt_color = colors.lightgreen
    print("\nCustomization parameters for the MFRC522:\n"
          "You will be fine with the default parameters if you use the default wiring.\n"
          "Hitting enter will always pick the default value.\n"
          "If unsure just hit 'enter' on all questions.\n"
          "Note: pin numbers refer to GPIOxx numbering!\n")

    print("\nThe SPI CE pin: CE0 or CE1")
    spi_ce = pyil.input_int("SPI CEx?", blank=0, min=0, max=1, prompt_color=prompt_color, prompt_hint=True)

    pin_irq = pyil.input_int("IRQ pin?", blank=24, min=1, max=27, prompt_color=prompt_color, prompt_hint=True)

    print("\nReset pin for hardware reset. This is an optional pin.\n"
          "Enter 0 to disable use of reset pin if you are tight on pins."
          "If not used, "
          " - hardware reset will only be performed by power-on-reset, but not when simply rebooting.\n"
          " - you MUST tie the reset pin of the MFRC522 board HIGH!")
    pin_rst = pyil.input_int("Reset pin?", blank=25, min=0, max=27, prompt_color=prompt_color, prompt_hint=True)

    print("\n4-byte-only legacy mode:\n"
          "Previously the pirc522 library could only read the lower 4 bytes of a card UID. "
          "It can now read 4-byte and 7-byte UIDs.\n"
          "Legacy mode turns back to the old behaviour. This only makes sense,\n"
          "if you already have an large RFID collection and do not want to re-assign every card")
    mode_legacy = pyil.input_yesno("4-byte only legacy mode?", blank=False, prompt_color=prompt_color, prompt_hint=True)

    if not mode_legacy:
        print("\nThe Cards UID can be stored as\n"
              " - integer number\n"
              " - concatenated set of raw bytes")
        uid_as_number = pyil.input_yesno("UID as number?", blank=True, prompt_color=prompt_color, prompt_hint=True)
    else:
        # Legacy mode always uses byte concatenated mode
        uid_as_number = False

    return {'spi_bus': 0,
            'spi_ce': spi_ce,
            'pin_irq': pin_irq,
            'pin_rst': pin_rst,
            'mode_legacy': mode_legacy,
            'uid_as_number': uid_as_number,
            'antenna_gain': 4,
            'log_all_cards': 'false'}


class ReaderClass(ReaderBaseClass):
    def __init__(self, params: dict):
        super().__init__(description=DESCRIPTION, params=params, logger=logger)

        config = configparser.ConfigParser()
        if params is None or len(params) == 0:
            logger.critical("Params dict is empty! Missing mandatory parameters.")
            raise KeyError("Params dict is empty! Missing mandatory parameters.")
        config.read_dict({'params': params})

        spi_bus = config['params'].getint('spi_bus')
        spi_ce = config['params'].getint('spi_ce')
        pin_irq = config['params'].getint('pin_irq')
        self.mode_legacy = config['params'].getboolean('mode_legacy')
        logger.info(f"Using legacy_mode = '{self.mode_legacy}'")
        pin_rst = config['params'].getint('pin_rst', fallback=0)
        if 'pin_rst' not in config['params']:
            logger.warning(f"No parameter 'pin_rst' found. Disabling hardware reset.")
        antenna_gain = config['params'].getint('antenna_gain', fallback=4)
        self.log_all_cards = config['params'].getboolean('log_all_cards', fallback=False)
        self.uid_as_number = config['params'].getboolean('uid_as_number', fallback=False)
        if 'uid_as_number' not in config['params']:
            logger.warning(f"No parameter 'uid_as_number' found. Defaulting to 'False'.")

        self.device = pirc522.RFID(bus=spi_bus,
                                   device=spi_ce,
                                   pin_rst=pin_rst,
                                   pin_irq=pin_irq,
                                   antenna_gain=antenna_gain,
                                   pin_mode=GPIO.BCM)

    def cleanup(self):
        self.device.cleanup()

    def read_card(self) -> str:
        # Scan for cards
        self.device.wait_for_tag()
        if self.mode_legacy:
            error, tag_type = self.device.request()
            if not error:
                # Perform anti-collision detection to find card uid
                error, uid = self.device.anticoll()
                if not error:
                    card_id = ''.join((str(x) for x in uid))
                    if self.log_all_cards:
                        logger.debug(f"Card detected with ID = '{card_id}'")
                    return card_id
            if self.log_all_cards:
                logger.debug("Error during reading card.")
            return ''
        else:
            # For the normal mode use the new convenience function
            uid = self.device.read_id(as_number=self.uid_as_number)
            # Check for empty string or NoneType
            if not uid:
                if self.log_all_cards:
                    logger.debug("Error during reading card.")
                return ''
            else:
                if self.uid_as_number:
                    card_id = str(uid)
                else:
                    card_id = ''.join((str(x) for x in uid))
                if self.log_all_cards:
                    logger.debug(f"Card detected with ID = '{card_id}'")
                return card_id


