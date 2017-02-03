# Configure your RPi and jukebox

This is the second step. Make sure to go through the [Installation](INSTALL-md) first.

## Identify and configure your RFID reader

The RFID reader is connected to your RPi via USB. As you plug it in, it should have made a 'beep'. And each time you swipe a keyring or card across the card reader, it should also make a 'beep'.

**Troubleshooting:** There is the odd chance that your reader is broken. How odd, I can not say. The first time I started playing around with this project on two different RPi machines (generation 1 and 2), when I ordered a second RFID reader it turned out to be broken. I doubt there is a 50/50 chance, I was just very unlucky. 

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

Once you started `crontab`, add the above line (starting with `@reboot`) to the bottom of the document. 

Save and close the file by typing `Ctrl & X` then `y` then hit the `Enter` key.

Now, when you reboot, the jukebox will automatically start and wait for input in the background.

## Copy the media player script

Inside the directory `/home/pi/RPi-Jukebox-RFID/scripts/` you find the file `rfid_trigger_play.sh.sample`. You need to make a copy of this file, because you might edit this file at a later stage.

~~~~
$ cd /home/pi/RPi-Jukebox-RFID/scripts/
$ cp rfid_trigger_play.sh.sample rfid_trigger_play.sh
$ chmod +x rfid_trigger_play.sh
~~~~

# Jukebox manual

Now the installation and configuration are complete. Time to read the manual of the jukebox to add songs, web streams, register new cards and so on. Read the [`MANUAL.md`](MANUAL.md).