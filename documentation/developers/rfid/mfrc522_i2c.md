# MFRC522 I2C Reader

The MFRC522-based readers connected via I2C

This reader module is based on the [mfrc522_i2c
library](https://github.com/cpranzl/mfrc522_i2c) and uses the I2C bus.

## Options

There are no configurable options for this module.

## Hardware

This reader module has been tested with  [M5Stack RFID 2 Unit WS1850S module](https://docs.m5stack.com/en/unit/rfid2).

### Using an alternate board with a different i2c_address

The default address is `0x28`. To find out the I2C address of your reader, first install the `i2c-tools` package:

`sudo apt install i2c-tools`

Then query all I2C addresses using:

`i2cdetect -y 1`

The address you see in the output will be a hex value (e.g. the hex value `0x28` is the decimal value `40`).
Convert this to decimal, then add this to your `rfid.yaml` settings file.

## Board Connections

### Default wiring

| MFRC522 | RPI GPIO     | RPI Pin |
|---------|--------------|---------|
| 5V      | 5V           | > 4     |
| GND     | GND          | > 6     |
| SDA     | GPIO 2 (SDA) | > 3     |
| SCL     | GPIO 3 (SCL) | > 5     |
