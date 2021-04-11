"""Template for creating and integrating a new RFID Reader

This template provides the skeleton API for a new Reader.
If you follow the conventions outlined below, your new reader will be picked up automatically
There is no extra need to register the Reader with the Phoniebox. Just re-run ./register_reader.py

Also have a look at the other reader subpackages to see how stuff works with an example

Your new reader is a python subpackage with these two mandatory modules (i.e. files)

File structure:

  awesome_reader/
    +- awesome_reader/awesome_reader.py  <-- The actual reader module (this file)
    +- awesome_reader/description.py     <-- A description module w/o dependencies. Do not change the filename!

Note:
- Single reader per directory / subpackage
- Obviously awesome_reader will be replaced with something more descriptive. The naming scheme for the subpackage is
  - <type_of_reader>_<io_bus>_<other_specials_like_special_lib>
  - e.g. generic_usb/generic_usb.py
  - e.g. pn532_spi/pn532_spi.py
  - ...
- Note: We deviate slightly from the python naming convention for modules here, as the module name is identical
  to the directory/subpackage name. And the directory name should be descriptive enough to know what is going on
  when looking at the file structure in git. Also it should specific enough to allow for later new module additions.
  I.e. the name is longer than recommended by Python and contains '_'.
- DO NOT use '-' in the filename! Even if that is the suggested naming convention in the Phoniebox project.
  That is no a valid character in python for module names. It makes loading the module statically a pain.
"""

# Standard imports from python packages
import os
import logging

# Add your imports here ...
# import third_party_reader_module

# Also import the description string into this module, to make everything available in a single module w/o code duplication
# Leave this line as is!
from .description import DESCRIPTION


# We use logger to control debug messages.
# This is fully setup. You can go ahead and simply use logger.info()/debug()/warning()/error()/critical()
# The logging level is also controlled from the readersupport module. It relies an the names below,
# so please do not change them, or the logging control will be broken
logger = logging.getLogger(os.path.basename(__file__).ljust(25))
logger.setLevel(logging.DEBUG)
logconsole = logging.StreamHandler()
logconsole.setFormatter(logging.Formatter('%(asctime)s - %(name)s - %(levelname)-8s: %(message)s', datefmt='%d.%m.%Y %H:%M:%S'))
logconsole.setLevel(logging.INFO)
logger.addHandler(logconsole)


def query_customization() -> dict:
    """This function will be called during the configuration/setup phase when the user selects this reader module.
    It must return all configuration parameters that are necessary to later use the Reader class.
    You can ask the user for selections and choices. And/or provide default values.
    If your reader requires absolutely no configuration return {} or delete this function"""
    # In the simplest form, this only provides default parameters and relies on the
    # user to modify the config file by hand, e.g. for a reset pin's location
    return {'reset_pin': '12'}


class Reader:
    """The actual reader class that is used to read RFID cards.
    It will be instantiated once and then read_card() is called in an endless loop.

    It will be used in a  manner
      with Reader(params) as reader:
        for card_id in reader:
          ...
    which ensures proper resource de-allocation. For this to work do not touch the functions
    __enter__ and __exit__. Put all your cleanup code into cleanup(self).

    Leave __iter__ and __next__ as they are. They are required for the iterator-style usage of this class"""

    def __enter__(self):
        # Do not change anything here!
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        # Do not change anything here!
        logger.debug(f"Cleaning up behind reader '{DESCRIPTION}'")
        self.cleanup()

    def __iter__(self):
        # Do not change anything here!
        return self

    def __next__(self):
        # Do not change anything here! Put your card read-out code in to read_card()
        return self.read_card()

    def __init__(self, params: dict):
        """In the constructor, you will get a dictionary with all the customization options read for this reader
        (and only this reader) from
        the configuration file. Note: all key/value pairs are string because they are read from file with configparser.
        You will need to do type conversion yourself.
        As you are dealing directly with potentially user-manipulated config information, it is
        advisable to do some sanity checks and give useful error messages. Even if you cannot recover gracefully,
        a good error message helps :-)

        Things to consider
        - params should be a dictionary, by could be empty or also be None, if the config file has no relating data.
        - params may no always contain all expected key/value pairs. So you might use default fallback values or
          raise an error depending on the missing information
        """
        # Keep these lines for common status reporting
        logger.info(f"Initializing reader '{DESCRIPTION}' from '{__file__}'")
        logger.info(f"Parameters = {params}")

        # Example 1:
        # In the simplest form, w/o error checks and type conversion, this would simply be to following.
        # But I strongly encourage some logging and sanity checking :-)
        # the_3rd_party_reader(**params)

        # Example 2:
        # A very neat way is to read the params dict back into a configparser structure. This allows you to use the
        # well-defined functions of the configparser for type conversion and fallback values.
        # https://docs.python.org/3/library/configparser.html#configparser.ConfigParser.get
        # Here is an example to get the parameter 'device' (string) and 'timeout' (integer)
        # Also take a look at rdm6300 for an extended working example
        # config = configparser.ConfigParser()
        # config.read_dict({'params': params})
        # device = config['params'].get('device', fallback='/dev/ttyS0')
        # timeout = config['params'].getfloat('timeout', fallback=0.1)

    def cleanup(self):
        """The cleanup function: Free and release all resources used by this card reader. e.g. if you are using the
        serial bus or GPIO pins.
        Will be called implicitly via the __exit__ function
        This function must exist! If there is nothing to do, just leave the pass statement in place below"""
        pass

    def read_card(self) -> str:
        """Blocking function that waits for a new card to appear and return the card's UID as string
        This is were your main code goes :-)

        This function must return a string with the card id
        In case of error, it may return None or an empty string"""
        pass


