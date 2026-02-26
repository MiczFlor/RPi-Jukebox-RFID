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

### spi_bus _(0)_

The SPI Bus ID. Fixed to 0, because other bus IDs also need re-configuration of the RPi (refer to RPi documentation).

### spi_ce _(default=0)_

The SPI Chip Select (CEx) pin. Mandatory.

This can be:

- 0 = GPIO8 (SPI0 CE0) - Pin 24
- 1 = GPIO7 (SPI0 CE1) - Pin 26

### pin_irq _(default=24)_

The IRQ GPIO pin for card detection. This is an optional pin, but required for interrupt-driven card detection.

If not used:

- uses polling mode instead of interrupt event
- has high CPU usage and may impact system performance!
- only use this mode if you have serious interrupt conflicts

### pin_rst _(default=25)_

The Reset GPIO pin for hardware reset. This is an optional pin.

If not used:

- hardware reset will only be performed by power-on-reset. This has been tested and works fine.
- you **_must_** tie the reset pin of the MFRC522 board **_high_**!

### mode_legacy _(default=false)_

4-byte-only legacy mode: previously the pirc522 library could only read the lower 4 bytes of a card UID. It can now read 4-byte and full 7-byte UIDs. Legacy mode turns back to the old behaviour. This only makes sense, if you already have an large RFID collection and do not want to re-assign every card.

### antenna_gain _(default=4)_

Antenna gain factor of the RFID reader chip on the MFRC522 board.

### log_all_cards _(default=false)_

If true all card read-outs will be logged, even when card is permanently on reader. Only for debugging.

## Board Connections

The following pin-out is for the default SPI Bus 0 on Raspberry Pins.

### MFRC522 default wiring (spi_bus=0, spi_ce=0)

|MFRC522 Pin Name  |Function            |RPI GPIO          |RPI Pin  |
|------------------|--------------------|------------------|---------|
|SDA               |Chip Select (CE)    |GPIO8 (SPI0 CE0)  |24       |
|SCK               |Serial Clock        |GPIO11 (SPI0 SCLK)|23       |
|MOSI              |Master Out, Slave In|GPIO10 (SPI0 MOSI)|19       |
|MISO              |Master In, Slave Out|GPIO9 (SPI0 MISO) |21       |
|IRQ               |Interrupt Request   |GPIO24            |18       |
|GND               |Ground              |                  |20       |
|RST               |Reset               |GPIO25            |22       |
|3.3V              |Power               |                  |17       |

Some RC522 boards use reversed labeling for MOSI and MISO pins. The good
thing is, no harm is done to the card reader when incorrectly connected.
In case no cards are read, try swapping the connections for MOSI and
MISO.

## Hardware

MFRC522 boards can be picked up from many places for little money.

### Cards/Tags

Cards or tags must support 13.56 MHz. Currently, only cards/tags of the type "NXP Mifare Classic 1k(S50)", "NXP Mifare Classic 4k(S70)" and "NXP Mifare Ultralight (C)" can be used. Type "NXP Mifare NTAG2xx" or others will not work!
