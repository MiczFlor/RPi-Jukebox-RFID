# Configure your Phoniebox on RPi Stretch

*Written for an tested on Raspbian GNU/Linux 9.4 (stretch) Kernel version: 4.14*

This is the second step. Make sure to go through the [installation](INSTALL-stretch.md) first.

Once you finished with the configuration, read the [manual](MANUAL.md) to add audio files and RFID cards.

## Identify and configure your RFID reader

The RFID reader is connected to your RPi via USB. As you plug it in, it should have made a 'beep'. And each time you swipe a keyring or card across the card reader, it should also make a 'beep'.

**NOTE:** if you are using **non-USB chip readers**, please take a look at these two threads for the [RDM6300 serial RFID module](https://github.com/MiczFlor/RPi-Jukebox-RFID/issues/175) and the [RC522 module](https://github.com/MiczFlor/RPi-Jukebox-RFID/issues/11). This will migrate to the docs eventually. And if you have cooked up your own solution for other devices, please share them in an [issue thread](https://github.com/MiczFlor/RPi-Jukebox-RFID/issues).

(Back to the plug'n'play USB readers)

Let's see if your reader is probably connected and recognised by your RPi. Check the following:

1. The LED on the reader is on.
2. When swiping a card or keyring, you hear a 'beep' noise.

If you can answer both with yes, you can be 90% sure all is working well. Just to be 100% sure, here are a few command to type on the command line which should list your reader.

~~~
ls -la /dev/input/by-id/
~~~

In my case, this will list the Barcode Reader and show that the system can interact with the device under `event0`:

~~~
lrwxrwxrwx 1 root root   9 Apr 30 09:55 usb-Sycreader_USB_Reader_08FF20150112-event-kbd -> ../event1
~~~

## Register your USB device for the Phoniebox

Now we know a lot about the RFID reader attached to our RPi. In order to use it as a controller for our Phoniebox, the software needs to know which device to listen to.

To register your device, go to the directory containing all the scripts and run the file `RegisterDevice.py`.

~~~
cd /home/pi/RPi-Jukebox-RFID/scripts/
python2 RegisterDevice.py
~~~

This will bring up a list of one or more devices. Spot the device you are using as a RFID reader, type the number (in this case *2*) and hit *Enter*.
~~~
Choose the reader from list
0 Chicony USB Keyboard
1 Chicony USB Keyboard
2 Sycreader USB Reader
3 Logitech USB-PS/2 Optical Mouse 
~~~

You can check if your device was registered properly by taking a look inside the file that was just generated, called `deviceName.txt`.

~~~~
cat deviceName.txt
~~~~

Now your Phoniebox knows which device to listen to when you are swiping your cards or keyrings.

## Copy the RFID chip configuration file

Inside the directory `/home/pi/RPi-Jukebox-RFID/settings/` you find the file `rfid_trigger_play.conf.sample` You need to make a copy of this files, to avoid overwriting changes if the content might change in the git repo.

Inside this `conf` file, you can add IDs from RFID cards to control
the functionality of the Phoniebox. See the content of the file for
more explanation.

~~~~
cd /home/pi/RPi-Jukebox-RFID/settings/
cp rfid_trigger_play.conf.sample rfid_trigger_play.conf
sudo chown pi:pi rfid_trigger_play.conf
sudo chmod 665 rfid_trigger_play.conf
~~~~

## <a name="configAudioIFace"></a>Create settings for audio playout

Creating files for the `settings` folder which contain the short name
of the amixer iface used and the percentage the volume increase or 
decreases when using the `volumeup` and `volumedown`  function.

**Troubleshooting**: 

* Inside `settings/Audio_iFace_Name` is the **iFace name** of the sound card. By default for the RPi this would be `PCM`. But this does not work for every setup. If you are using *phatbeat* as a DAC for example, you need to change the content of `Audio_iFace_Name` from `PCM` to `Master` or `Speaker`. Other external sound cards might use different interface names. To see if `PCM` could work for you, type `amixer sget PCM`.
To list all available iFace names, type `amixer scontrols`.
* If one is **using an audio amplifier (like the pHAT BEAT)** without a physical volume limiter (like a potentiometer) your Phoniebox can get very loud "accidentally". The maximal volume can be set in `settings/Max_Volume_Limit`.

~~~
echo "PCM" > /home/pi/RPi-Jukebox-RFID/settings/Audio_iFace_Name
echo "3" > /home/pi/RPi-Jukebox-RFID/settings/Audio_Volume_Change_Step
echo "100" > /home/pi/RPi-Jukebox-RFID/settings/Max_Volume_Limit
echo "0" > /home/pi/RPi-Jukebox-RFID/settings/Idle_Time_Before_Shutdown
~~~

## <a name="systemdautostart"></a>Auto-start the Phoniebox

This is the final tweak to the configuration: automatically start our Phoniebox software after the RPi has booted and have it listen to RFID cards. The Raspbian OS 9 (stretch) uses systemd to start the components.

**Systemd will launch the required services after booting AND take care of restarting the script in case they die**. 

First copy the service config files to the correct directory:

```
sudo cp /home/pi/RPi-Jukebox-RFID/misc/sampleconfigs/rfid-reader.service.stretch-default.sample /etc/systemd/system/rfid-reader.service
sudo cp /home/pi/RPi-Jukebox-RFID/misc/sampleconfigs/startup-sound.service.stretch-default.sample /etc/systemd/system/startup-sound.service
sudo cp /home/pi/RPi-Jukebox-RFID/misc/sampleconfigs/gpio-buttons.service.stretch-default.sample /etc/systemd/system/gpio-buttons.service
sudo cp /home/pi/RPi-Jukebox-RFID/misc/sampleconfigs/idle-watchdog.service.sample /etc/systemd/system/idle-watchdog.service
```

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

The newly installed service can be started either by rebooting the Phoniebox or
with:
```sudo systemctl start rfid-reader```

To see if the reader process is running use the following command:
```
sudo systemctl status rfid-reader
```
This should produce an output like this:
```
pi@Jukebox:~ $ systemctl status rfid-reader
 * rfid-reader.service - RFID-Reader Service
   Loaded: loaded (/etc/systemd/system/rfid-reader.service; enabled; vendor pres
   Active: active (running) since Fri 2018-04-13 07:34:53 UTC; 5h 47min ago
 Main PID: 393 (python2)
   CGroup: /system.slice/rfid-reader.service
           └─393 /usr/bin/python2 /home/pi/RPi-Jukebox-RFID/scripts/daemon_rfid_

Apr 13 07:34:53 Jukebox systemd[1]: Started RFID-Reader Service.
```

The mp3s for startup and shutdown sound have to be copied to the right folder. You may use your own sound files as well.
```
cp /home/pi/RPi-Jukebox-RFID/misc/sampleconfigs/startupsound.mp3.sample /home/pi/RPi-Jukebox-RFID/shared/startupsound.mp3
cp /home/pi/RPi-Jukebox-RFID/misc/sampleconfigs/shutdownsound.mp3.sample /home/pi/RPi-Jukebox-RFID/shared/shutdownsound.mp3
```

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

# Phoniebox manual

Now the installation and configuration are complete. Time to read the manual of the Phoniebox to add songs, web streams, register new cards and so on. Read the [`MANUAL.md`](MANUAL.md).
