"""
Image factory for a 320x240 color framebuffer display.

Produces a landscape RGB image with:
- Cover art on the left (or a placeholder if unavailable)
- Artist, album, and title on the right
- Repeat and pause indicators at the bottom right
"""

import os
import textwrap
from typing import Optional

from PIL import Image, ImageDraw, ImageFont  # type: ignore


# Display dimensions
WIDTH = 320
HEIGHT = 240

# Layout constants
COVER_SIZE = 140
COVER_MARGIN = 10
TEXT_LEFT = COVER_SIZE + COVER_MARGIN * 2
TEXT_RIGHT = WIDTH - COVER_MARGIN
TEXT_TOP = 10
LINE_SPACING = 6

# Colors (RGB tuples)
COLOR_BACKGROUND = (20, 20, 25)
COLOR_TEXT_PRIMARY = (255, 255, 255)
COLOR_TEXT_SECONDARY = (180, 180, 180)
COLOR_ACCENT = (0, 200, 255)
COLOR_PAUSE = (255, 200, 0)
COLOR_REPEAT = (100, 255, 100)
COLOR_PLACEHOLDER = (60, 60, 70)


class Fb2in8ImageFactory:
    """
    Create 320x240 RGB images for the fb_2in8 color display.
    """

    def __init__(self):
        self._font_path = os.path.join(
            os.path.dirname(os.path.dirname(os.path.realpath(__file__))),
            'display/resources/Font.ttc'
        )

    def _get_font(self, size: int):
        return ImageFont.truetype(self._font_path, size)

    def _draw_text(self, draw, text: str, x: int, y: int, font_size: int, color, max_width: int):
        """
        Draw text, wrapping to multiple lines if needed. Returns the y-coordinate after the text.
        """
        font = self._get_font(font_size)
        char_width_estimate = font_size * 0.55
        max_chars = int(max_width / char_width_estimate)
        lines = textwrap.wrap(text or '', width=max(max_chars, 1))

        for line in lines:
            draw.text((x, y), line, font=font, fill=color)
            y += font_size + LINE_SPACING

        return y

    def _draw_cover(self, image, coverart: Optional[str]):
        """
        Draw cover art or a placeholder on the left side of the image.
        """
        draw = ImageDraw.Draw(image)
        cover_x = COVER_MARGIN
        cover_y = (HEIGHT - COVER_SIZE) // 2

        if coverart:
            try:
                cover_path = coverart
                if not os.path.isabs(cover_path):
                    # Resolve relative to the webapp build cover-cache directory
                    # From src/jukebox/components/display/ go up 4 levels to project root,
                    # then to src/webapp/build/cover-cache
                    base_dir = os.path.expanduser(
                        os.path.join(
                            os.path.dirname(
                                os.path.dirname(
                                    os.path.dirname(
                                        os.path.dirname(os.path.realpath(__file__))
                                    )
                                )
                            ),
                            'src/webapp/build/cover-cache'
                        )
                    )
                    cover_path = os.path.join(base_dir, cover_path)

                with Image.open(cover_path) as cover:
                    cover = cover.convert('RGB')
                    cover = cover.resize((COVER_SIZE, COVER_SIZE))
                    image.paste(cover, (cover_x, cover_y))
                    return
            except Exception as e:
                # Fall back to placeholder on any error
                pass

        # Placeholder
        draw.rectangle(
            [(cover_x, cover_y), (cover_x + COVER_SIZE, cover_y + COVER_SIZE)],
            fill=COLOR_PLACEHOLDER
        )
        font = self._get_font(18)
        placeholder_text = 'No Cover'
        bbox = draw.textbbox((0, 0), placeholder_text, font=font)
        text_width = bbox[2] - bbox[0]
        text_height = bbox[3] - bbox[1]
        text_x = cover_x + (COVER_SIZE - text_width) // 2
        text_y = cover_y + (COVER_SIZE - text_height) // 2
        draw.text((text_x, text_y), placeholder_text, font=font, fill=COLOR_TEXT_SECONDARY)

    def _draw_status_indicators(self, draw, paused: bool, repeat_info: str):
        """
        Draw repeat and pause indicators at the bottom right.
        """
        indicators = []
        if repeat_info == 'repeat_one':
            indicators.append(('R1', COLOR_REPEAT))
        elif repeat_info == 'repeat_all':
            indicators.append(('RA', COLOR_REPEAT))
        if paused:
            indicators.append(('P', COLOR_PAUSE))

        if not indicators:
            return

        font = self._get_font(18)
        x = TEXT_RIGHT
        y = HEIGHT - 30

        for label, color in reversed(indicators):
            bbox = draw.textbbox((0, 0), label, font=font)
            text_width = bbox[2] - bbox[0]
            x -= text_width + 10
            draw.text((x, y), label, font=font, fill=color)

    def create(self,
               title: str,
               artist: str,
               album: Optional[str] = None,
               paused: bool = False,
               repeat_info: str = '',
               coverart: Optional[str] = None):
        """
        Create a 320x240 RGB image for the framebuffer display.
        """
        image = Image.new('RGB', (WIDTH, HEIGHT), COLOR_BACKGROUND)

        self._draw_cover(image, coverart)

        draw = ImageDraw.Draw(image)
        x = TEXT_LEFT
        y = TEXT_TOP
        max_width = TEXT_RIGHT - TEXT_LEFT

        # Artist
        y = self._draw_text(draw, artist or 'Unknown artist', x, y, 24, COLOR_TEXT_PRIMARY, max_width)
        y += 6

        # Album
        y = self._draw_text(draw, album or 'Unknown album', x, y, 18, COLOR_TEXT_SECONDARY, max_width)
        y += 10

        # Title
        self._draw_text(draw, title or 'Unknown title', x, y, 20, COLOR_ACCENT, max_width)

        # Status indicators
        self._draw_status_indicators(draw, paused, repeat_info)

        return image
