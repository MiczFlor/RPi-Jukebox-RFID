# <a name="install"></a>Installing Phoniebox on RPi Stretch

*Written for an tested on Raspbian GNU/Linux 9.4 (stretch) Kernel version: 4.14*

The installation is the first step to get your Phoniebox up and running. Once you have done this, proceed to the [configuration](CONFIGURE-stretch.md).

And Once you finished with the configuration, read the [manual](MANUAL.md) to add audio files and RFID cards.

This project has been tested on Raspberry Pi model 1, 2, 3 HiFiBerry and Zero.

## <a name="oneLineInstall"></a>One line install command

For the impatient: there is a one line script. If you have your

* Raspberry Pi up and running on stretch and 
* are connected to the Internet

open the terminal and paste the following line:

~~~
cd; rm stretch-install-default*; wget https://raw.githubusercontent.com/MiczFlor/RPi-Jukebox-RFID/master/scripts/installscripts/stretch-install-default.sh; chmod +x stretch-install-default.sh; ./stretch-install-default.sh
~~~

Having said this, you might learn a bit more about your Raspberry Pi to walk through the installation process step by step, like this:

The one line install command contains five separate commands linked up by replacing the *end of line* with `;`. The commands do the following:

* `cd` - move to the home directory
* `rm stretch-install-default-02*` - remove previously downloaded versions of the install script
* `wget https://raw.githubusercont...` - download the actual install script from github
* `chmod +x stretch-install-default-02.sh` - make the script executable
* `./stretch-install-default-02.sh` - run the script

## Install Raspbian on your RPi

