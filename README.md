# Phoniebox: the RPi-Jukebox-RFID

A contactless jukebox for the Raspberry Pi, playing audio files, playlists, podcasts, web streams and spotify triggered by RFID cards. All plug and play via USB, no soldering iron needed. Update: if you must, it now also features a howto for adding GPIO buttons controls.

**MUST READ for users of [Phoniebox +Spotify Edition](docs/SPOTIFY-INTEGRATION.md)**

*Important update news*

* **Phoniebox 1.1.8 released** (2018-12-10)
* Two types of *one-line-install* scripts are now available. 
  * *Phoniebox Classic* supports local audio, web radio, podcasts, YouTube (download and convert), GPIO and/or RFID
  * *Phoniebox +Spotify* supports everything *Classic* does PLUS Spotify. However: the local audio management has changed for the *+Spotify* edition. [More about the changes in the +Spotify edition here.](docs/SPOTIFY-INTEGRATION.md)
   [One-line install script adding **Spotify** to your Phoniebox](https://github.com/MiczFlor/RPi-Jukebox-RFID/wiki/INSTALL-stretch#one-line-install-command), a much simpler install procedure: copy and paste one line into your terminal and hit *enter*. See the next bulletpoint for information on how you can help to improve the new Spotify version. (2018-11-09)
* **Spotify integration needs you** I invite everybody to use our [spotify thread](https://github.com/MiczFlor/RPi-Jukebox-RFID/issues/18) to post improvements regarding this feature. You might also want to [improve the documentation on *Spotify integration*](docs/SPOTIFY-INTEGRATION.md) - which will soon move to the wiki, getting us to the next bulletpoint.
* **Documentation moved to the wiki** The [GitHub wiki for Phoniebox](https://github.com/MiczFlor/RPi-Jukebox-RFID/wiki) is active. And in the making. Not sure if this is the best way to go, but please try to add content in the wiki regarding special hardware, software tweaks and the like.
* **Upgrade** if you are looking for *how to upgrade* please check out [UPGRADE.md](docs/UPGRADE.md) - and if you found out something that should go there, please create a pull request. (2018-10-18)
* **One Line Install Script** As of version 1.x there is . Find out more about the [one-line Phoniebox install script](https://github.com/MiczFlor/RPi-Jukebox-RFID/wiki/INSTALL-stretch#oneLineInstall). (2018-08-18)
* **Podcasts!** More for myself than anybody else, I guess, I added the [podcast feature for Phoniebox](https://github.com/MiczFlor/RPi-Jukebox-RFID/wiki/MANUAL#podcasts) (2018-05-09)
* **Bleeding edge: `develop` branch** The maintenance with a growing contributor team (kudos!) got complicated. I introduced the branch `develop` which is where all new stuff is happening before merged to `master`. Read the [CONTRIBUTING.md](docs/CONTRIBUTE.md) file for [more infos on how to contribute code](docs/CONTRIBUTE.md). (2018-08-30)
---

<a href="https://youtu.be/7GI0VdPehQI" target="_blank"><img src="docs/img/iFun-YouTube.jpg" alt="Prototype of the RFID jukebox" width="800" height="450" border="1" /></a>

*See the Phoniebox code in action, watch this video and read the blog post from [iphone-ticker.de](https://www.iphone-ticker.de/wochenend-projekt-kontaktlose-musikbox-fuer-kinder-123063/)*

**What makes this Phoniebox easy to install and use:**

* Runs on all Raspberry Pi models (1, 2 and 3) and [Raspberry Zero](https://github.com/MiczFlor/RPi-Jukebox-RFID/issues/15). (jump to the [install instructions](#install))
* Just plug and play using USB, no soldering iron needed.
* Once the Phoniebox is up and running, add music from any computer on your home network.
* Register new RFID cards easily without having to connect to the RPi.
* Play single or multiple files, podcasts or web streams.
* Volume control is also done with RFID cards or key fobs.
* Connect to your Phoniebox via your wifi network or run the Phoniebox like an access point and connect directly without a router.
* **Bonus:** control the Phoniebox from your phone or computer via a web app.

![The web app allows you to change the volume level, list and play audio files and folders, stop the player and shut down the RPi gracefully.](docs/img/web-app-iphone-screens.jpg "The web app allows you to change the volume level, list and play audio files and folders, stop the player and shut down the RPi gracefully.")

The **web app** runs on any device and is mobile optimised. It provides:

* An audio player to pause, resume, shuffle, loop, stop and skip to previous and next track.
* Sub folder support: manage your collection in sub folders. Phoniebox has two play buttons: only this folder and eeeeverything in this folder.
* Manage files and folders via the web app.
* Register new RFID cards, manage Phoniebox settings, display system info and edit the wifi connection.
* Covers displayed in the web app (files called `cover.jpg`).

## Phoniebox Gallery

|  |  |   |   |   |   |
| --- | --- | --- | --- | --- | --- |
| ![Caption](docs/img/gallery/Steph-20171215_h90-01.jpg "Caption") | ![Caption](docs/img/gallery/Elsa-20171210_h90-01.jpg "Caption") | ![Caption](docs/img/gallery/Geliras-20171228-Jukebox-01-h90.jpg "Caption") | ![Caption](docs/img/gallery/UlliH-20171210_h90-01.jpg "Caption") | ![Caption](docs/img/gallery/KingKahn-20180101-Jukebox-01-h90.jpg "Caption") | ![Caption](docs/img/gallery/hailogugo-20171222-h90-01.jpg "Caption") | 

**See more innovation, upcycling and creativity in the [Phoniebox Gallery](https://github.com/MiczFlor/RPi-Jukebox-RFID/wiki/GALLERY) or visit and share the project's homepage at [phoniebox.de](http://phoniebox.de/). There is also an [english Phoniebox page](http://phoniebox.de/index.php?l=en).**

## <a name="install"></a>Installation

* Installation instructions for Raspbian [Stretch](https://github.com/MiczFlor/RPi-Jukebox-RFID/wiki/INSTALL-stretch) are available in the `docs` folder.
* You can also use the [headless installation over ssh](https://github.com/MiczFlor/RPi-Jukebox-RFID/wiki/INSTALL-stretch#ssh-install) straight from a fresh SD card.
* For a quick install procedure, take a look at the [bash install script for Stretch](https://github.com/MiczFlor/RPi-Jukebox-RFID/blob/master/scripts/installscripts/stretch-install-default.sh). This should get you started quickly.
* If you choose the step by step installation, you need to walk through the configuration steps for [Stretch](https://github.com/MiczFlor/RPi-Jukebox-RFID/wiki/CONFIGURE-stretch).
* Once everything has been installed and configured, [read the manual](https://github.com/MiczFlor/RPi-Jukebox-RFID/wiki/MANUAL) to change settings, register RFID cards, add audio.

Adding push buttons to control volume, skipping tracks, pause, play: read the [GPIO buttons installation guide](docs/GPIO-BUTTONS.md).

## Manual

In the [Manual](https://github.com/MiczFlor/RPi-Jukebox-RFID/wiki/MANUAL) you will learn:

* [How to connect to the Phoniebox from any computer to add and edit audio files.](https://github.com/MiczFlor/RPi-Jukebox-RFID/wiki/MANUAL#connect)
* [How to register new RFID cards, assign them a *human readable* shortcut and add audio files for each card.](https://github.com/MiczFlor/RPi-Jukebox-RFID/wiki/MANUAL#registercards)
* [How to add webradio stations and other streams to the playout files](https://github.com/MiczFlor/RPi-Jukebox-RFID/wiki/MANUAL#webstreams) - [and even mix web based and local files.](https://github.com/MiczFlor/RPi-Jukebox-RFID/wiki/MANUAL#mixwebstreams)
* [Adding Podcasts the your Phoniebox](https://github.com/MiczFlor/RPi-Jukebox-RFID/wiki/MANUAL#podcasts)
* [How to control the Phoniebox through the web app.](https://github.com/MiczFlor/RPi-Jukebox-RFID/wiki/MANUAL#webapp)
* [How to assign cards specific tasks such as changing the volume level or shutting down the Phoniebox.](https://github.com/MiczFlor/RPi-Jukebox-RFID/wiki/MANUAL#cardcontrol)

## Contributing improvements

Read the [CONTRIBUTING.md](docs/CONTRIBUTE.md) file for [more infos on how to contribute code](docs/CONTRIBUTE.md).

## Reporting bugs

To make maintenance easier for everyone, please run the following script 
and post the results when reporting a bug.
(Note: the results contain some personal information like IP or SSID.
You might want to erase some of it before sharing with the bug report.)
~~~
/home/pi/RPi-Jukebox-RFID/scripts/helperscripts/Analytics_AfterInstallScript.sh 
~~~
Just copy this line and paste it into your terminal on the pi.

If you find something that doesn't work. And you tried and tried again, but it still doesn't work, please report your issue in the ["issues" section](https://github.com/MiczFlor/RPi-Jukebox-RFID/issues). Make sure to include information about the system and hardware you are using, like: 

*Raspberry ZERO, OS Jessie, Card reader lists as (insert here) when running scripts/RegisterDevice.py, installed Phoniebox version 0.9.3 (or: using latest master branch).*

## Troubleshooting

There is a growing section of [troubleshooting](https://github.com/MiczFlor/RPi-Jukebox-RFID/wiki/MANUAL#faq) including:

* I want to improve the onboard audio quality
* I am moving, how do I get the Phoniebox into my new WiFi network?
* The RFID Reader doesn't seem to work.
* Changing the volume does not work, but the playout works.
* Script `daemon_rfid_reader.py` only works via SSH not by RFID cards.
* Script daemon is closing down unexpectedly.
* Everything seems to work, but I hear nothing when swiping a card.
* I would like to use two cards / IDs to do the same thing.

## Acknowledgments

There are many, many, many inspiring suggestions and solutions on the web to bring together the idea of a jukebox with RFID cards. I want to mention a few of these that have inspired me.

* Thanks to all the [contributors](https://github.com/MiczFlor/RPi-Jukebox-RFID/graphs/contributors). Not only for the good code review and feature suggestions, but also for the good spirit I get each time a new Phoniebox comes to this world :)
* Thanks to Andreas aka [hailogugo](https://github.com/hailogugo) for writing and testing the script for the [GPIO buttons as controllers for the jukebox](docs/GPIO-BUTTONS.md).
* [Francisco Sahli's Music Cards: RFID cards + Spotify + Raspberry Pi](https://fsahli.wordpress.com/2015/11/02/music-cards-rfid-cards-spotify-raspberry-pi/) written in python, playing songs from Spotify. The code [music-cards](https://github.com/fsahli/music-cards) is on GitHub.
* [Jeremy Lightsmith's rpi-jukebox](https://github.com/jeremylightsmith/rpi-jukebox) written in Python, using the mpg123 player
* [Marco Wiedemeyer's Raspberry Pi Jukebox für Kinder (German)](https://mwiedemeyer.de/blog/post/Raspberry-Pi-Jukebox-fur-Kinder) written in mono, using the MPD player
* [Marcus Nasarek's Kindgerechter Audioplayer mit dem Raspberry Pi (German)](http://www.raspberry-pi-geek.de/Magazin/2014/03/Kindgerechter-Audioplayer-mit-dem-Raspberry-Pi) triggered by QR codes via a camera instead of RFID cards, written in bash and using the xmms2 media player
* [Huy Do's jukebox4kids / Jukebox für Kinder](http://www.forum-raspberrypi.de/Thread-projekt-jukebox4kids-jukebox-fuer-kinder) written in Python, [the code is on github](https://github.com/hdo/jukebox4kids)
* [Willem van der Jagt's How I built an audio book reader for my nearly blind grandfather](http://willemvanderjagt.com/2014/08/16/audio-book-reader/) written in python and using the MDP player.

For my rendition of the RFID jukebox, I have forked two files from [Francisco Sahli](https://github.com/fsahli/music-cards) to register the RFID reader and read the ID from the cards with the python scripts `Reader.py` and `RegisterDevice.py`.

I also want to link to two proprietary and commercial projects, because they also inspired me. And they challenged me, because of their shortcomings in terms of openness and in the case of tonies, the lack of "ownership" of the audiobooks and plays you actually bought. However, both products are very well made.

* [tonies® - das neue Audiosystem für mehr Hör-Spiel-Spaß im Kinderzimmer. (German)](https://tonies.de/) You buy a plastic figure which then triggers the audiofile - which is served over the web.
* [Hörbert - a MP3 player controlled by buttons](https://hoerbert.com) In Germany this has already become a *classic*. They also started selling a DIY kit.

## Shopping list

Here is a list of equipment needed. Chances are that you will find most of it in the back of your drawers or at the bottom of some shoe box. Well, most of it, possibly not the RFID reader itself.

* **Has to be returned** [USB Stereo Speaker Set (6 Watt, 3,5mm jack, USB-powered) black](https://www.notebooksbilliger.de/trust+leto+20+speaker+set+black/?nbb=pla.google_&wt_cc2=902-0001_Hardware_253868&gclid=EAIaIQobChMIzoaZ9J763gIVyqSaCh1hKAV1EAQYASABEgLAY_D_BwE) | This USB powered speaker set sounds good for its size, is good value for money and keeps this RPi project clean and without the need of a soldering iron :)
* **obtained** Speaker cables
* **obtained** sd card
* **obtained** [raspberry pi 3 model b ](http://amzn.to/2ku0pu7) | you might be surprised how easy and affordable you can get an rpi second hand. think about the planet before you buy a new one.
* **obtained** RFID Card Reader (USB): [Neuftech USB RFID Reader ID](https://www.ebay.de/sch/i.html?_from=R40&_trksid=m570.l1313&_nkw=Neuftech+USB+RFID+Reader+ID&_sacat=0) using 125 kHz - make sure to buy compatible cards, RFID stickers or key fobs working with the same frequency as the reader. **Important notice:** the hardware of the reader that I had linked here for a long times seems to have changed and suddenly created problems with the Phoniebox installation. The reader listed now has worked and was recommended by two Phoniebox makers (2018 Oct 4). I can not guarantee that this will not change and invite you to give [RFID Reader feedback in this thread](https://github.com/MiczFlor/RPi-Jukebox-RFID/issues/231).  
* **obtained** JR45 socket for housing
* **obtained** Six push buttons (<https://www.reichelt.de/drucktaster-0-2a-60vdc-1x-ein-beleuchtet-gn-t-9146-gn-p44434.html?> and <https://www.reichelt.de/arcade-button-mit-mikroschalter-gelb-arc-button-ye-p225321.html?>)
* **obtained** Electric resistor for led (<https://www.reichelt.de/duennschichtwiderstand-axial-0-6-w-75-ohm-1-vi-mbb02070c7509-p233774.html?>)
* **obtained** 20 Jumper cables (<https://www.reichelt.de/entwicklerboards-steckbrueckenkabel-20-pole-m-m-f-f-f-m-25-debo-kabelset-p161046.html?>)
* **obtained** Short network cable internal
* **obtained** Broadband speaker FR 10HM (<https://www.reichelt.de/breitbandlautsprecher-fr-10hm-20-w-8-ohm-vis-fr-10hm-8-p66815.html?>)
* **obtained** Audio jack adapter, 3,5 mm, Stereo, 3-pol, terminal block (<https://www.reichelt.de/klinkenstecker-3-5-mm-stereo-3-pol-terminalblock-delock-65419-p127460.html?>)
* **obtained** Audio amplifier, Stereo, 3,7 W, class D (<https://www.reichelt.de/entwicklerboards-audioverstaerker-stereo-3-7-w-klasse-d-debo-sound-amp2-p235507.html?>)
* **obtained** Speaker cover (<https://www.reichelt.de/lueftergitter-90-x-90-x-5-5-mm-stahl-silber-rnd-460-00041-p223501.html?>)
* **obtained** Power bank (<https://www.reichelt.de/powerbank-li-po-20800-mah-usb-ans-pb-20800-p195298.html?>)
* **included in RFID reader** Five RFID tags
* **included in button** One led
* **postponed** Switch to disconnect power consumers from power pack
* **postponed** USB charging outlet
* **postponed** Headphone connector?

### Special hardware

These are links to additional items which are not needed, but might be what you want to make your dream of a Phoniebox come true:

* [Ground Loop Isolator / Entstörfilter Audio](https://amzn.to/2Kseo0L) this seems to [get rid off crackles in the audio out (a typical RPi problem)](https://github.com/MiczFlor/RPi-Jukebox-RFID/issues/341) 
* [Drehregler / Rotary Encoder / Dial](https://amzn.to/2J34guF) for volume control. Read here for more information on how to [integrate the rotary dial](https://github.com/MiczFlor/RPi-Jukebox-RFID/issues/267) 
* [HiFiBerry DAC+ Soundcard](https://amzn.to/2J36cU9) Read here for more information on how to [HifiBerry Soundcard integration](https://github.com/MiczFlor/RPi-Jukebox-RFID/wiki/MANUAL#hifiberry-dac-soundcard-details)
