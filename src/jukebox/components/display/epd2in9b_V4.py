"""
E-Ink display driver for waveshare 2.9 V4
"""
    
import logging

from .waveshare_epd import epd2in9b_V4
from .epd2in9b_V4_image_factory import Epd2in9bV4ImageFactory

logger = logging.getLogger('jb.Display.Lcd')

class Epd2in9bV4Display:
    """
    E-Ink display driver for waveshare 2.9 V4
    """
    def __init__(self):
        self.image_factory = Epd2in9bV4ImageFactory()
        epd = epd2in9b_V4.EPD()
        epd.init()
        epd.Clear()
        epd.display_Base_color(0xFF)

    def show(self, title: str, artist: str, album: str = None, paused: bool = False, repeat_info: str = None, coverart: str = None):
        """
        Show title and artist etc. on the display.
        """
        epd = epd2in9b_V4.EPD()        
        image = self.image_factory.create(epd.height, epd.width, title, artist, album, paused, repeat_info)
        epd.display_Partial(epd.getbuffer(image), 5, 5, epd.width - 5, epd.height - 5)        

    def clear(self):
        """
        E-Ink is to laty for clearing all the time, so keep it on display
        """
