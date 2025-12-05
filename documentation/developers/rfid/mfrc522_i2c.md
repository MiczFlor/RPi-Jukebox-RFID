# MFRC522 I2C Reader

The MFRC522-based readers connected via I2C

This reader module is based on the [mfrc522_i2c
library](https://github.com/cpranzl/mfrc522_i2c) and uses the I2C bus.

## Options

There are no configurable options for this module.

## Hardware

This reader module has been tested with  [M5Stack RFID 2 Unit WS1850S module](https://docs.m5stack.com/en/unit/rfid2).

## Board Connections

### Default wiring

| MFRC522 | RPI GPIO     | RPI Pin |
|---------|--------------|---------|
| 5V      | 5V           | > 4     |
| GND     | GND          | > 6     |
| SDA     | GPIO 2 (SDA) | > 3     |
| SCL     | GPIO 3 (SCL) | > 5     |
