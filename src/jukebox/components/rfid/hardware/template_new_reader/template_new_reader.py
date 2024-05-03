# Standard imports from python packages
import logging

# Add your imports here ...
# import third_party_reader_module

# Import the ReaderBaseClass for common API. Leave as this line as it is!
from components.rfid import ReaderBaseClass
import jukebox.cfghandler

# Also import the description string into this module, to make everything available in a single module w/o code duplication
# Leave this line as is!
from .description import DESCRIPTION

# Create logger.
# Logging is fully setup. Just replace '.new' with something meaningful and short
logger = logging.getLogger('jb.rfid.new')
# Get the global handler to the RFID config
cfg = jukebox.cfghandler.get_handler('rfid')


def query_customization() -> dict:
    """
    Query the user for reader parameter customization

    This function will be called during the configuration/setup phase when the user selects this reader module.
    It must return all configuration parameters that are necessary to later use the Reader class.
    You can ask the user for selections and choices. And/or provide default values.
    If your reader requires absolutely no configuration return {}
    """
    # In the simplest form, this only provides default parameters and relies on the
    # user to modify the config file by hand, e.g. for a reset pin's location
    return {'reset_pin': '12',
            'number_format': 'integer'}


class ReaderClass(ReaderBaseClass):
    """
    The actual reader class that is used to read RFID cards.

    It will be instantiated once and then read_card() is called in an endless loop.

    It will be used in a  manner
      with Reader(reader_cfg_key) as reader:
        for card_id in reader:
          ...
    which ensures proper resource de-allocation. For this to work derive this class from ReaderBaseClass.
    All the required interfaces are implemented there.

    Put your code into these functions (see below for more information)
      - `__init__`
      - read_card
      - cleanup
      - stop
    """
    def __init__(self, reader_cfg_key):
        """
        In the constructor, you will get the `reader_cfg_key` with which you can access the configuration data

        As you are dealing directly with potentially user-manipulated config information, it is
        advisable to do some sanity checks and give useful error messages. Even if you cannot recover gracefully,
        a good error message helps :-)
        """
        # Create a per-instance logger, just in case the reader will run multiple times in various threads
        # Replace '.new' with something meaningful and short
        self._logger = logging.getLogger(f'jb.rfid.new({reader_cfg_key})')
        # Initialize the super-class. Don't change anything here
        super().__init__(reader_cfg_key=reader_cfg_key, description=DESCRIPTION, logger=self._logger)

        # Get the configuration from the rfid.yaml:
        # Lock config around the access
        with cfg:
            # Get a reference to the actual reader-specific config
            config = cfg.getn('rfid', 'readers', reader_cfg_key, 'config', default=None)
            # Read out all values
            # Good practice:
            # Check for missing values and give warning / error depending on severity
            if 'reset_pin' not in config:
                self._logger.warning("Key 'reset_pin' not given in configuration! Using default value: '12'.")
            # For missing values, set default values if possible
            self.number_format = config.setdefault('number_format', 'decimal')
            # If default values make no sense, just use get. That will raise an exception if the value is missing
            self.reset_pin = config.get('reset_pin')

        self._logger.debug(f"Config reset_pin = {self.reset_pin}, number_format = {self.number_format}")
        self._keep_running = True

    def cleanup(self):
        """
        The cleanup function: free and release all resources used by this card reader (if any).

        Put all your cleanup code here, e.g. if you are using the serial bus or GPIO pins.
        Will be called implicitly via the __exit__ function
        This function must exist! If there is nothing to do, just leave the pass statement in place below
        """
        pass

    def stop(self):
        """
        This function is called to tell the reader to exist it's reading function.

        This function is called before cleanup is called.

        > [!NOTE]
        > This is usually called from a different thread than the reader's thread! And this is the reason for the
        > two-step exit strategy. This function works across threads to indicate to the reader that is should stop attempt
        > to read a card. Once called, the function read_card will not be called again. When the reader thread exits
        > cleanup is called from the reader thread itself.

        """
        self._keep_running = False

    def read_card(self) -> str:
        """
        Blocking or non-blocking function that waits for a new card to appear and return the card's UID as string

        This is were your main code goes :-)
        This function must return a string with the card id
        In case of error, it may return None or an empty string

        The function should break and return with an empty string, once stop() is called
        """
        if not self._keep_running:
            return ''
        # third_party_reader_module.read_card() and so on
