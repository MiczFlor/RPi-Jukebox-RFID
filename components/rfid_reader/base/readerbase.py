from abc import ABC, abstractmethod
import inspect
import os


class ReaderBaseClass(ABC):
    """
    Abstract Base Class for all Reader Classes to ensure common API

    Look at template_new_reader.py for documentation how to integrate a new RFID reader
    """
    def __init__(self, description, params, logger):
        super().__init__()
        self.logger = logger
        self.description = description
        self.params = params
        # Get the filename of the module that uses ReaderBaseClass (i.e. derives from it)
        callee_filename = os.path.normpath(inspect.stack()[1].filename)
        logger.info(f"Initializing reader {self.description} from {callee_filename}")
        logger.debug(f"Reader object = {self}")
        logger.info(f"Parameters = {params}")

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        self.logger.debug(f"Cleaning up behind reader '{self.description}'")
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
