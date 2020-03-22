# How to setup the PN532 RFID reader

These instructions are for the following RFID reader:

<https://shop.pimoroni.com/products/adafruit-pn532-nfc-rfid-controller-shield-for-arduino-extras>

Similar shields/breakout boards, based on the same chip might work, but have not been tested.  

It has been tested with the I2C interface. Using SPI might work as well, but it has not been tested.

The following steps should be done before installing RPi-Jukebox-RFID. If RPi-Jukebox-RFIS is already
installed, make sure to disable the phoniebox-rfid-reader service first (`sudo systemctl stop phoniebox-rfid-reader.service`).
   

1. Connect the PN532 RFID reader to the GPIO pins

    | PN532 | Raspberry |
    | ----- | --------- |
    | 5V    | 5V        |
    | GND   | GND       |
    | SDA   | SDA0      |
    | SCL   | SCL0      |

2.  Activate the I2C interface of the Raspberry Pi
    - `sudo raspi-config`
    - Select "5 Interfacing Options" -> I2C -> yes  

3. Install I2C tools and libnfc
    - `sudo apt-get install i2c-tools libnfc-bin`

4. Check that the reader is found trough I2C
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
    

5. Configure libnfc

    - `sudo nano /etc/nfc/libnfc.conf`
    - Add the following lines at the end of the file:

          device.name = "_PN532_I2c"
          device.connstring = "pn532_i2c:/dev/i2c-1"

6. Test libnfc config
   - Run `nfc-list`
   - Output should be:

          nfc-list uses libnfc 1.7.1
          NFC device: pn532_i2c:/dev/i2c-1 opened


7. Configure experimental reader
   - `cd scripts`
   - `cp Reader.py.experimental Reader.py`
   - Run `python3 RegisterDevice.py`
   - Select 2 (PN532)


If you disabled the service, start it again:
`sudo systemctl stop phoniebox-rfid-reader.service`
