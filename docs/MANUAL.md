# Jukebox Manual

Before you can run the jukebox, you need to have it installed and configured. 
Make sure to go through the [installation](INSTALL.md) and [configuration](CONFIGURE.md) first.

In this manual you will learn:

* How to connect to the jukebox from any computer to add and edit audio files.
* How to register new RFID cards, assign them a *human readable* shortcut and add audio files for each card.
* How to add web streams to the playout files - and even mix web based and local files.
* How to control the jukebox through the web app.
* How to assign cards specific tasks such as changing the volume level or shutting down the jukebox.

## Connecting to the jukebox

You need to connect to the jukebox in order to manage audio files and register new RFID cards. There are two ways to connect to the jukebox.

1. Using SSH to log into the jukebox
2. Connect over the home network

Most of the jukebox management should be done with the second option: connecting over your home network. This is the easiest way to add and remove audio files, because you are using your file manager to copy and paste files onto the jukebox. Copying files to the jukebox using the SSH login is actually more complicated.

### Connecting over SSH

Find out more about how to [connect over SSH from Windows, Mac, Linux or Android on the official RPi page](https://www.raspberrypi.org/documentation/remote-access/ssh/).

### Connecting with Apple Mac OS X

* Start the **Finder** application.
* Select **Go** pulldown menu and go to **Connect to server...**
* As the server address, type `smb://` followed by the IP address of your jukebox. In my case this would be: `smb://192.168.178.199`
* The following screen requires you to login as a **Registered User**. Name and password are the ones you specified when installing the *Samba* server. I suggested to use `pi` and `raspberry`.
* Selecting **Remember this password...** will connect to the jukebox automatically.
* Now, if you go to the finder, at the bottom left menu under *Shared* you will find the IP address of your jukebox.
* Clicking on the IP in the left menu will open the files on the jukebox. Under `pi_network` you should see: `audiofolders`, `shotcuts`, `placeholder` and once you registered RFID cards also the file `latestID.txt` (all of which will be explained later).

### Connecting with Linux / Ubuntu

* Open the windows manager.
* Navigate to **Network** in the left menu or select **File** > **Connect to server...** from the pulldown menu.
* Clicking from **Network** to **Windows Network** will bring you to the Raspberry Pi home network.
* If you chose **File** > **Connect to server...**, type `smb://` followed by the IP address of your jukebox. In my case this would be: `smb://192.168.178.199`
* In both cases, you will be exposed to the login screen eventually.

## Registering a new RFID card or key fob

Everything about the jukebox is controlled with RFID cards or key fobs. Therefore, registering a card is the first thing you need to do. Registering a card means: finding out the unique ID of the card. Once you know the ID, you can either add content (music, web streams) or assign a function - like *increase volume*.

This is how you figure out the ID of a RFID card:

1. Boot up the jukebox.
2. Swipe the RFID card across the jukebox (you should hear a 'beep' sound when the reader recognises the card).
3. Open the shared folder in your windows manager over the home network (see above for details on how to connect).
4. Open the file `latestID.txt` by double clicking it. This file contains the information you need.

The file contains information about the card like the following:

~~~~
Card ID '0594672283' was used at '2017-02-02.12:26:08'.
This ID has been used before.
The shortcut points to audiofolder 'stop'.
~~~~

The first line lists the ID of the card: `0594672283`. 

The second line tells us that the card has been used before. Note that every time you swipe a card, the file `latestID.txt` is being created. Therefore it is very likely this file notes a card has been used before.

The third line is giving us information about a *human readable* shortcut given to this ID. In this case, there is a folder named `stop` - which can contain audio files or text files with links to web streams. 

### Making a 'human readable' shortcut for a card

Imagine you have a card with a sticker of birds on it. Every time somebody swipes the bird card across the jukebox, you want it to play a lot of bird sounds. And when you add or delete birds from the playlist, you don't want to need to know the card ID. You just want to drop the files into a folder called `birds`.

This is why you can assign *human readable* names for card IDs. This is how you do it:

1. Swipe the card across the jukebox.
2. Open the file `latestID.txt` to find out the card ID (e.g. `0594672283`).
3. Navigate to the folder `shortcuts` in your windows manager.
4. Open the file of the same name as the card ID with a text editor.
5. Change the content of that file to `birds`

Now you have told the jukebox that every time the card with the ID `0594672283` is swiped across, play what's in the folder `birds`. Let's continue and make that folder and the audio files inside.

### Creating a new audio playlist for a new card

Following the previous step, we now have a card that triggers the jukebox to seek the folder `birds` and play the contents of that folder as an audio playlist. This is how you create the folder and fill it with content:

1. Open your windows manager and connect to the jukebox via the home network.
2. Navigate to the folder `audiofolders`.
3. Create a new folder inside this folder called `birds`.
4. Copy audio files into this folder.

That's it. If you swipe the card across the jukebox, it will play all the files in the folder `birds`.

**Note:** files are played in alphabetical order. If you want to change the order, rename the files accordingly.

### Playing a web stream

An audio stream from the web can mean two things:

1. A live web radio station that plays endlessly.
2. A static file on the web that has a URL.

These two are actually very different and will result in different behaviour of the jukebox. A live web stream never stops. This means that it will continue to play until you shut down the machine or start something else by swiping a different card across the jukebox.

A static file on the web is more or less the same as a local file. The jukebox will play the content of the file and once it's finished, it will be idle waiting for the next card or continue playing the next file in the folder (see about mixing audio files and web streams in the next section).

This is how you add a web stream to a specific card:

1. Register the card, create a shortcut and the matching folder as described above.
2. Navigate to the folder you just created.
3. Create a text file ending with `.txt`, for example: `livewebradio.txt`.
4. Open the text file and copy the URL of the live stream (or static file) into the file.

That's it. Now, if you swipe with the card, the jukebox will open the matching folder, open the text file and send the content to the *VLC* media player.

**Note:** you can find a number of radio stations at the [Community Radio Browser](http://www.radio-browser.info). When you find a station you like, click on the *Save* icon which will download a file `radio.pls`. You can open this file with a text editor and within the file find the URL of the live web radio stream.

**Troubleshooting:** if you add a web stream or URL which is invalid, this might create the *VLC* media player to revert to what it played the last time it was launched. If your jukebox seems to become erratic, check the URLs in your audio folder.

### Mixing audio files and web streams

As described above, the media player will (attempt to) play any content it finds in a folder in alphabetical order. I decided to work with the *VLC* media player because it is very robust and really tries to play anything it can. This means it also mixes audio files and web streams.

If you want to create such a mix, simply mix the content inside the audio folder. The jukebox will play all content in alphabetical order. Keep this in mind if you plan the order of the playlist.

**Note:** if you add a URL from a live web station to the playlist, the jukebox will never get to play the files after this URL - because the live radio never stops.


## The Jukebox Web App

You can control the jukebox with your mobile phone, smart TV or through a browser on a computer. On any device connected to the same WiFi home network as your jukebox, open the browser and type in the static IP address of your jukebox. If you do this on your phone, the web app should something look like this:

![The web app allows you to change the volume level, list and play audio files and folders, stop the player and shut down the RPi gracefully.](/home/micz/Documents/bitbucket/musicbox/docs/img/web-app-iphone-screens.png "The web app allows you to change the volume level, list and play audio files and folders, stop the player and shut down the RPi gracefully.")

### Change the volume level

At the top of the page, you can select the volume level in a pulldown menu. Hit *Set volume* and the volume on your jukebox will be changed. This change will remain active even after a reboot.

### Play and list audio files

All the folders and containing audio files are listed in the web app. In case there are more folders on the jukebox than RFID cards in use, you can also play the audio files which have no corresponding RFID card using the web app.

Scroll to the folder you want to play and hit the *Play* icon left of the folder name. This will start the playout on the jukebox.

If you want to see the files contained inside an audio folder, click on the folder name. This will list the content beneath the folder name. A second click on the folder name will hide the list of files again.

### Stop playout

At the top of the page you can see the *Stop Player* icon. If you are using a mobile device, this option might be hidden within the navigation, in which case, click the hamburger icon to see the *Stop Player* option.

Click on the *Stop Player* icon to stop the playout on the jukebox.

### Shutdown the jukebox gracefully

At the top of the page, on the right side, you can see the option *Shutdown jukebox*. If you are using a mobile device, this option might be hidden within the navigation, in which case, click the hamburger icon to see the *Shutdown jukebox* option.

Click on *Shutdown jukebox* to shutdown the RPi gracefully. While it is perfectly save to shutdown the RPi the hard way by unplugging the power supply, it is being rumoured that a graceful shutdown extends the life expectancy of the SD card in your RPi. I have no clue if that is true and scientifically proven.

If you use the *Shutdown jukebox* option, unplug the RPi power supply after the machine has shut down to save energy.

## Jukebox controls using RFID cards

This requires you to connect to the jukebox over SSH, because it requires to edit a script on the machine. Find out more about how to [connect over SSH from Windows, Mac, Linux or Android on the official RPi page](https://www.raspberrypi.org/documentation/remote-access/ssh/).

If you are unsure about connecting over SSH, you can also take the jukebox and connect it to a monitor, keyboard and mouse and work on the machine directly.

The main file controlling the jukebox and the audio playout is called:

~~~~
/home/pi/RPi-Jukebox-RFID/scripts/rfid_trigger_play.sh
~~~~

This script operates in two stages. Firstly, it attempts to match the card ID with a command that controls the jukebox. If there is no match, it will move on and look for a folder which is associated with the card that contains audio material - and play the content.

If you want to assign certain control commands with RFID cards, firstly register the card to find out the unique ID (see above for details).

The commands which are available in the script are:

* **CMDMUTE** - will mute the jukebox. The file(s) continue to play, but there will be no sound coming out.
* **CMDVOL30** to **CMDVOL100** - sets the volume to the percentage passed on, being one of: 30%, 50%, 75%, 85%, 90%, 95%, 100%.
* **CMDSTOP** - stop the media player (without changing the volume).
* **CMDSHUTDOWN** - shutdown the jukebox. While you can switch off the RPi the hard way by unplugging it from the power source, in the long run using the proper shutdown method extends the life expectation of your jukebox. After the shutdown, you still should detach the power supply - if only to make sure the speakers don't drain power.

Once you have logged in to the RPi over SSH or booted with monitor and keyboard attached, open the script in the nano editor:

~~~~
$ nano /home/pi/RPi-Jukebox-RFID/scripts/rfid_trigger_play.sh
~~~~

Scroll down until you see the list of available commands:

~~~~
CMDMUTE="mute"
CMDVOL30="30"
CMDVOL50="50"
CMDVOL75="75"
CMDVOL80="80"
CMDVOL85="85"
CMDVOL90="90"
CMDVOL95="95"
CMDVOL100="100"
CMDSTOP="stop"
CMDSHUTDOWN="halt"
~~~~

Change the values of the commands you want to assign, leave the other ones unchanged. In our example, the changed list might look like this:

~~~~
CMDMUTE="0594672283"
CMDVOL30="30"
CMDVOL50="50"
CMDVOL75="75"
CMDVOL80="80"
CMDVOL85="85"
CMDVOL90="1594672283"
CMDVOL95="95"
CMDVOL100="100"
CMDSTOP="stop"
CMDSHUTDOWN="2594672283"
~~~~

Save the changes and close the editor. The changes takes effect immediately.

**Note:** if you (accidently) assign a command and an audio folder to the same card, the jukebox will not play the audio. It will only execute the command.