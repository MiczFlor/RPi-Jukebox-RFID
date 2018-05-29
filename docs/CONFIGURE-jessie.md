# Configure your Phoniebox on RPi Jessie

*Written for an tested on Raspbian GNU/Linux (jessie)*

This is the second step. Make sure to go through the [installation](INSTALL-jessie.md) first.

Once you finished with the configuration, read the [manual](MANUAL.md) to add audio files and RFID cards.

## Identify and configure your RFID reader

The RFID reader is connected to your RPi via USB. As you plug it in, it should have made a 'beep'. And each time you swipe a keyring or card across the card reader, it should also make a 'beep'.

**Troubleshooting:** When you buy the RFID reader and the chips, make sure that they match. There are different standards. It happened to me that the reader made the *beep* as if it reads the card - but it didn't.

Let's see if your reader is probably connected and recognised by your RPi. Check the following:

1. The LED on the reader is on.
2. When swiping a card or keyring, you hear a 'beep' noise.

If you can answer both with yes, you can be 90% sure all is working well. Just to be 100% sure, here are a few command to type on the command line which should list your reader.

~~~~
$ ls -la /dev/input/by-id/
~~~~

In my case, this will list the Barcode Reader and show that the system can interact with the device under `event0`:

~~~~
lrwxrwxrwx 1 root root   9 Feb  1 18:58 usb-13ba_Barcode_Reader-event-kbd -> ../event0
~~~~

If you want all the details about your USB device, you can use the command `sudo lsusb`, short for 'list USB devices'. Scroll through the output to find the *Barcode Reader*. This long description can be helpful if you need specific information about available drivers. In my case, for example, we learn that the product ID of the device is `PCP-BCG4209`. Below I am listing an excerpt from the complete list of information.

~~~~
$ sudo lsusb -v

Bus 001 Device 004: ID 13ba:0018 PCPlay Barcode PCP-BCG4209
Device Descriptor:
...
  idVendor           0x13ba PCPlay
  idProduct          0x0018 Barcode PCP-BCG4209
  bcdDevice          0.01
  iManufacturer      0
  iProduct           1 Barcode Reader
...
  MaxPower           400mA
...
  bInterfaceClass    3 Human Interface Device
...
  bInterfaceProtocol 1 Keyboard
...
  Device Status:     0x0000
  (Bus Powered)
~~~~

What we learn from this detailed list:

1. The device is a 'Human Interface Device' and acts like a 'Keyboard', which is exactly how the RFID reader operates: it registers as a USB keyboard and when you swipe a card, it will 'print' the card ID, followed by a return key, as if you typed it into the keyboard.
2. It can use up to 400mA in power consumption. (This information is not trivial. In one forum I found a post where the user could only run this USB device by using a USB hub with a special power supply. The RPi did not provide enough power over the USB.)
3. The vendor is called *PCPlay*.
4. The product is called *Barcode Reader*.

## Register your USB device for the jukebox

Now we know a lot about the RFID reader attached to our RPi. In order to use it as a controller for our jukebox, the software needs to know which device to listen to.

To register your device, go to the directory containing all the scripts and run the file `RegisterDevice.py`.

~~~~
$ cd /home/pi/RPi-Jukebox-RFID/scripts/
$ python2 RegisterDevice.py
Choose the reader from list
0 Barcode Reader 
~~~~

This will bring up a list of one or more devices. Spot the device you are using as a RFID reader, type the number (in this case *0*) and hit *Enter*.

You can check if your device was registered properly by taking a look inside the file that was just generated, called `deviceName.txt`.

~~~~
$ cat deviceName.txt
Barcode Reader
~~~~

Now your jukebox knows which device to listen to when you are swiping your cards or keyrings.

## Auto-start the jukebox

Note: If you use a recent Raspbian installation you system will most likely
use systemd for the system start. If it does it is preferrable to use
systemd to start the components since systemd will also take care of
restarting the script in case they die. See below for the procedure to do
so.

This is the final tweak to the configuration: automatically start our jukebox software after the RPi has booted and have it listen to RFID cards.

To start the jukebox daemon, we are taking advantage of another daemon which is installed on most Unix systems: *Cron*. We are using cron in a very basic way by telling it: "every time the computer has booted up, run the following script". 

In cron language, this translates to:

~~~~
@reboot python2 /home/pi/RPi-Jukebox-RFID/scripts/daemon_rfid_reader.py &
~~~~

