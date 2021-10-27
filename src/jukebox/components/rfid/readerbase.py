import inspect
import os
import logging
from abc import ABC, abstractmethod


class ReaderBaseClass(ABC):
    """
    Abstract Base Class for all Reader Classes to ensure common API

    Look at template_new_reader.py for documentation how to integrate a new RFID reader
    """
    def __init__(self, reader_cfg_key: str, description: str, logger: logging.Logger):
        super().__init__()
        self.logger = logger
        self.description = description
        # Get the filename of the module that uses ReaderBaseClass (i.e. derives from it)
        callee_filename = os.path.normpath(inspect.stack()[1].filename)
        logger.info(f"Initializing reader '{self.description}' from '{callee_filename}'")
        logger.debug(f"Reader object is {self} for reader config key '{reader_cfg_key}'")

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        self.logger.debug("Exiting")
        self.cleanup()

    def __iter__(self):
        return self

    def __next__(self):
        return self.read_card()

    @abstractmethod
    def read_card(self):
        pass

    @abstractmethod
    def cleanup(self):
        pass

    @abstractmethod
    def stop(self):
        pass
