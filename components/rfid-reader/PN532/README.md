# How to setup the PN532 RFID reader

These instructions are for the following RFID reader:

<https://shop.pimoroni.com/products/adafruit-pn532-nfc-rfid-controller-shield-for-arduino-extras>

Similar shields/breakout boards, based on the same chip might work, but have not been tested.  

It has been tested with the I2C interface. Using SPI might work as well, but it has not been tested.


1. Connect the PN532 RFID reader to the GPIO pins

    | PN532 | Raspberry Pi | Raspi Pins |
    | ----- | ------------ | ---------- |
    | 5V    | 5V           |     4      |
    | GND   | GND          |     6      |
    | SDA   | GPIO 2 (SDA) |     3      |
    | SCL   | GPIO 3 (SCL) |     5      |

2. **You can use the `setup_pn532.sh` script (recommended)** or follow the manual steps:

3. Activate the I2C interface of the Raspberry Pi
    - `sudo raspi-config`
    - Select "5 Interfacing Options" -> I2C -> yes
    - or instead of using the UI, here is the CLI command:
        `sudo raspi-config nonint do_i2c 0`

4. Install I2C tools
    - `sudo apt-get install i2c-tools`

5. Check that the reader is found trough I2C
    - check `sudo i2cdetect -y 1`
    - output should look like this:


                 0  1  2  3  4  5  6  7  8  9  a  b  c  d  e  f
            00:          -- -- -- -- -- -- -- -- -- -- -- -- -- 
            10: -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- 
            20: -- -- -- -- 24 -- -- -- -- -- -- -- -- -- -- -- 
            30: -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- 
            40: -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- 
            50: -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- 
            60: -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- 
            70: -- -- -- -- -- -- -- -- 

    - if the table is empty, try switching I2C off and on again in raspi-config or reboot

6. Configure experimental reader
   - `cd scripts`
   - `cp Reader.py.experimental Reader.py`
   - Run `python3 RegisterDevice.py`
   - Select 2 (PN532)

7. Restart the phoniebox-rfid-reader service
   - `sudo systemctl restart phoniebox-rfid-reader.service`
