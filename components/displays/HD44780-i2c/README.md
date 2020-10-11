
# LCD displays based on HD44780

*([Permission to use this code for the Phoniebox project](https://github.com/chbuehlmann/RPi-Jukebox-RFID/pull/859#discussion_r408667007) on April 15th 2020 by author [Denis Pleic](https://github.com/DenisFromHR). Original [code on https://gist.github.com/DenisFromHR/cc863375a6e19dce359d](https://gist.github.com/DenisFromHR/cc863375a6e19dce359d))*

The following files allow using LCD displays based on HD44780 connected via i2c bus for this project. The following displays have been used for testing:

- 2x16 display
- 4x20 display (recommended as more information can be displayed)

Various informations such as artist, album, track_number, track_title, track_time and many more can be displayed see main script for more display options.

The required files are:

- components/displays/HD44780-i2c/i2c_lcd.py
- components/displays/HD44780-i2c/i2c_lcd_driver.py
- components/displays/HD44780-i2c/i2c-lcd.service.default.sample
- components/displays/HD44780-i2c/README.md


The first file is the main LCD script that makes use of I2C_LCD_driver.py.

The second file is the library needed to drive the LCD via i2c, originates from DenisFromHR (Denis Pleic) see http://www.circuitbasics.com/raspberry-pi-i2c-lcd-set-up-and-programming

The third is used as sample service file that runs the i2c_lcd.py main script at boot-up if the service is properly installed (install description can be found below.).

The fourth file is this file which describes the features, usage and installation of the code.

### Installation

* You need to install additional python libraries. Run the following two command in the command line:

`sudo apt-get install i2c-tools python-smbus python3-numpy python-mpdclient python-mpd`

`pip install smbus numpy python-mpd2`

* You need to know which I2C bus your Raspberry Pi has available on GPIOs:

`ls /dev/i2c-*`

It'll output "/dev/i2c-x", where x is your bus number. Note this bus number as you will need it in step 6.
* Now detect the adapter by using the i2cdetect command, inserting your bus number:

`sudo i2cdetect -y bus_number`

The I2C address of my LCD is 27. Take note of this number, it will be need in step 6.

* if i2cdetect is not found install i2c-tools

`sudo apt-get update`

`sudo apt-get install i2c-tools`

* Next we need to install SMBUS, which gives the Python library we’re going to use access to the I2C bus on the Pi. At the command prompt, enter

`sudo apt-get install python-smbus`

* Modify "i2c_lcd_driver.py" line 19 which reads "I2CBUS = 1" and adapt it to your bus number (see step 2.) Furthermore modify line 22 which reads "ADDRESS = 0x27" and adapt it to your I2C address (see step 3.)
* Modify "i2c_lcd.py" to adapt it yo your specific display e.g. 2x16 or 4x20 (default). The lines 15-19 look like the following:

```
################# CHANGE YOUR SETTINGS HERE!!! ###########################################
## Display settings                                                                     ##
n_cols = 20                 # EDIT!!!  <-- number of cols your display has              ##
n_rows = 4                  # EDIT!!!  <-- number of rows your display has              ##
val_delay = 0.4             # EDIT!!!  <-- speed of the scolling text                   ##
```
Check if "n_cols" and "n_rows" need to be changed and modify them if necessary. The "val_delay" constant leave for the time being. Lower values will speed up things but will make the text less visible/readable.

* next install and start "i2c-lcd.service"

`sudo cp /home/pi/RPi-Jukebox-RFID/components/displays/HD44780-i2c/i2c-lcd.service.default.sample /etc/systemd/system/i2c-lcd.service`

* register service by running, it will thereby start on the next boot-up

`sudo systemctl enable i2c-lcd`

* Reboot and enjoy!

---

For test purposes you can use the following command to start and stop the service without rebooting
to start the service instantly run

`sudo systemctl start i2c-lcd`

to stop the service instantly run

`sudo systemctl stop i2c-lcd`

Best regards,
Simon
