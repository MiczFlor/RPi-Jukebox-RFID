# Installing Phoniebox on RPi Stretch

*Written for an tested on Raspbian GNU/Linux 9.4 (stretch) Kernel version: 4.14*

The installation is the first step to get your jukebox up and running. Once you have done this, proceed to the [configuration](CONFIGURE-stretch.md).

And Once you finished with the configuration, read the [manual](MANUAL.md) to add audio files and RFID cards.

This project has been tested on Raspberry Pi model 1, 2, 3 HiFiBerry and Zero.

**Quick install script:** after you installed Raspbian and are online with your RPi, you might want to proceed to the [install script for Stretch](https://github.com/MiczFlor/RPi-Jukebox-RFID/blob/master/scripts/installscripts/stretch-install-default-01.sh). Having said this, if you are new to your Raspberry, you will learn more going through this step by step.

## Install Raspbian on your RPi

There are a number of operating systems to chose from on the [official RPi download page](https://www.raspberrypi.org/downloads/) on [www.raspberrypi.org](http://www.raspberrypi.org). We want to work with is the official distribution *Raspbian*. 

IMPORTANT: if you want to be sure that you have the same system running that this documentation was written for, you need to use the stretch distribution which you can download here: [2018-03-13-raspbian-stretch.zip](https://downloads.raspberrypi.org/raspbian/images/raspbian-2018-03-14/2018-03-13-raspbian-stretch.zip).

After you downloaded the `zip` file, follow the instructions on the official [INSTALLING OPERATING SYSTEM IMAGES](https://www.raspberrypi.org/documentation/installation/installing-images/README.md) page. I have used [etcher](https://etcher.io/) to make the SD card as described.

## Configure your RPi

Before you boot your RPi for the first time, make sure that you have all the external devices plugged in. What we need at this stage:

1. An external monitor connected over HDMI
2. A WiFi card over USB (unless you are using a RPi with an inbuilt WiFi card).
3. A keyboard and mouse over USB.

Now you have installed and operating system and even a windows manager (called Pixel on Raspbian). Start up your RPi and it will bring you straight to the home screen. Notice that you are not required to log in.

### Firmware update improves audio out?

If you want to update the RPI firmware, this is the right point to do so. This manual was written for the default firmware. Read more about how to update and why you might want to give it a try in a separate [Firmware Update document](FIRMWARE_UPDATE.md).

### Configure your keyboard

In the dropdown menu at the top of the home screen, select:

'Berry' > Preferences > Mouse and Keyboard Settings

Now select the tab *Keyboard* and then click *Keyboard Layout...* at the bottom right of the window. From the list, select your language layout.

### Configure the WiFi

At the top right of the home screen, in the top bar, you find an icon for *Wireless & Wired Network Settings*. Clicking on this icon will bring up a list of available WiFi networks. Select the one you want to connect with and set the password.

**Note**: Follow this link if you have [trouble with a USB Wifi card](https://www.raspberrypi.org/forums/viewtopic.php?t=44044).

**Disable WiFi power management**

Make sure the WiFi power management is disabled to avoid dropouts. Firstly, check if it is switched on, type in the terminal: 
~~~
iwconfig
~~~
This should return something like the following:
~~~
lo        no wireless extensions.

eth0      no wireless extensions.

wlan0     IEEE 802.11  ESSID:
          Mode:Managed  Frequency:2.437 GHz  Access Point: 34:31:C4:0A:8F:83   
          Bit Rate=72.2 Mb/s   Tx-Power=31 dBm
          Retry short limit:7   RTS thr:off   Fragment thr:off
          Power Management:on
          Link Quality=63/70  Signal level=-47 dBm  
          Rx invalid nwid:0  Rx invalid crypt:0  Rx invalid frag:0
          Tx excessive retries:2  Invalid misc:0   Missed beacon:0
~~~
The line `Power Management:on` is important: out of the box, it seems to be switched on, so let's switch it off, type:
~~~
sudo iwconfig wlan0 power off
~~~
And then check again with `iwconfig` that the line now says: `Power Management:off`.

### Access over SSH

SSH will allow you to log into the RPi from any machine in the network. This is useful because once the jukebox is up and running, it won't have a keyboard, mouse or monitor attached to it. Via SSH you can still configure the system and make changes - if you must.

Open a terminal to star the RPi configuration tool.

~~~~
sudo raspi-config
~~~~
Select `Interface Options` and then `SSH Enable/Disable remote command line...` to enable the remote access.

You should also change your password at this stage in `raspi-config`. The default password after a fresh install is `raspberry`. 

Find out more about how to [connect over SSH from Windows, Mac, Linux or Android on the official RPi page](https://www.raspberrypi.org/documentation/remote-access/ssh/).

### Autologin after boot

When you start the jukebox, it needs to fire up without stalling at the login screen. This can also be configured using the RPi config tool.

Open a terminal to star the RPi configuration tool.

~~~~
$ sudo raspi-config
~~~~

Select `Boot options` and then `Desktop / CLI`. The option you want to pick is `Console Autologin - Text console, automatically logged in as 'pi' user`.

### Set a static IP address for your RPi

To be able to log into your RPi over SSH from any machine in the network, you need to give your machine a static IP address.

Check if the DHCP client daemon (DHCPCD) is active.
~~~~
sudo service dhcpcd status
~~~~
If you don't get any status, you should start the `dhcpcd` daemon:
~~~~
sudo service dhcpcd start
sudo systemctl enable dhcpcd
~~~~
Check the IP address the RPi is running on at the moment:
~~~~
$ ifconfig

wlan0     Link encap:Ethernet  HWaddr 74:da:38:28:72:72  
          inet addr:192.168.178.82  Bcast:192.168.178.255  Mask:255.255.255.0
          ...
~~~~
You can see that the IP address is 192.168.178.82. We want to assign a static address 192.168.178.199.

**Note:** assigning a static address can create conflict with other devices on the same network which might get the same address assigned. Therefore, if you can, check your router configuration and see if you can assign a range of IP addresses for static use.

Change the IPv4 configuration inside the file `/etc/dhcpcd.conf`.
~~~~
sudo nano /etc/dhcpcd.conf
~~~~
Don't be surprised, if the file is empty. Then only add the lines below. In my case, I added the following lines to assign the static IP. You need to adjust this to your network needs:

~~~~
interface wlan0
static ip_address=192.168.178.201/24
static routers=192.168.178.1
static domain_name_servers=192.168.178.1
~~~~
Save the changes with `Ctrl & O` then `Enter` then `Ctrl & X`.

## Install required packages and the Phoniebox code

The following lines will install all the required packages:

~~~
sudo apt-get update
sudo apt-get install apt-transport-https samba samba-common-bin python-dev python-pip gcc linux-headers-4.9 lighttpd php7.0-common php7.0-cgi php7.0 php7.0-fpm vlc mpg123 git
sudo pip install "evdev == 0.7.0"
~~~

### Using git to pull the code from github

[*git* is a version control system](https://git-scm.com/) which makes it easy to pull software from GitHub - which is where the jukebox software is located.

~~~~
cd /home/pi/
git clone https://github.com/MiczFlor/RPi-Jukebox-RFID.git
~~~~

Now you have the code repo of the Phoniebox in the directory `/home/pi/RPi-Jukebox-RFID`.

## Configure your system

### Samba: Share files and folder over your home network 

To make the jukebox easy to administer, it is important that you can add new songs and register new RFID cards over your home network. This can be done from any machine. The way to integrate your RPi into your home network is using *Samba*, the standard [Windows interoperability suite for Linux and Unix](https://www.samba.org/).

Open a terminal and install the required packages with this line:

First, let's edit the *Samba* configuration file and define the workgroup the RPi should be part of.

~~~~
sudo nano /etc/samba/smb.conf
~~~~

Edit the entries for workgroup and wins support:

~~~~
workgroup = WORKGROUP
wins support = yes
~~~~

If you are already running a windows home network, add the name of the network where I have added `WORKGROUP`. 

Now add the specific folder that we want to be exposed to the home network in the `smb.conf` file. 

~~~~
[pi_jukebox]
   comment= Pi Jukebox
   path=/home/pi/RPi-Jukebox-RFID/shared
   browseable=Yes
   writeable=Yes
   only guest=no
   create mask=0777
   directory mask=0777
   public=no
~~~~

**Note:** the `path` given in this example works (only) if you are installing the jukebox code in the directory `/home/pi/`.

Finally, add the user `pi` to *Samba*. For simplicity and against better knowledge regarding security, I suggest to stick to the default user and password:

~~~~
user     : pi
password : raspberry
~~~~

Type the following to add the new user:

~~~~
sudo smbpasswd -a pi
~~~~

### evdev: expose common interfaces

Python-evdev exposes most of the more common interfaces defined in the evdev subsystem.  In other words: in order to read the IDs from the RFID cards, we need to dig deep into the operating system. We need to have an ear at the source of the RFID reader, so to speak. And in order to listen to these events using the programming language *python*, we need to install the package *evdev*.

The above installation commands should have installed everything just fine. In case you run into problems, read the [official devdev ocumentation](http://python-evdev.readthedocs.io/en/latest/install.html)

Having said this, the official way did not work for me on the RPI and I did the followng:

Find out the linux kernel release you are running:

~~~~
uname -r
~~~~

In my case it returned `4.14.30-v7+`. Now I took a look at the header files available:
~~~~
apt-cache search linux-headers-
~~~~

The highest version number that came up in the list was `linux-headers-4.9`:
~~~
(...)
linux-headers-4.9.0-6-all - All header files for Linux 4.9 (meta-package)
linux-headers-4.9.0-6-all-armhf - All header files for Linux 4.9 (meta-package)
linux-headers-4.9.0-6-common - Common header files for Linux 4.9.0-6
linux-headers-4.9.0-6-common-rt - Common header files for Linux 4.9.0-6-rt
linux-headers-4.9.0-6-rpi - Header files for Linux 4.9.0-6-rpi
linux-headers-4.9.0-6-rpi2 - Header files for Linux 4.9.0-6-rpi2
(...)
~~~

Which I added in the long install line above: `sudo apt-get install linux-headers-4.9`.


### Running the web app

There is a second way to control the RFID jukebox: through the browser. You can open a browser on your phone or computer and type in the static IP address that we assigned to the RPi earlier. As long as your phone or PC are connected to the same WiFi network that the RPi is connected to, you will see the web app in your browser.

### lighttpd: web server for web app

On Raspbian OS Stretch, some configuration still seems to be based on PHP5. We are using PHP7 and therefore need to make some changes to the configuration.

Open the configuration file:

~~~~
sudo nano /etc/lighttpd/lighttpd.conf
~~~~

Change the document root, meaning the folder where the webserver will look for things to display or do when somebody types in the static IP address. To point it to the Jukebox web app, change the line in the configuration to:

~~~~
server.document-root = "/home/pi/RPi-Jukebox-RFID/htdocs"
~~~~
Save the changes with `Ctrl & O` then `Enter` then `Ctrl & X`.

The webserver is usually not very powerful when it comes to access to the system it is running on. From a security point of view, this is a very good concept: you don't want a website to potentially change parts of the operating system which should be locked away from any public access.

We do need to give the webserver more access in order to run a web app that can start and stop processes on the RPi. To make this happen, we need to add the webserver to the list of users/groups allowed to run commands as superuser. To do so, open the list of sudo users in the nano editor:

~~~~
sudo nano /etc/sudoers
~~~~

And at the bottom of the file, add the following line:

~~~~
www-data ALL=(ALL) NOPASSWD: ALL
~~~~
Save the changes with `Ctrl & O` then `Enter` then `Ctrl & X`.

The final step to make the RPi web app ready is to tell the webserver how to execute PHP. To enable the lighttpd server to execute php scripts, the fastcgi-php module must be enabled. Type:
~~~
sudo lighttpd-enable-mod fastcgi
sudo lighttpd-enable-mod fastcgi-php
~~~

The configuration might still be set to use PHP5, we want PHP7. Open the config file:

~~~~
sudo nano /etc/lighttpd/conf-available/15-fastcgi-php.conf
~~~~

Edit the content to look like this:
~~~~
# -*- depends: fastcgi -*-
# /usr/share/doc/lighttpd/fastcgi.txt.gz
# http://redmine.lighttpd.net/projects/lighttpd/wiki/Docs:ConfigurationOptions#mod_fastcgi-fastcgi

## Start an FastCGI server for php (needs the php5-cgi package)
fastcgi.server += ( ".php" =>
        ((
                "socket" => "/var/run/php/php7.0-fpm.sock",
                "broken-scriptfilename" => "enable"
        ))
)
~~~~
Save the changes with `Ctrl & O` then `Enter` then `Ctrl & X`.

Now load the new configs into the web server by typing:
~~~
sudo service lighttpd force-reload
~~~

### Make a copy of the web app config file

There is a sample config file in the `htdocs` folder which you need to copy to `config.php`.
This assures that you can make changes to `config.php` which will not be affected by updates
in the upstream repository.

~~~~
sudo cp /home/pi/RPi-Jukebox-RFID/htdocs/config.php.sample /home/pi/RPi-Jukebox-RFID/htdocs/config.php
~~~~

Make sure the `shared` and `htdocs` folders are accessible by the web server:

~~~~
sudo chown -R pi:www-data /home/pi/RPi-Jukebox-RFID/shared
sudo chmod -R 775 /home/pi/RPi-Jukebox-RFID/shared
sudo chown -R pi:www-data /home/pi/RPi-Jukebox-RFID/htdocs
sudo chmod -R 775 /home/pi/RPi-Jukebox-RFID/htdocs
~~~~

Next on the list is the media player which will play the audio files and playlists: VLC. In the coming section you will also learn more about why we gave the web server more power over the system by adding it to the list of `sudo` users.

### VLC: the media player

The VLC media player not only plays almost everything (local files, web streams, playlists, folders), it also comes with a command line interface `CLVC` which we will be using to play media on the jukebox.

The next step is a severe hack. Quite a radical tweak: we will change the source code of the VLC binary file. We need to do this so that we can control the jukebox also over the web app. VLC was designed not to be run with the power of a superuser. In order to trigger VLC from the webserver, this is exactly what we are doing.

Changing the binary code is only a one liner, replacing `geteuid` with `getppid`. If you are interested in the details what this does, you can [read more about the VLC hack here](https://www.blackmoreops.com/2015/11/02/fixing-vlc-is-not-supposed-to-be-run-as-root-sorry-error/).

~~~~
$ sudo sed -i 's/geteuid/getppid/' /usr/bin/vlc
~~~~

**Note:** changing the binary of VLC to allow the program to be run by the webserver as a superuser is another little step in a long string of potential security problems. In short: the jukebox is a perfectly fine project to run for your personal pleasure. It's not fit to run on a public server.

## Using a USB soundcard

In order to use an external USB soundcard instead of the inbuilt audio out, you might need to update your system and tweak a couple of config files, depending on your card. The most comprehensive explanation on why and how, you can find at [adafruit](https://learn.adafruit.com/usb-audio-cards-with-a-raspberry-pi/instructions). 

Using the Jessie distribution, you might be lucky and there is a quick fix setting the [~/.asoundrc](https://raspberrypi.stackexchange.com/questions/39928/unable-to-set-default-input-and-output-audio-device-on-raspberry-jessie) file.

## Reboot your Raspberry Pi

Ok, after all of this, it's about time to reboot your jukebox. Make sure you have the static IP address at hand to login over SSH after the reboot.

~~~~
sudo reboot
~~~~

# Configure the jukebox

Continue with the configuration in the file [`CONFIGURE-stretch.md`](CONFIGURE-stretch.md).


