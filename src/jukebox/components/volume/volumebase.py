import logging

from abc import ABC, abstractmethod

import jukebox.cfghandler
from jukebox import plugs


class VolumeBaseClass(ABC):
    """
    Abstract Base Class for all Volume Classes to ensure common API
    """
    def __init__(self, logger: logging.Logger, cfg: jukebox.cfghandler):
        super().__init__()
        self.logger = logger
        self.cfg = cfg
        self._max_volume = 100

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

    @plugs.tag
    def set_max_volume(self, max_volume):
        self.logger.debug(f"Set Max Volume = {max_volume}")
        if not 0 <= max_volume <= 100:
            self.logger.warning(f"set_max_volume: volume out-of-range: {max_volume}")
        self._max_volume = max_volume
        if max_volume < self.get_volume():
            self.set_volume(max_volume)
        # Making max_volume persistent for reboot
        self.cfg.setn('volume', 'max_volume', value=self._max_volume)
        return self.get_max_volume()

    @plugs.tag
    def get_max_volume(self):
        return self._max_volume
