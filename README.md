# Phoniebox: the RPi-Jukebox-RFID

A contactless jukebox for the Raspberry Pi, playing audio files, playlists, podcasts, web streams triggered by RFID cards. All plug and play via USB, no soldering iron needed. Update: if you must, it now also features a howto for adding GPIO buttons controls.

*Important update news*

* **Phoniebox 1.1.1 released** Adding *recursive folder playout* and *recording* to the Phoniebox. With version 1.0.0 we switched the audio player to `mpd`, added *resume play* for audiobook lovers, RFID switch for *wifi off*, new *player interface*, *random* and *repeat*. At this stage the *recursive* playout only works in the web app, not RFID cards. (2018-09-13)
* **Upgrade** if you are looking for *how to upgrade* please check out [UPGRADE.md](docs/UPGRADE.md) - and if you found out something that should go there, please create a pull request. (2018-09-10)
* **One Line Install Script** As of version 1.0 there is a much simpler install procedure: copy and paste one line into your terminal and hit *enter*. Find out more about the [one-line Phoniebox install script](docs/INSTALL-stretch.md#oneLineInstall). (2018-08-18)
* **Podcasts!** More for myself than anybody else, I guess, I added the [podcast feature for Phoniebox](docs/MANUAL.md#podcasts) (2018-05-09)
* **Bleeding edge: `develop` branch** The maintenance with a growing contributor team (kudos!) got complicated. I introduced the branch `develop` which is where all new stuff is happening before merged to `master`. (2018-08-30)
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

**See more innovation, upcycling and creativity in the [Phoniebox Gallery](docs/GALLERY.md) or visit and share the project's homepage at [phoniebox.de](http://phoniebox.de/). There is also an [english Phoniebox page](http://phoniebox.de/index.php?l=en).**

## <a name="install"></a>Installation

* Installation instructions for Raspbian [Stretch](docs/INSTALL-stretch.md) are available in the `docs` folder.
* You can also use the [headless installation over ssh](docs/INSTALL-stretch.md#ssh-install) straight from a fresh SD card.
* For a quick install procedure, take a look at the [bash install script for Stretch](https://github.com/MiczFlor/RPi-Jukebox-RFID/blob/master/scripts/installscripts/stretch-install-default.sh). This should get you started quickly.
* If you choose the step by step installation, you need to walk through the configuration steps for [Stretch](docs/CONFIGURE-stretch.md).
* Once everything has been installed and configured, read the manual to change settings, register RFID cards, add audio: [`MANUAL.md`](docs/MANUAL.md)

Adding push buttons to control volume, skipping tracks, pause, play: read the [GPIO buttons installation guide](docs/GPIO-BUTTONS.md).

## Manual

In [`MANUAL.md`](docs/MANUAL.md) you will learn:

* [How to connect to the Phoniebox from any computer to add and edit audio files.](docs/MANUAL.md#connect)
* [How to register new RFID cards, assign them a *human readable* shortcut and add audio files for each card.](docs/MANUAL.md#registercards)
* [How to add webradio stations and other streams to the playout files](docs/MANUAL.md#webstreams) - [and even mix web based and local files.](docs/MANUAL.md#mixwebstreams)
* [Adding Podcasts the your Phoniebox](docs/MANUAL.md#podcasts)
* [How to control the Phoniebox through the web app.](docs/MANUAL.md#webapp)
* [How to assign cards specific tasks such as changing the volume level or shutting down the Phoniebox.](docs/MANUAL.md#cardcontrol)

## Contributing improvements

The preferred way of code contributions are [pull requests (follow this link for a small howto)](https://www.digitalocean.com/community/tutorials/how-to-create-a-pull-request-on-github). And ideally pull requests using the "running code" on your Phoniebox. Alternatively, feel free to post tweaks, suggestions and snippets in the ["issues" section](https://github.com/MiczFlor/RPi-Jukebox-RFID/issues).

## Reporting bugs

If you find something that doesn't work. And you tried and tried again, but it still doesn't work, please report your issue in the ["issues" section](https://github.com/MiczFlor/RPi-Jukebox-RFID/issues). Make sure to include information about the system and hardware you are using, like: 

*Raspberry ZERO, OS Jessie, Card reader lists as (insert here) when running scripts/RegisterDevice.py, installed Phoniebox version 0.9.3 (or: using latest master branch).*

## Troubleshooting

There is a growing section of [troubleshooting](docs/MANUAL.md#faq) including:

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

* [Raspberry Pi 3 Model B ](http://amzn.to/2ku0PU7) | You might be surprised how easy and affordable you can get an RPi second hand. Think about the planet before you buy a new one.
* [Contactless RFID IC Card Reader with USB Interface PLUS 5 Cards + 5 Key Fob](http://amzn.to/2kXkMjr) | This package is good value for money, because it gets you started, including everything plus 5 RFID cards and 5 key fobs. 
* [USB Stereo Speaker Set (6 Watt, 3,5mm jack, USB-powered) black](http://amzn.to/2kXrard) | This USB powered speaker set sounds good for its size, is good value for money and keeps this RPi project clean and without the need of a soldering iron :)
* [External USB Soundcard with Virtual Surround Sound, Plug & Play](http://amzn.to/2kXflBf) | The additional soundcard is optional. If you don't like the sound coming straight from the RPi jack, this is a good value for money USB soundcard.
* [USB A Male to Female Extenstion Cable with Switch On/Off](http://amzn.to/2hHrvkG) | I placed this USB extension between the USB power adapter and the Phoniebox. This will allow you to switch the Phoniebox on and off easily.
* [USB 2.0 Hub 4-port bus powered USB Adapter](http://amzn.to/2kXeErv) | Depending on your setup, you will need none, one or two of these. If you are using the external USB powered speakers, you need one to make sure the speakers get enough power. If you want to use the additional USB soundcard and have an older RPi, you might need a second one to make sure you can connect enough devices with the RPi.
