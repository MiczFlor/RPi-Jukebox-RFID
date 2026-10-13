"""
Framebuffer display driver for a 320x240 color LCD.

Writes images directly to a Linux framebuffer device (e.g. /dev/fb0).
Supports dynamic stride handling to avoid screen artifacts.
Supports rgb888 (24 bit) and rgb565 (16 bit) color formats.
"""

import fcntl
import logging
import os
import struct

from PIL import Image  # type: ignore

from .fb_2in8_image_factory import Fb2in8ImageFactory

logger = logging.getLogger('jb.Display.Fb2in8')


class Fb2in8Display:
    """
    Framebuffer display driver for a 320x240 color LCD.
    """

    def __init__(self, framebuffer: str = '/dev/fb0', color_format: str = 'rgb888'):
        self._framebuffer = framebuffer
        self._width = 320
        self._height = 240
        self._color_format = color_format.lower()
        self.image_factory = Fb2in8ImageFactory()

    def show(self, title: str, artist: str, album: str = None, paused: bool = False,
             repeat_info: str = None, coverart: str = None):
        """
        Render and display the current track information on the framebuffer.
        """
        try:
            image = self.image_factory.create(title, artist, album, paused, repeat_info or '', coverart)
            self._write_to_framebuffer(image)
        except Exception as e:
            logger.error(f'Error rendering framebuffer display: {e}')

    def clear(self):
        """
        Clear the framebuffer by filling it with black pixels.
        """
        try:
            image = Image.new('RGB', (self._width, self._height), (0, 0, 0))
            self._write_to_framebuffer(image)
        except Exception as e:
            logger.error(f'Error clearing framebuffer display: {e}')

    def _get_framebuffer_geometry(self):
        """
        Query the framebuffer device for its real geometry.
        Returns (xres, yres, bits_per_pixel, stride_bytes).
        """
        ioctl_fbioget_vscreeninfo = 0x4600

        with open(self._framebuffer, 'rb') as fb:
            fbuf = bytearray(160)
            fcntl.ioctl(fb.fileno(), ioctl_fbioget_vscreeninfo, fbuf)

            xres = struct.unpack('@I', fbuf[0:4])[0]
            yres = struct.unpack('@I', fbuf[4:8])[0]
            bits_per_pixel = struct.unpack('@I', fbuf[24:28])[0]
            stride = struct.unpack('@I', fbuf[48:52])[0]

            return xres, yres, bits_per_pixel, stride

    def _write_to_framebuffer(self, image: Image):
        """
        Write a PIL RGB image to the Linux framebuffer device, respecting the
        framebuffer's real stride (bytes per line) so that no artifacts appear.
        """
        if not os.path.exists(self._framebuffer):
            logger.warning(f'Framebuffer device not found: {self._framebuffer}')
            return

        xres, yres, bpp, stride = self._get_framebuffer_geometry()
        logger.debug(f'Framebuffer geometry: {xres}x{yres}, {bpp}bpp, stride={stride}')

        image = image.convert('RGB')
        image = image.resize((xres, yres))

        if self._color_format == 'rgb565':
            raw = self._convert_to_rgb565_strided(image, stride)
        else:
            raw = self._convert_to_rgb888_strided(image, stride)

        with open(self._framebuffer, 'wb') as fb:
            fb.write(raw)
            fb.flush()

        logger.debug(f'Wrote {len(raw)} bytes to {self._framebuffer} (format={self._color_format})')

    def _convert_to_rgb565_strided(self, image: Image, stride: int) -> bytes:
        """
        Convert a PIL RGB image to RGB565 little-endian bytes, including line padding
        to match the framebuffer stride.
        """
        pixels = list(image.getdata())
        raw = bytearray()
        line_bytes = self._width * 2
        padding = stride - line_bytes

        for y in range(self._height):
            for x in range(self._width):
                idx = y * self._width + x
                r, g, b = pixels[idx]
                rgb565 = ((r >> 3) << 11) | ((g >> 2) << 5) | (b >> 3)
                raw.append(rgb565 & 0xFF)
                raw.append((rgb565 >> 8) & 0xFF)
            raw.extend(b'\x00' * padding)

        return bytes(raw)

    def _convert_to_rgb888_strided(self, image: Image, stride: int) -> bytes:
        """
        Convert a PIL RGB image to RGB888 bytes, including line padding to match the
        framebuffer stride.
        """
        pixels = list(image.getdata())
        raw = bytearray()
        line_bytes = self._width * 3
        padding = stride - line_bytes

        for y in range(self._height):
            for x in range(self._width):
                idx = y * self._width + x
                r, g, b = pixels[idx]
                raw.extend([r, g, b])
            raw.extend(b'\x00' * padding)

        return bytes(raw)