Add this line to your *crontab*, a table of scheduled jobs. To edit this cron table for the user pi on your RPi, type:

~~~~
$ crontab -e
~~~~

The first time you fire up this command, the system will ask you which editor to use.

Once you started `crontab`, add the two lines at the bottom of the document:

```
@reboot mpg123 /home/pi/RPi-Jukebox-RFID/misc/startupsound.mp3
@reboot python2 /home/pi/RPi-Jukebox-RFID/scripts/daemon_rfid_reader.py &
```

**Note:** The first line plays a startup sound, using the command line player mpg123. The sound used here is being shipped with Ubuntu and can be found at `/usr/share/sounds/ubuntu/notifications/Mallet.ogg`.

Save and close the file by typing `Ctrl & X` then `y` then hit the `Enter` key.

Now, when you reboot, the jukebox will automatically start and wait for input in the background.

## Auto-start the jukebox by systemd 

If you chose to use the `crontab` option to launch the card reader daemon scripts, you can ignore this part.
If you want to use the `systemd` way, first copy the service config files to the correct directory:

```
sudo cp /home/pi/RPi-Jukebox-RFID/misc/*.service /etc/systemd/system/
```

If you installed your jukebox to /home/pi/Rpi-jukebox-RFID you can leave the
files as they are, otherwise you need to change the path in the *.service
text files.

Now systemd has to be notified that there are new service files:

```
sudo systemctl daemon-reload
```

The last step is to enable the service files:

```
sudo systemctl enable rfid-reader
sudo systemctl enable startup-sound
sudo systemctl enable gpio-buttons (optional)
```

The newly installed service can be started either by rebooting the jukebox or
with ```sudo systemctl start rfid-reader```.

To see if the reader process is running use the command ```sudo systemctl
status rfid-reader``` to produce an output like this:

```
pi@Jukebox:~ $ systemctl status rfid-reader
● rfid-reader.service - RFID-Reader Service
   Loaded: loaded (/etc/systemd/system/rfid-reader.service; enabled; vendor pres
   Active: active (running) since Fri 2018-04-13 07:34:53 UTC; 5h 47min ago
 Main PID: 393 (python2)
   CGroup: /system.slice/rfid-reader.service
           └─393 /usr/bin/python2 /home/pi/RPi-Jukebox-RFID/scripts/daemon_rfid_

Apr 13 07:34:53 Jukebox systemd[1]: Started RFID-Reader Service.
```
  

## Copy the media player and daemon script

Inside the directory `/home/pi/RPi-Jukebox-RFID/scripts/` you find the file `rfid_trigger_play.sh.sample` . You need to make a copy of these files, because you might edit these files at a later stage.

~~~~
cd /home/pi/RPi-Jukebox-RFID/scripts/
cp rfid_trigger_play.sh.sample rfid_trigger_play.sh
chmod +x rfid_trigger_play.sh
chmod +x playout_controls.sh
~~~~

## Link playout_controls to the scipt directory

Inside the `/home/pi/RPi-Jukebox-RFID/scipts/` you find the files `VLC_playout_controls.sh`, `MPG123_playout_controls.sh`, `MPV_playout_controls.sh` and `rfid_trigger_play.conf`
Choose the one for the Player you like and create the link to the script directory.

~~~~~
ln -s /home/pi/RPi-Jukebox-RFID/settings/MPG123_playout_controls.sh /home/pi/RPi-Jukebox-RFID/scripts/playout_controls.sh
~~~~~

# Connecting the hardware

Once the software is all in place, make sure the hardware is connected correctly.

1. Connect a USB hub with the power supply. From this hub, connect the RPi to one plug and the USB powered speakers to another. Do not connect the speakers to the USB of the RPi, because the power coming from the RPi might not be enough to run the speakers.
2. You need a number of USB plugs to connect the following and therefore possibly need a second USB hub to connect to the RPi USB:
    * RFID card reader
    * WiFi dongle (WLAN adapter for RPi < version 3)
    * External soundcard (optional)
3. Connect the speakers with the 3.5mm jack to the soundcard (either the built in one from the RPi or the external one attached to the RPi over USB).

# Push buttons (GPIO) for volume control and the like

Adding control buttons for volume, skipping tracks, pause, play, read the [GPIO buttons installation guide](GPIO-BUTTONS.md).

# Jukebox manual

Now the installation and configuration are complete. Time to read the manual of the jukebox to add songs, web streams, register new cards and so on. Read the [`MANUAL.md`](MANUAL.md).
