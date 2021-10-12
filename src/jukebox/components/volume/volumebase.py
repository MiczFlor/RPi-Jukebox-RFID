import logging
from abc import ABC, abstractmethod


class VolumeBaseClass(ABC):
    """
    Abstract Base Class for all Volume Classes to ensure common API
    """
    def __init__(self, logger: logging.Logger):
        super().__init__()
        self.logger = logger

    @abstractmethod
    def get_volume(self):
        pass

    @abstractmethod
    def set_volume(self, volume):
        pass

    @abstractmethod
    def mute(self):
        pass

    @abstractmethod
    def unmute(self):
        pass

    @abstractmethod
    def inc_volume(self, step):
        pass

    @abstractmethod
    def dec_volume(self, step):
        pass
