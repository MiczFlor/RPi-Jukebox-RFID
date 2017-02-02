# Identify and configure your RFID reader

The RFID reader is connected to your RPi via USB. As you plug it in, it should have made a 'beep'. And each time you swipe a keyring or card across the card reader, it should also make a 'beep'.

**Troubleshooting:** There is the odd chance that your reader is broken. How odd, I can not say. The first time I started playing around with this project on two different RPi machines (generation 1 and 2), when I ordered a second RFID reader it turned out to be broken. I doubt there is a 50/50 chance, I was just very unlucky. 

Let's see if your reader is probably connected and recognised by your RPi. Check the following:

1. The LED on the reader is on.
2. When swiping a card or keyring, you hear a 'beep' noise.

If you can answer both with yes, you can be 90% sure all is working well. Just to be 100% sure, here are a few command to type on the command line which should list your reader.

In Unix-like operating systems like your RPi is running, every connected device appears in the file system as if it were an ordinary file. Let's give it a try. To list all devices by ID, type:

~~~~
$ ls -la /dev/input/by-id/
~~~~

In my case, this will list the Barcode Reader and show that the system can interact with the device under `event0`:

~~~~
lrwxrwxrwx 1 root root   9 Feb  1 18:58 usb-13ba_Barcode_Reader-event-kbd -> ../event0
~~~~

If you want all the details about your USB device, you can use the command `sudo lsusb`, short for 'list USB devices'. Adding the option `-v` for 'be verbose', you will get a long and detailed list of all USB devices attached to your RPi. `lsusb` will now display detailed information about the devices shown. This includes configuration descriptors for the device's current speed. Class descriptors will be shown, when available, for USB device classes including hub, audio, HID, communications, and chipcard.

Scroll through the output to find the *Barcode Reader*. This long description can be helpful if you need specific information about available drivers or information on how to operate your device from the command line (none of this you will need to do now, this is for your RPi future - once you get into hacking your device).

In this case, for example, we learn that the product ID of the device is `PCP-BCG4209`. Below I am listing an excerpt from the complete list of information.

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

Now we know a lot about the RFID reader attached to our RPi. In order to use it as a controller for our jukebox, the software needs to know which device to listen to. Remember, this is why we started the above detective work in the first place: our software needs to *listen* to the device and whenever somebody swipes a card, it needs to read the card ID and then trigger an action - most likely playing some music.

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

When you switch on the RPi jukebox, you want it to boot up and be ready to play. Remember, once this RPi workshop is finished, there are neither monitor nor keyboard or mouse attached to your RPi. It's booting in the dark, so to speak.

Therefore we need to add one final tweak to the configuration: automatically start our jukebox software after the RPi has booted and have it listen to RFID cards.

Software with this kind of stealth behaviour is often called a *daemon*. It is a piece of [code running as a background process](https://en.wikipedia.org/wiki/Daemon_(computing)), without any control or interaction needed by the user.

To start our own jukebox daemon, we are taking advantage of another daemon which is installed on most Unix systems, like your RPi: *Cron*, a scheduler that runs programs (or jobs) at certain intervals. [The way in which recurring jobs are triggered by the cron daemon is rather nifty](https://en.wikipedia.org/wiki/Cron). We don't need to dive into the details, because we are using cron in a very basic way by telling it: "every time the computer has booted up, run the following script". 

In cron language, this translates to:

~~~~
@reboot python2 /home/pi/RPi-Jukebox-RFID/scripts/daemon_rfid_reader.py &
~~~~

Let's break this down:

1. `@reboot` : once the boot process is completed, do the following
2. `python2` : run a python script using the latest python version 2.x which is installed on the system.
3. `/home/pi/RPi-Jukebox-RFID/scripts/daemon_rfid_reader.py` : this is the absolute path to the script on your system.
4. `&` : start this process as a background process (this is not needed here, I added it to have the complete command. If you were to start the script on the command line manually, the `&` added at the end will push the process into the background and free the command line.)

Now that you know what this line will be doing, add it to the right place in your system. Every user on a Unix system has his/her own *crontab*, a table of jobs that are scheduled. To edit this cron table for the user pi on your RPi, simply type:

~~~~
$ crontab -e
~~~~

The first time you fire up this command, the system will ask you which editor to use. Because it is widely used and most of the time set as the default editor, I advice you to use [*nano*](https://www.nano-editor.org/).

Once you started `crontab`, add the above line (starting with `@reboot`) to the bottom of the document. 

Save and close the file by typing `Ctrl & X` then `y` then hit the `Enter` key.

Now, when you reboot, the jukebox will automatically start and wait for input in the background.

## Copy the media player script

Inside the directory `/home/pi/RPi-Jukebox-RFID/scripts/` you find the file `rfid_trigger_play.sh.sample`. You need to make a copy of this file, because you might edit this file at a later stage. If you don't make a copy there is a chance that the changes you make might be overwritten by the master on GitHub, if you update the code.

~~~~
$ cd /home/pi/RPi-Jukebox-RFID/scripts/
$ cp rfid_trigger_play.sh.sample rfid_trigger_play.sh
$ chmod +x rfid_trigger_play.sh
~~~~

# Jukebox manual

Now the installation and configuration are complete. Time to read the manual of the jukebox to add songs, web streams, register new cards and so on. Read the [`MANUAL.md`](MANUAL.md).