MFRC522 SPI Reader
--------------------

.. |fileonly| replace:: This setting can only be changed by directly modifying the reader.yaml configuration file after the configuration tool has been run.

RC522 RFID reader via SPI connection.

**place-capable**: yes

Installation
^^^^^^^^^^^^^^

Run the ref:`run_rfid_configuration` tool for guided installation.

Options
^^^^^^^^^^^^^^

In principle Raspberry PIs support multiple SPI interfaces. The reader class is based on pi-rc522 which
uses spidev. This allows to use different SPI bus configurations. The below parameters regarding pin-out are
just routed through to spidev. Have a look at the spidev documentation for details if you really want to
use a different SPI bus. The default setup makes most sense for almost everyone.

spi_bus *(default=0)*
    The SPI Bus ID. The default bus is 0. For other bus IDs, the RPi also needs to re-configured. For that reason
    we set this to zero. |fileonly|

spi_ce *(default=0)*
    SPI chip enable pin. On default SPI bus 0, this can be

        * 0 = GPIO??
        * 1 = GPIO??

    For other SPI buses refer to RPi documentation.

pin_irq
    Mandatory IRQ pin. This can be any GPIO pin.

pin_rst *(default=0)*
    Reset pin for hardware reset. This is an optional pin.
    If not used,

        * hardware reset will only be performed by power-on-reset. This is not a problem.
        * you **must** tie the reset pin of the MFRC522 board **high**!

mode_legacy *(default=false)*
    4-byte-only legacy mode: previously the pirc522 library could only read the lower 4 bytes of a card UID.
    It can now read 4-byte and full 7-byte UIDs.
    Legacy mode turns back to the old behaviour. This only makes sense, if you already have an large RFID collection
    and do not want to re-assign every card

antenna_gain *(default=4)*
    Antenna gain factor of the RFID reader chip on the MFRC522 board. |fileonly|

log_all_cards *(default=false)*
    If true all card read-outs will be logged, even when card is permanently on reader.
    Only for debugging. |fileonly|


Board Connections
^^^^^^^^^^^^^^^^^^^^^^^^^^^^

The following pin-out is for the default SPI Bus 0 on Raspberry Pins

(spi_bus=0, spi_ce=0, pin_irq=24)

.. table:: MFRC522 default wiring (spi_bus=0, spi_ce=0)
    :widths: auto

    ===============   ========  =======
    Pin Board Name    Function  PI pin
    ===============   ========  =======
    SDA               CE        GPIO8
    SCK               SCLK      GPIO11
    MOSI              MOSI      GPIO10
    MISO              MISO      GPIO9
    IRQ               IRQ       GPIO24
    GND
    RST               RST       GPIO25
    3.3V
    ===============   ========  =======
