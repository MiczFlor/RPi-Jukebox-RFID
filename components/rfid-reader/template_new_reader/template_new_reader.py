"""Template for creating and integrating a new RFID Reader

This template provides the skeleton API for a new Reader.
If you follow the naming conventions for this file
directly structure convention, it will be picked up automatically.
There is no extra need to register the Reader with the Phoniebox. Just re-run ./register_reader.py

Also have a look at the other reader modules to see how stuff works with an example

File structure:
- Single reader per directory
- Directory name and file name are identical
  -> i.e. awesome_reader/awesome_reader.py
- Note: We deviate slightly from the python naming convention for modules here, as the module name is identical
 to directory name and that should be descriptive enough to know what is going on when looking at the file
 structure in git. Also it should specific enough to allow for later new module additions.
- Naming scheme for the module
  - <type_of_reader>_<io_bus>_<other_specials_like_special_lib>
  - e.g. generic_usb/generic_usb.py
  - e.g. pn532_spi/pn532_spi.py
  - ...
- DO NOT use '-' in the filename! Even if that is the suggested naming convention in the Phoniebox project.
  That is no a valid character in python for module names. It makes loading the module statically a pain.
"""

# Standard imports from python packages
import os
import logging

# IMPORTANT:
# Wrap 3rd party imports that need only be installed when actually using this reader module in a try-except block
# Reason: This way the module can be loaded and things like DESCRIPTION can be read-out even without installing
# all dependencies. As a result all available readers can be listed w/o installing all dependencies.
# As a result only the dependencies for the selected reader need to be installed on the system
# Create a requirements.txt file in your reader's directory. These dependencies are installed automatically when this
# reader is selected for the first time
try:
    import specialized_3rd_party_module
except ModuleNotFoundError:
    pass


# We use logger to control debug messages.
# This is fully setup. You can go ahead and simply use logger.debug()/warning()/error()/info()
# The logging level is also controlled from the readersupport module. It relies an the names below,
# so please do not change them, or the logging control will be broken
# Create logger
logger = logging.getLogger(os.path.basename(__file__).ljust(25))
logger.setLevel(logging.DEBUG)
# Create console handler and set default level (may be overwritten by readersupport module)
logconsole = logging.StreamHandler()
logconsole.setFormatter(logging.Formatter('%(asctime)s - %(name)s - %(levelname)-8s: %(message)s', datefmt='%d.%m.%Y %H:%M:%S'))
logconsole.setLevel(logging.INFO)
logger.addHandler(logconsole)


"""Provide a short title for this reader.
This is what that user will see when asked for selecting his Reader
So, be precise but readable."""
DESCRIPTION = 'Template RFID Reader Module'


def query_customization() -> dict:
    """This function will be called during the configuration/setup phase when the user selects this reader module.
    It must return all configuration parameters that are necessary to later use the Reader class.
    You can ask the user for selections and choices. And/or provide default values
    If your reader requires absolutely no configuration return {}"""
    # In the simplest form, this only provides default parameters and relies on the
    # user to modify the config file by hand, e.g. for a reset pin's location
    return {'reset_pin': '12'}


class Reader:
    """The actual reader class that is used to read RFID cards.
    It will be instantiated once and then read_card is called in an endless loop.
    It will be used in a  mannser
      with Redaer(params) as r:
         ...
    which ensures proper resource de-allocation. For this to work do not touch the functions
    __enter__ and __exit__. Put all your cleanup code into cleanup(self)."""

    def __enter__(self):
        # Do not change anything here!
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        # Do not change anything here!
        logger.debug(f"Cleaning up behind reader '{DESCRIPTION}'")
        self.cleanup()

    def __init__(self, params: dict):
        """In the constructor, you will get a dictionary with all the customization options read for this reader from
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
        # In the simplest form, w/o error checks and type conversion, this would simply be to following.
        # But I strongly encourage some logging and sanity checking :-)
        # the_3rd_party_reader(**params)

        # A very neat way is to read the params dict back into a configparser structure. This allows you to use the
        # well-defined functions of the configparser for type conversion and fallback values.
        # Here is an example to get the parameter 'device' (string) and 'timeout' (integer)
        # https://docs.python.org/3/library/configparser.html#configparser.ConfigParser.get
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
        """Blocking function that waits for a new card to appear and return the card's UID as string"""


