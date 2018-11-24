import threading

RASPBERRY = object()
BEAGLEBONE = object()
board = RASPBERRY
try:
    # Try with Raspberry PI imports first
    import spidev
    import RPi.GPIO as GPIO
    SPIClass = spidev.SpiDev
    def_pin_rst = 22
    def_pin_irq = 18
    def_pin_mode = GPIO.BOARD
except ImportError:
    # If they failed, try with Beaglebone
    import Adafruit_BBIO.SPI as SPI
    import Adafruit_BBIO.GPIO as GPIO
    SPIClass = SPI.SPI
    board = BEAGLEBONE
    def_pin_rst = "P9_23"
    def_pin_irq = "P9_15"
    def_pin_mode = None

class RFID(object):
    pin_rst = 22
    pin_ce = 0
    pin_irq = 18

    mode_idle = 0x00
    mode_auth = 0x0E
    mode_receive = 0x08
    mode_transmit = 0x04
    mode_transrec = 0x0C
    mode_reset = 0x0F
    mode_crc = 0x03

    auth_a = 0x60
    auth_b = 0x61

    act_read = 0x30
    act_write = 0xA0
    act_increment = 0xC1
    act_decrement = 0xC0
    act_restore = 0xC2
    act_transfer = 0xB0

    act_reqidl = 0x26
    act_reqall = 0x52
    act_anticl = 0x93
    act_select = 0x93
    act_end = 0x50

    reg_tx_control = 0x14
    length = 16

    antenna_gain = 0x04

    authed = False
    irq = threading.Event()

    def __init__(self, bus=0, device=0, speed=1000000, pin_rst=def_pin_rst,
            pin_ce=0, pin_irq=def_pin_irq, pin_mode = def_pin_mode):
        self.pin_rst = pin_rst
        self.pin_ce = pin_ce
        self.pin_irq = pin_irq

        self.spi = SPIClass()
        self.spi.open(bus, device)
        if board == RASPBERRY:
            self.spi.max_speed_hz = speed
        else:
            self.spi.mode = 0
            self.spi.msh = speed

        if pin_mode is not None:
            GPIO.setmode(pin_mode)
        if pin_rst != 0:
            GPIO.setup(pin_rst, GPIO.OUT)
            GPIO.output(pin_rst, 1)
        GPIO.setup(pin_irq, GPIO.IN, pull_up_down=GPIO.PUD_UP)
        GPIO.add_event_detect(pin_irq, GPIO.FALLING,
                callback=self.irq_callback)
        if pin_ce != 0:
            GPIO.setup(pin_ce, GPIO.OUT)
            GPIO.output(pin_ce, 1)
        self.init()

    def init(self):
        self.reset()
        self.dev_write(0x2A, 0x8D)
        self.dev_write(0x2B, 0x3E)
        self.dev_write(0x2D, 30)
        self.dev_write(0x2C, 0)
        self.dev_write(0x15, 0x40)
        self.dev_write(0x11, 0x3D)
        self.dev_write(0x26, (self.antenna_gain<<4))
        self.set_antenna(True)

    def spi_transfer(self, data):
        if self.pin_ce != 0:
            GPIO.output(self.pin_ce, 0)
        r = self.spi.xfer2(data)
        if self.pin_ce != 0:
            GPIO.output(self.pin_ce, 1)
        return r

    def dev_write(self, address, value):
        self.spi_transfer([(address << 1) & 0x7E, value])

    def dev_read(self, address):
        return self.spi_transfer([((address << 1) & 0x7E) | 0x80, 0])[1]

    def set_bitmask(self, address, mask):
        current = self.dev_read(address)
        self.dev_write(address, current | mask)

    def clear_bitmask(self, address, mask):
        current = self.dev_read(address)
        self.dev_write(address, current & (~mask))

    def set_antenna(self, state):
        if state == True:
            current = self.dev_read(self.reg_tx_control)
            if ~(current & 0x03):
                self.set_bitmask(self.reg_tx_control, 0x03)
        else:
            self.clear_bitmask(self.reg_tx_control, 0x03)

    def set_antenna_gain(self, gain):
        """
        Sets antenna gain from a value from 0 to 7.
        """
        if 0 <= gain <= 7:
            self.antenna_gain = gain

    def card_write(self, command, data):
        back_data = []
        back_length = 0
        error = False
        irq = 0x00
        irq_wait = 0x00
        last_bits = None
        n = 0

        if command == self.mode_auth:
            irq = 0x12
            irq_wait = 0x10
        if command == self.mode_transrec:
            irq = 0x77
            irq_wait = 0x30

        self.dev_write(0x02, irq | 0x80)
        self.clear_bitmask(0x04, 0x80)
        self.set_bitmask(0x0A, 0x80)
        self.dev_write(0x01, self.mode_idle)

        for i in range(len(data)):
            self.dev_write(0x09, data[i])

        self.dev_write(0x01, command)

        if command == self.mode_transrec:
            self.set_bitmask(0x0D, 0x80)

        i = 2000
        while True:
            n = self.dev_read(0x04)
            i -= 1
            if ~((i != 0) and ~(n & 0x01) and ~(n & irq_wait)):
                break

        self.clear_bitmask(0x0D, 0x80)

        if i != 0:
            if (self.dev_read(0x06) & 0x1B) == 0x00:
                error = False

                if n & irq & 0x01:
                    print("E1")
                    error = True

                if command == self.mode_transrec:
                    n = self.dev_read(0x0A)
                    last_bits = self.dev_read(0x0C) & 0x07
                    if last_bits != 0:
                        back_length = (n - 1) * 8 + last_bits
                    else:
                        back_length = n * 8

                    if n == 0:
                        n = 1

                    if n > self.length:
                        n = self.length

                    for i in range(n):
                        back_data.append(self.dev_read(0x09))
            else:
                print("E2")
                error = True

        return (error, back_data, back_length)

    def request(self, req_mode=0x26):
        """
        Requests for tag.
        Returns (False, None) if no tag is present, otherwise returns (True, tag type)
        """
        error = True
        back_bits = 0

        self.dev_write(0x0D, 0x07)
        (error, back_data, back_bits) = self.card_write(self.mode_transrec, [req_mode, ])

        if error or (back_bits != 0x10):
            return (True, None)

        return (False, back_bits)

    def anticoll(self):
        """
        Anti-collision detection.
        Returns tuple of (error state, tag ID).
        """
        back_data = []
        serial_number = []

        serial_number_check = 0

        self.dev_write(0x0D, 0x00)
        serial_number.append(self.act_anticl)
        serial_number.append(0x20)

        (error, back_data, back_bits) = self.card_write(self.mode_transrec, serial_number)
        if not error:
            if len(back_data) == 5:
                for i in range(4):
                    serial_number_check = serial_number_check ^ back_data[i]

                if serial_number_check != back_data[4]:
                    error = True
            else:
                error = True

        return (error, back_data)

    def calculate_crc(self, data):
        self.clear_bitmask(0x05, 0x04)
        self.set_bitmask(0x0A, 0x80)

        for i in range(len(data)):
            self.dev_write(0x09, data[i])
        self.dev_write(0x01, self.mode_crc)

        i = 255
        while True:
            n = self.dev_read(0x05)
            i -= 1
            if not ((i != 0) and not (n & 0x04)):
                break

        ret_data = []
        ret_data.append(self.dev_read(0x22))
        ret_data.append(self.dev_read(0x21))

        return ret_data

    def select_tag(self, uid):
        """
        Selects tag for further usage.
        uid -- list or tuple with four bytes tag ID
        Returns error state.
        """
        back_data = []
        buf = []

        buf.append(self.act_select)
        buf.append(0x70)

        for i in range(5):
            buf.append(uid[i])

        crc = self.calculate_crc(buf)
        buf.append(crc[0])
        buf.append(crc[1])

        (error, back_data, back_length) = self.card_write(self.mode_transrec, buf)

        if (not error) and (back_length == 0x18):
            return False
        else:
            return True

    def card_auth(self, auth_mode, block_address, key, uid):
        """
        Authenticates to use specified block address. Tag must be selected using select_tag(uid) before auth.
        auth_mode -- RFID.auth_a or RFID.auth_b
        key -- list or tuple with six bytes key
        uid -- list or tuple with four bytes tag ID
        Returns error state.
        """
        buf = []
        buf.append(auth_mode)
        buf.append(block_address)

        for i in range(len(key)):
            buf.append(key[i])

        for i in range(4):
            buf.append(uid[i])

        (error, back_data, back_length) = self.card_write(self.mode_auth, buf)
        if not (self.dev_read(0x08) & 0x08) != 0:
            error = True

        if not error:
            self.authed = True

        return error

    def stop_crypto(self):
        """Ends operations with Crypto1 usage."""
        self.clear_bitmask(0x08, 0x08)
        self.authed = False

    def halt(self):
        """Switch state to HALT"""

        buf = []
        buf.append(self.act_end)
        buf.append(0)

        crc = self.calculate_crc(buf)
        self.clear_bitmask(0x08, 0x80)
        self.card_write(self.mode_transrec, buf)
        self.clear_bitmask(0x08, 0x08)
        self.authed = False

    def read(self, block_address):
        """
        Reads data from block. You should be authenticated before calling read.
        Returns tuple of (error state, read data).
        """
        buf = []
        buf.append(self.act_read)
        buf.append(block_address)
        crc = self.calculate_crc(buf)
        buf.append(crc[0])
        buf.append(crc[1])
        (error, back_data, back_length) = self.card_write(self.mode_transrec, buf)

        if len(back_data) != 16:
            error = True

        return (error, back_data)

    def write(self, block_address, data):
        """
        Writes data to block. You should be authenticated before calling write.
        Returns error state.
        """
        buf = []
        buf.append(self.act_write)
        buf.append(block_address)
        crc = self.calculate_crc(buf)
        buf.append(crc[0])
        buf.append(crc[1])
        (error, back_data, back_length) = self.card_write(self.mode_transrec, buf)
        if not(back_length == 4) or not((back_data[0] & 0x0F) == 0x0A):
            error = True

        if not error:
            buf_w = []
            for i in range(16):
                buf_w.append(data[i])

            crc = self.calculate_crc(buf_w)
            buf_w.append(crc[0])
            buf_w.append(crc[1])
            (error, back_data, back_length) = self.card_write(self.mode_transrec, buf_w)
            if not(back_length == 4) or not((back_data[0] & 0x0F) == 0x0A):
                error = True

        return error

    def irq_callback(self, pin):
        self.irq.set()

    def wait_for_tag(self):
        # enable IRQ on detect
        self.init()
        self.irq.clear()
        self.dev_write(0x04, 0x00)
        self.dev_write(0x02, 0xA0)
        # wait for it
        waiting = True
        while waiting:
            self.dev_write(0x09, 0x26)
            self.dev_write(0x01, 0x0C)
            self.dev_write(0x0D, 0x87)
            waiting = not self.irq.wait(0.1)
        self.irq.clear()
        self.init()

    def reset(self):
        authed = False
        self.dev_write(0x01, self.mode_reset)

    def cleanup(self):
        """
        Calls stop_crypto() if needed and cleanups GPIO.
        """
        if self.authed:
            self.stop_crypto()
        GPIO.cleanup()

    def util(self):
        """
        Creates and returns RFIDUtil object for this RFID instance.
        If module is not present, returns None.
        """
        try:
            from .util import RFIDUtil
            return RFIDUtil(self)
        except ImportError:
            return None
