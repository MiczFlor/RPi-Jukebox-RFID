import textwrap
import os
from PIL import Image, ImageDraw, ImageFont # type: ignore

class Epd2in9bV3ImageFactory:
    
    def _get_font(self, size: int):
        return ImageFont.truetype(os.path.join(os.path.dirname(os.path.dirname(os.path.realpath(__file__))), 'display/resources/Font.ttc'), size)
    
    def create(self, 
               epd_height: int,
               epd_width: int,
               title: str, 
               artist: str, 
               album: str = None, 
               paused: bool = False, 
               repeat_info: str = None):
        
        line0 = artist if artist else 'Unknown artist'        
        
        lines_album = textwrap.wrap(album or '', width=35)
        
        line1 = lines_album[0] if len(lines_album) > 0 else 'Unknown album'
        line2 = lines_album[1] if len(lines_album) > 1 else ''
        
        lines_title = textwrap.wrap(title or '', width=35)
        
        line3 = lines_title[0] if len(lines_title) > 0 else 'Unknown title'
        line4 = lines_title[1][25:] if len(lines_title) > 1 else ''

        font24 = self._get_font(24);
        font18 = self._get_font(18);

        image = Image.new('1', (epd_height, epd_width), 0)
        draw = ImageDraw.Draw(image)
        draw.text((10, 0), line0, font = font24, fill = 255)
        draw.text((10, 29), line1, font = font18, fill = 255)
        draw.text((10, 49), line2, font = font18, fill = 255)
        
        draw.text((10, 75), line3, font = font18, fill = 255)
        draw.text((10, 99), line4, font = font18, fill = 255)
        
        if repeat_info == 'repeat_one':
            draw.text((240, 99), "[R1]", font = font18, fill = 255)
        elif repeat_info == 'repeat_all':
            draw.text((240, 99), "[RA]", font = font18, fill = 255)
        else:
            draw.text((240, 99), "   ", font = font18, fill = 255)
            
        if paused:
            draw.text((270, 99), "[P]", font = font18, fill = 255)
        elif repeat_info == 'repeat_all':
            draw.text((270, 99), "   ", font = font18, fill = 255)
            
        return image;