There are a number of operating systems to chose from on the [official RPi download page](https://www.raspberrypi.org/downloads/) on [www.raspberrypi.org](http://www.raspberrypi.org). We want to work with is the official distribution *Raspbian*. 

Install and configure via SSH: if you need to install and configure the Phoniebox via SSH, you might want to jump to the [headless installation](#ssh-install) towards the end of this document.

IMPORTANT: if you want to be sure that you have the same system running that this documentation was written for, you need to use the stretch distribution which you can download here: [2018-03-13-raspbian-stretch.zip](https://downloads.raspberrypi.org/raspbian/images/raspbian-2018-03-14/2018-03-13-raspbian-stretch.zip).

After you downloaded the `zip` file, follow the instructions on the official [INSTALLING OPERATING SYSTEM IMAGES](https://www.raspberrypi.org/documentation/installation/installing-images/README.md) page. I have used [etcher](https://etcher.io/) to make the SD card as described.

Plug the SD into your Pi, connect keyboard, monitor and mouse. And fire it up.

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

SSH will allow you to log into the RPi from any machine in the network. This is useful because once the Phoniebox is up and running, it won't have a keyboard, mouse or monitor attached to it. Via SSH you can still configure the system and make changes - if you must.

Open a terminal to star the RPi configuration tool.

~~~~
sudo raspi-config
~~~~
Select `Interface Options` and then `SSH Enable/Disable remote command line...` to enable the remote access.

You should also change your password at this stage in `raspi-config`. The default password after a fresh install is `raspberry`. 

Find out more about how to [connect over SSH from Windows, Mac, Linux or Android on the official RPi page](https://www.raspberrypi.org/documentation/remote-access/ssh/).

### Autologin after boot

When you start the Phoniebox, it needs to fire up without stalling at the login screen. This can also be configured using the RPi config tool.

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
sudo apt-get install apt-transport-https samba samba-common-bin python-dev python-pip gcc linux-headers-4.9 lighttpd php7.0-common php7.0-cgi php7.0 php7.0-fpm at mpd mpc mpg123 git ffmpeg python-mutagen
~~~

### Using git to pull the code from github

[*git* is a version control system](https://git-scm.com/) which makes it easy to pull software from GitHub - which is where the Phoniebox software is located.

~~~~
cd /home/pi/
git clone https://github.com/MiczFlor/RPi-Jukebox-RFID.git
~~~~

### Install python requirements

~~~~
cd /home/pi/RPi-Jukebox-RFID/
pip install -r requirements.txt
~~~~


Now you have the code repo of the Phoniebox in the directory `/home/pi/RPi-Jukebox-RFID`.

## Configure your system

### Samba: Share files and folder over your home network 

To make the Phoniebox easy to administer, it is important that you can add new songs and register new RFID cards over your home network. This can be done from any machine. The way to integrate your RPi into your home network is using *Samba*, the standard [Windows interoperability suite for Linux and Unix](https://www.samba.org/).

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
[phoniebox]
   comment=Pi Jukebox
   path=/home/pi/RPi-Jukebox-RFID/shared
   browseable=Yes
   writeable=Yes
   only guest=no
   create mask=0777
   directory mask=0777
   public=no
   veto files=/._*/.DS_Store/
~~~~

**Note:** the `path` given in this example works (only) if you are installing the Phoniebox code in the directory `/home/pi/`.

If the audio files are not inside the `shared` folder, you might want to add another section to the config file. Otherwise you can not manage audio files over the samba / windows network. This might look like this - changing the path to your needs:

~~~~
[phoniebox_audio]
   comment=Pi Jukebox
   path=/path/to/audiofolders
   browseable=Yes
   writeable=Yes
   only guest=no
   create mask=0777
   directory mask=0777
   public=no
   veto files=/._*/.DS_Store/
~~~~

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

There is a second way to control the RFID Phoniebox: through the browser. You can open a browser on your phone or computer and type in the static IP address that we assigned to the RPi earlier. As long as your phone or PC are connected to the same WiFi network that the RPi is connected to, you will see the web app in your browser.

### lighttpd: web server for web app

On Raspbian OS Stretch, some configuration still seems to be based on PHP5. We are using PHP7 and therefore need to make some changes to the configuration.

Open the configuration file:

~~~~
sudo nano /etc/lighttpd/lighttpd.conf
~~~~

Change the document root, meaning the folder where the webserver will look for things to display or do when somebody types in the static IP address. To point it to the Phoniebox web app, change the line in the configuration to:

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

### File upload via web app: changes in php.ini

The Phoniebox web app allows to upload files through the web app. To do so, php needs to understand that it is allowed to ignore files sizes and maximum size per file and the like. Such restrictions are set in the file `/etc/php/7.0/fpm/php.ini`. What you need to change (or use the sample script in the following step) are these variables - they need to be changed to read like the following:

~~~
file_uploads = On
upload_max_filesize = 0
max_file_uploads = 20
post_max_size = 0
~~~

Copy the `php.ini` file to the right place and change the user and access rights:

~~~
sudo cp /home/pi/RPi-Jukebox-RFID/misc/sampleconfigs/php.ini.stretch-default.sample /etc/php/7.0/fpm/php.ini
sudo chown root:root /etc/php/7.0/fpm/php.ini
sudo chmod 644 /etc/php/7.0/fpm/php.ini
~~~

If you don't want to reboot your Phoniebox, you need to restart `php7.0-fpm` to load the new `php.ini` file.

~~~
sudo service php7.0-fpm restart
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

## Install MPD, the music player daemon

[Music Player Daemon](https://www.musicpd.org/) (MPD) is a flexible, powerful, server-side application for playing music. Through plugins and libraries it can play a variety of sound files while being controlled by its network protocol. While MPD is running in the background, MPC acts like a player 'on top'. 

You need to change the configuration file.
~~~
sudo nano /etc/mpd.conf
~~~

Find these options and change to the following:

* `music_directory "/home/pi/RPi-Jukebox-RFID/shared/audiofolders"`
* `playlist_directory "/tmp"`
* `user "root"`
* `auto_update "yes"` (you have to remove the # in front of that line)

Maybe you need to change the audio iFace in the config file, too. By default it uses `PCM` which should work out of the box. If it does not work, try `Master` or `Speakers`. Here you can find more information on [how to find the right audio iFace name](CONFIGURE-stretch.md#configAudioIFace) in the section 'Create settings for audio playout'.

* `mixer_control "yourAudioIfaceNameHere"` (you need to uncomment this line and change the audio iFace shortname)

Then you need to update `mpc`:

~~~
mpc update
~~~

## Using a USB soundcard

In order to use an external USB soundcard instead of the inbuilt audio out, you might need to update your system and tweak a couple of config files, depending on your card. The most comprehensive explanation on why and how, you can find at [adafruit](https://learn.adafruit.com/usb-audio-cards-with-a-raspberry-pi/instructions). 

Using the Jessie distribution, you might be lucky and there is a quick fix setting the [~/.asoundrc](https://raspberrypi.stackexchange.com/questions/39928/unable-to-set-default-input-and-output-audio-device-on-raspberry-jessie) file.

## Reboot your Raspberry Pi

Ok, after all of this, it's about time to reboot your Phoniebox. Make sure you have the static IP address at hand to login over SSH after the reboot.

~~~~
sudo reboot
~~~~

# Configure the Phoniebox

Continue with the configuration in the file [`CONFIGURE-stretch.md`](CONFIGURE-stretch.md).

# APPENDIX

## <a name="ssh-install"></a>Installation and configuration via SSH / headless installation

Setting up the Phoniebox via a SSH connection saves the need for a monitor and a mouse. The following worked on Raspian stretch.

* Flash your SD card with the Raspian image
* Eject the card and insert it again. This should get the `boot` partition mounted.
* In the boot partition, create a new empty file called `ssh`. This will enable the SSH server later.
* Create another file in the same place called `wpa_supplicant.conf`. Set the file content according to the following example:

```
ctrl_interface=DIR=/var/run/wpa_supplicant GROUP=netdev
network={
    ssid="YOUR_NETWORK_NAME"
    psk="YOUR_PASSWORD"
    key_mgmt=WPA-PSK
}
```

Note: This works for WPA-secured wifi networks, which should be the vast majority.

* Save the file
* Unmount and eject the card, insert it into the Raspy, boot.
* Find out the IP address of the raspberry. Most Wifi routers have a user interface that lists all devices in the network with the IP address they got assigned.
* Connect via ssh with username `pi` and password `raspberry`.
* Jump back to the [top of this document](#install) to walk through the other steps of the installation.

Sources

* [how-to-set-up-wifi-on-your-raspberry-pi-without-ethernet](https://howchoo.com/g/ndy1zte2yjn/how-to-set-up-wifi-on-your-raspberry-pi-without-ethernet)
* [how-to-enable-ssh-on-raspbian-without-a-screen](https://howchoo.com/g/ote0ywmzywj/how-to-enable-ssh-on-raspbian-without-a-screen)

