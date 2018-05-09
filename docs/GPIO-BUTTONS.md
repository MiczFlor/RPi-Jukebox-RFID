
# Control Jukebox with buttons / GPIO

(Other docs: [Installation](INSTALL-stretch.md) |
[Configuration](CONFIGURE-stretch.md) |
[Jukebox manual](MANUAL.md))

**Add buttons to your jukebox to control volume, skip tracks and more.**

Before we start:
One of the plus points about this projects, at least in my mind, 
was the fact that you don't need a soldering iron to build it.
Everything is USB, plug and play, thank you, boot and go.

Many, many fellow jukebox tweakers have contacted me to push
the envelope a bit further and add buttons to the jukebox.
Buttons to change the volume and skip between tracks in a playlist.

Right now (12th Dec 2017) I still have to get my soldering iron
out of the shelf and try this myself. Until then, what I have done here
is compiling and editing howto mails and docs I got sent.
I would love to hear feedback and get pull requests to improve 
this documentation. So if you are successful, give back to the project
by sharing your knowledge.

Enough said, here we go.

---

## Pin numbering on the RPi

On your RPi there are pin numbers printed on the board. In the following we are not referring to the board numbers, but the Broadcom (BCM) pin numbering for the GPIO pins. You can find more information on this issue on the [pin numbering](https://gpiozero.readthedocs.io/en/stable/recipes.html#pin-numbering) section of the GPIO Zero documentation site.

![Any pin marked “GPIO” in the diagram below can be used as a pin number. For example, if an LED was attached to “GPIO17” you would specify the pin number as 17 rather than 11.](img/GPIO-pin-numbering.png
 "Any pin marked “GPIO” in the diagram below can be used as a pin number. For example, if an LED was attached to “GPIO17” you would specify the pin number as 17 rather than 11.")

Any pin marked “GPIO” in the diagram above can be used as a pin number. A button attached to “GPIO17” would be specified in the script as pin number 17 rather than 11 (which would be the count on the board).

## Fire up the soldering iron

Ok, you asked for it, roll up your sleeves and read these before you start:

* [Getting started with soldering on raspberrypi.org](https://www.raspberrypi.org/blog/getting-started-soldering/)
* [Switch and buttons basics on sparkfun.com](https://learn.sparkfun.com/tutorials/switch-basics)

You will be running wires from the RPi board to another board where the buttons will be connected. The following image is what this looks like in a successful project.

![The extra board to connect the RPi with the buttons using resistors on the extra board.](img/buttons-board.jpg
 "The extra board to connect the RPi with the buttons using resistors on the extra board.")

On the above image you can also see the pin numbering, in this case containing both: the RPi board numbering on the RPi3 and the Broadcom (BCM) pin numbering used for the code.

The script for the GPIO buttons we are using have been provided by Andreas aka [hailogugo](https://github.com/hailogugo). He also sent the picture above and has a working version of the GPIO button solution. Pin numbers and functionality in this example connect as such:

| Board | GPIO (BCM) | Function |
| --- | --- | --- |
| 15 | 22 | Volume up |
| 16 | 23 | Volume down |
| 11 | 17 | Next track |
| 13 | 27 | Previous track |
| 37 | 26 | Play/Pause |

### Circuit example(s) for the button wiring

You will be using push buttons, which are essentially the same as arcade buttons, meaning: when you press them down, they are ON, when you let go, the are OFF. So skipping a track is tapping a button once, changing the volume, each tap changes it a bit.

There are a number of different ways to connect a button. The easiest one is well explained on O'Reilly's RPi site:

* [Connecting a Push Switch, O'Reilly](http://razzpisampler.oreilly.com/ch07.html)
* Watch the [Connecting a Push Switch with Raspberry Pi video on YouTube](https://youtu.be/3TDJ4FmtGgk)

## Install GPIO software

We need to run [GPIO Zero](https://gpiozero.readthedocs.io/en/stable/), a simple interface to GPIO devices with Raspberry Pi. GPIO Zero is installed by default in Raspbian Jessie. To install see the [installing](https://gpiozero.readthedocs.io/en/stable/installing.html) chapter on their site. Better safe than sorry, so lets install the packages on our machine:

~~~
$ sudo apt-get install python3-gpiozero python-gpiozero
~~~

**Note**: No harm done to install both, python3 and python2. This needs trimming later on.

Make a copy of the [python script for the GPIO buttons](../misc/GPIO-button-sample.py) into the scripts folder. This way you are free to make changes to the script without changing your github repo.

~~~
$ cp /home/pi/RPi-Jukebox-RFID/misc/GPIO-button-sample.py /home/pi/RPi-Jukebox-RFID/scripts/gpio-buttons.py
~~~

And change the copy to be executable

~~~
$ sudo chmod +x /home/pi/RPi-Jukebox-RFID/scripts/gpio-buttons.py
~~~

**Note**: work in progress: the [python script for the GPIO buttons](../misc/GPIO-button-sample.py) will be explained when I get to it.

To have this started automatically at boot. Please read the section on [autostarting the scripts](CONFIGURE-stretch.md#systemdautostart) in the configuration documentation [CONFIGURE-stretch.md](CONFIGURE-stretch.md#systemdautostart).