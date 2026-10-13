"""
E-Ink display driver for waveshare 2.9 V3
"""

import logging
from .waveshare_epd import epd2in9d
from .epd2in9b_V3_image_factory import Epd2in9bV3ImageFactory

logger = logging.getLogger('jb.Display.Lcd')

class Epd2in9bV3Display:
    """
    For some rease the waveshare examples, are note able to present
    partial updates on V3 display, but the the *d library it works 
    fine. Without partial update e-ink is usless on the phoniebox.
    """
    def __init__(self):
        self.image_factory = Epd2in9bV3ImageFactory()
        epd = epd2in9d.EPD()
        epd.init()
        epd.Clear()        

    def show(self, title: str, artist: str, album: str = None, paused: bool = False, repeat_info: str = None, coverart: str = None):
        """
        Show title and artist etc. on the display.
        """
        epd = epd2in9d.EPD()
        epd.init()        
        
        epd.DisplayPartial(epd.getbuffer(self.image_factory.create(epd.height, epd.width, title, artist, album, paused, repeat_info)))        
        epd.sleep()

    def clear(self):
        """
        E-Ink is to laty for clearing all the time, so keep it on display
        """
