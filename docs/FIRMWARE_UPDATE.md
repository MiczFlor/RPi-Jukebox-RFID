# Firmware update improves audio out?

**This has not been tested yet**: The analogue audio out quality of the RPi3 is horrible. Learn more about the [impact of the firmware update in the raspberry forum](https://www.raspberrypi.org/forums/viewtopic.php?f=29&t=167934). In the same forum you can find information on the [firmaware update effect on the analogue audio out](https://www.raspberrypi.org/forums/viewtopic.php?f=29&t=136445). If you were to try to update the firmware, now would be the right moment. I tried the firmware update successfully, but haven't yet built a Phoniebox on top of it. So if you are new to the RPi, skip the following lines and go to the next chapter, configuring your keyboard.

Open a terminal window and update the firmware typing:
~~~~
sudo rpi-update
~~~~
Then reboot the machine:
~~~~
sudo reboot
~~~~
Now open the terminal window again. The howto suggests to switch off the HDMI audio out:
~~~~
amixer cset numid=3 1
~~~~
Open the config file with:
~~~~
sudo nano /boot/config.txt
~~~~
and add the following line:
~~~~
audio_pwm_mode=2
~~~~
Better safe than sorry, reboot the machine once more:
~~~~
sudo reboot
~~~~
