"""
Serial controller for the Raspberry Pi Pico LED strip.

The Pico is connected via USB-Serial and accepts plain text commands such as:
  fill 0 255 0
  chase 255 128 0 30
  rainbow 20
  off
"""

import glob
import logging
import os

try:
    import serial  # type: ignore
except ImportError:
    serial = None

logger = logging.getLogger('jb.LedStrip.Pico')


class PicoLedController:
    """
    Send LED control commands to a Pico over USB-Serial.
    """

    def __init__(self, port: str = None, baud: int = 115200):
        self.baud = baud
        self.port = self._resolve_port(port)

    def _resolve_port(self, preferred_port: str) -> str:
        """
        Return the preferred port if it exists, otherwise auto-detect any USB-ACM device.
        """
        if preferred_port and os.path.exists(preferred_port):
            return preferred_port

        for candidate in sorted(glob.glob('/dev/ttyACM*')):
            return candidate

        return preferred_port or '/dev/ttyACM0'

    def send(self, command: str, timeout: float = 2.0) -> bool:
        """
        Send a command string to the Pico.
        """
        if serial is None:
            logger.error('pyserial is not installed')
            return False

        if not os.path.exists(self.port):
            logger.warning(f'Pico serial port not found: {self.port}')
            return False

        try:
            with serial.Serial(self.port, self.baud, timeout=timeout) as s:
                s.reset_input_buffer()
                s.reset_output_buffer()
                s.write((command + '\n').encode())
                s.flush()
                logger.debug(f'Sent LED command: {command}')
            return True
        except Exception as e:
            logger.error(f'Failed to send "{command}" to {self.port}: {e}')
            return False

    def fill(self, r: int, g: int, b: int):
        self.send(f'fill {r} {g} {b}')

    def off(self):
        self.send('off')

    def chase(self, r: int, g: int, b: int, delay: int):
        self.send(f'chase {r} {g} {b} {delay}')

    def rainbow(self, delay: int):
        self.send(f'rainbow {delay}')

    def set_led(self, index: int, r: int, g: int, b: int):
        self.send(f'set {index} {r} {g} {b}')

    def range(self, start: int, end: int, r: int, g: int, b: int):
        self.send(f'range {start} {end} {r} {g} {b}')
