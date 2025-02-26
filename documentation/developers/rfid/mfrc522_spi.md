# MFRC522 SPI Reader

RC522 RFID reader via SPI connection.

**place-capable**: yes

## Installation

Run the [RFID reader configuration tool](../coreapps.md#RFID-Reader) for guided installation.

## Options

In principle Raspberry PIs support multiple SPI interfaces. The reader
class is based on pi-rc522 which uses spidev. This allows to use
different SPI bus configurations. The below parameters regarding pin-out
are just routed through to spidev. Have a look at the spidev
documentation for details if you really want to use a different SPI bus.
The default setup makes most sense for almost everyone.

### spi_bus *(default=0)*

The SPI Bus ID. The default bus is 0. For other bus IDs, the RPi also needs to re-configured. For that reason we set this to zero.

### spi_ce *(default=0)*

SPI chip enable pin. On default SPI bus 0, this can be

- 0 = GPIO8 (Pin 24)
- 1 = GPIO7 (Pin 26)

For other SPI buses refer to RPi documentation.

### pin_irq

Mandatory IRQ pin. This can be any GPIO pin.

### pin_rst *(default=0)*

Reset pin for hardware reset. This is an optional pin. If not used,

- hardware reset will only be performed by power-on-reset. This has been tested and works fine.
- you **must** tie the reset pin of the MFRC522 board **high**!

### mode_legacy *(default=false)*

4-byte-only legacy mode: previously the pirc522 library could only read the lower 4 bytes of a card UID. It can now read 4-byte and full 7-byte UIDs. Legacy mode turns back to the old behaviour. This only makes sense, if you already have an large RFID collection and do not want to re-assign every card.

### antenna_gain *(default=4)*

Antenna gain factor of the RFID reader chip on the MFRC522 board.

### log_all_cards *(default=false)*

If true all card read-outs will be logged, even when card is permanently on reader. Only for debugging.

## Board Connections

The following pin-out is for the default SPI Bus 0 on Raspberry Pins.

### MFRC522 default wiring (spi_bus=0, spi_ce=0)

|Pin Board Name  |Function  |RPI GPIO  |RPI Pin  |
|----------------|----------|----------|---------|
|SDA             |CE        |GPIO8     |24       |
|SCK             |SCLK      |GPIO11    |23       |
|MOSI            |MOSI      |GPIO10    |19       |
|MISO            |MISO      |GPIO9     |21       |
|IRQ GND         |IRQ       |GPIO24    |18       |
|RST 3.3V        |RST       |GPIO25    |22       |

Some RC522 boards use reversed labeling for MOSI and MISO pins. The good
thing is, no harm is done to the card reader when incorrectly connected.
In case no cards are read, try swapping the connections for MOSI and
MISO.

## Hardware

MFRC522 boards can be picked up from many places for little money.

### Cards/Tags

Cards or tags must support 13.56 MHz. Currently, only cards/tags of the type "NXP Mifare Classic 1k(S50)", "NXP Mifare Classic 4k(S70)" and "NXP Mifare Ultralight (C)" can be used. Type "NXP Mifare NTAG2xx" or others will not work!
