# Standard imports from python packages
import logging

import pirc522

import jukebox.cfghandler
from components.rfid import ReaderBaseClass
import misc.inputminus as pyil
from misc.simplecolors import Colors
from .description import DESCRIPTION

logger = logging.getLogger('jb.rfid.rc522')
cfg = jukebox.cfghandler.get_handler('rfid')


def query_customization() -> dict:
    prompt_color = Colors.lightgreen
    print("\nCustomization parameters for the MFRC522:\n"
          "You will be fine with the default parameters if you use the default wiring.\n"
          "Hitting enter will always pick the default value.\n"
          "If unsure just hit 'enter' on all questions.\n"
          "Note: pin numbers refer to GPIOxx numbering!\n")

    print("\nThe SPI CE pin: CE0 or CE1")
    spi_ce = pyil.input_int("SPI CEx (CE0=GPIO8, CE1=GPIO7)?", blank=0, min=0, max=1, prompt_color=prompt_color,
                            prompt_hint=True)

    pin_irq = pyil.input_int("IRQ GPIO pin (BCM numbering)?", blank=24, min=1, max=27, prompt_color=prompt_color,
                             prompt_hint=True)

    print("\nReset GPIO pin for hardware reset. This is an optional pin.\n"
          "Enter 0 to disable use of reset pin if you are tight on pins."
          "If not used, "
          " - hardware reset will only be performed by power-on-reset, but not when simply rebooting.\n"
          " - you MUST tie the reset pin of the MFRC522 board HIGH!")
    pin_rst = pyil.input_int("Reset GPIO pin (BCM numbering)?", blank=25, min=0, max=27, prompt_color=prompt_color,
                             prompt_hint=True)

    print("\n4-byte-only legacy mode:\n"
          "Previously the pirc522 library could only read the lower 4 bytes of a card UID. "
          "It can now read 4-byte and 7-byte UIDs.\n"
          "Legacy mode turns back to the old behaviour. This only makes sense,\n"
          "if you already have an large RFID collection and do not want to re-assign every card")
    mode_legacy = pyil.input_yesno("4-byte only legacy mode?", blank=False, prompt_color=prompt_color, prompt_hint=True)

    return {'spi_bus': 0,
            'spi_ce': spi_ce,
            'pin_irq': pin_irq,
            'pin_rst': pin_rst,
            'mode_legacy': mode_legacy,
            'antenna_gain': 4,
            'log_all_cards': False}


class ReaderClass(ReaderBaseClass):
    def __init__(self, reader_cfg_key):
        self._logger = logging.getLogger(f'jb.rfid.522({reader_cfg_key})')
        super().__init__(reader_cfg_key=reader_cfg_key, description=DESCRIPTION, logger=self._logger)

        with cfg:
            config = cfg.setndefault('rfid', 'readers', reader_cfg_key, 'config', value={})
            if len(config) == 0:
                self._logger.critical("Params dict is empty! Missing mandatory parameters.")
                raise KeyError("Params dict is empty! Missing mandatory parameters.")

            # We cannot reasonably assume default parameters for the pin out
            # If missing add them as Type None, so that users may change the config manually
            spi_bus = config.setdefault('spi_bus', None)
            spi_ce = config.setdefault('spi_ce', None)
            pin_irq = config.setdefault('pin_irq', None)

            if 'pin_rst' not in config:
                self._logger.warning("No parameter 'pin_rst' found. Disabling hardware reset.")
            pin_rst = config.setdefault('pin_rst', 0)

            self.mode_legacy = config.setdefault('mode_legacy', False)
            self._logger.info(f"Using legacy_mode = '{self.mode_legacy}'")

            antenna_gain = config.setdefault('antenna_gain', 4)
            self.log_all_cards = config.setdefault('log_all_cards', False)

        self._keep_running = True
        self._read_function = self._read_card_legacy if self.mode_legacy else self._read_card_normal
        self.device = pirc522.RFID(bus=spi_bus,
                                   device=spi_ce,
                                   pin_rst=pin_rst,
                                   pin_irq=pin_irq,
                                   antenna_gain=antenna_gain,
                                   pin_mode='BCM')

    def cleanup(self):
        self.device.cleanup()

    def stop(self):
        self._keep_running = False
        # Simulate an IRQ Trigger to get out of wait_for_tag in read_card
        self.device.irq.set()

    def _read_card_legacy(self) -> str:
        error, tag_type = self.device.request()
        if not error:
            # Perform anti-collision detection to find card uid
            error, uid = self.device.anticoll()
            if not error:
                card_id = ''.join((str(x) for x in uid))
                if self.log_all_cards is True:
                    self._logger.debug(f"Card detected with ID = '{card_id}'")
                return card_id
        if self.log_all_cards is True:
            self._logger.debug("Error during reading card.")
        return ''

    def _read_card_normal(self) -> str:
        # The Cards UID can be stored as"
        #  - the actual integer UID number (decoded - the right way)
        #  - concatenated set of raw bytes (not decoded - this was previously the only way)
        # Only in legacy mode use raw bytes
        #
        # For the normal mode use the new convenience function
        #
        uid = self.device.read_id(as_number=True)
        # Check for empty string or NoneType
        if not uid:
            if self.log_all_cards is True:
                self._logger.debug("Error during reading card.")
            return ''
        card_id = str(uid)
        if self.log_all_cards is True:
            self._logger.debug(f"Card detected with ID = '{card_id}'")
        return card_id

    def read_card(self) -> str:
        # Scan for cards
        self.device.wait_for_tag()
        if not self._keep_running:
            return ''
        return self._read_function()
