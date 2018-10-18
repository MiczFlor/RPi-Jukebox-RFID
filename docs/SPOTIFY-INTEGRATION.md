
# Spotify support for Phoniebox

**Testers needed for the Spotify integration** to make it universal and include into the install process soon. Please read [more in this thread](https://github.com/MiczFlor/RPi-Jukebox-RFID/issues/18#issuecomment-430140524).
This is the first draft (2018-10-18) of the documentation on how to integrate Spotify into your Phoniebox. It starts from scratch (i.e. with the installation of the stretch OS). Please add, edit and comment to this document while testing the code on the `develop` branch.

The plan is to have an alternative isntall script for the Spotify version alongside the default install. Later I plan to make this an option in the default install script.

## Installing stretch on your Pi

1. Install Strech on SD Card.
2. Remove card and insert again.

Setting up the Phoniebox via a SSH connection saves the need for a monitor and a mouse. The following worked on Raspian stretch.

* Flash your SD card with the Raspian image
* Eject the card and insert it again. This should get the boot partition mounted.
* In the boot partition, create a new empty file called ssh. This will enable the SSH server later.
* Create another file in the same place called wpa_supplicant.conf. Set the file content according to the following example:
~~~
ctrl_interface=DIR=/var/run/wpa_supplicant GROUP=netdev
network={
	ssid="YOUR_NETWORK_NAME"
	psk="YOUR_PASSWORD"
	key_mgmt=WPA-PSK
}
~~~
Note: This works for WPA-secured wifi networks, which should be the vast majority.

* Save the file
* Unmount and eject the card, insert it into the Raspy, boot.
* Find out the IP address of the raspberry. Most Wifi routers have a user interface that lists all devices in the network with the IP address they got assigned.
* Connect via ssh with username pi and password raspberry.
* Jump back to the top of this document to walk through the other steps of the installation.

## Sort Order of sound cards - correction.

~~~
cat /proc/asound/modules
~~~
You get:
~~~
0 snd_bcm2835
1 snd_usb_audio
~~~
Change sort order:
~~~
sudo nano /etc/modprobe.d/alsa-base.conf
~~~
If file is empty, add the following lines:
~~~
options snd_usb_audio index=0
options snd_bcm2835 index=1
options snd slots=snd-usb-audio,snd-bcm2835
~~~
After reboot you get:
~~~
cat /proc/asound/modules

0 snd_usb_audio
1 snd_bcm2835
~~~
## For Root-User
~~~
sudo passwd root
sudo nano /etc/ssh/sshd_config
~~~
Search for PermitRootLogin and change it to yes.
	
## Install MOPIDY

Add the archive’s GPG key:
~~~
wget -q -O - https://apt.mopidy.com/mopidy.gpg | sudo apt-key add -
~~~
Add the APT repo to your package sources:
~~~
sudo wget -q -O /etc/apt/sources.list.d/mopidy.list https://apt.mopidy.com/stretch.list
~~~
Install Mopidy and all dependencies:
~~~
sudo apt-get update
sudo apt-get install mopidy
~~~
Finally, you need to set a couple of config values, and then you’re ready to run Mopidy. Alternatively you may want to have Mopidy run as a system service, automatically starting at boot.

To install one of the listed packages, e.g. mopidy-spotify, simply run the following:
~~~
sudo rm -rf /usr/lib/python2.7/dist-packages/mopidy_spotify*
sudo rm -rf /usr/lib/python2.7/dist-packages/Mopidy_Spotify-*
cd
sudo rm -rf mopidy-spotify
git clone -b fix/incompatible_playlists --single-branch https://github.com/BlackLight/mopidy-spotify.git
cd mopidy-spotify
sudo python setup.py install
~~~

## Mopidy as service...

On modern systems using systemd you can enable the Mopidy service by running:
~~~
sudo systemctl enable mopidy
~~~
This will make Mopidy start when the system boots.
Mopidy is started, stopped, and restarted just like any other systemd service:
~~~
sudo systemctl start mopidy
sudo systemctl stop mopidy
sudo systemctl restart mopidy
~~~
You can check if Mopidy is currently running as a service by running:
~~~
sudo systemctl status mopidy
~~~		
## Install MOPIDY-IRIS Web Interface
~~~
sudo pip install Mopidy-Iris
su -
sudo echo "mopidy ALL=NOPASSWD: /usr/local/lib/python2.7/dist-packages/mopidy_iris/system.sh" >> /etc/sudoers
sudo reboot
~~~
## Configure Mopidy...
~~~
sudo nano /etc/mopidy/mopidy.conf
~~~
Add to the end if entries not exist (you have to get client-id and client-secret here: https://www.mopidy.com/authenticate/ )
This must be done manually. Put your username, password, client_id, client_secret into the spotify section.
The audio section has to be tested, because i don't know if  "output = alsasink" works for everyone. "mixer_volume" is the start volume of phoniebox! attention: if you leave this blank, volume will be 100% after reboot!!
~~~
[audio]
output = alsasink
mixer_volume = 30

[mpd]
hostname = 0.0.0.0

[http]
hostname = 0.0.0.0

[iris]
country = DE
locale = de_DE

[spotify]
enabled = true
username = spotify_username
password = spotify_password
client_id = spotify_client_id
client_secret = spotify_client_secret
#bitrate = 160
#volume_normalization = true
#private_session = false
#timeout = 10
#allow_cache = true
#allow_network = true
#allow_playlists = true
#search_album_count = 20
#search_artist_count = 10
#search_track_count = 50
#toplist_countries =

[spotify_web]
client_id = spotify_client_id
client_secret = spotify_client_secret
~~~
Then edit this file:
~~~
sudo nano ~/.config/mopidy/mopidy.conf
~~~
Like this:
~~~
# For further information about options in this file see:
#   http://docs.mopidy.com/
#
# The initial commented out values reflect the defaults as of:
#   Mopidy 2.2.0
#   Mopidy-File 2.2.0
#   Mopidy-HTTP 2.2.0
#   Mopidy-Iris 3.27.1
#   Mopidy-Local 2.2.0
#   Mopidy-Local-Images 1.0.0
#   Mopidy-M3U 2.2.0
#   Mopidy-MPD 2.2.0
#   Mopidy-SoftwareMixer 2.2.0
#   Mopidy-Spotify 3.1.0
#   Mopidy-Stream 2.2.0
#
# Available options and defaults might have changed since then,
# run `mopidy config` to see the current effective config and
# `mopidy --version` to check the current version.

[core]
cache_dir = $XDG_CACHE_DIR/mopidy
config_dir = $XDG_CONFIG_DIR/mopidy
data_dir = $XDG_DATA_DIR/mopidy
max_tracklist_length = 10000
restore_state = false

[logging]
#color = true
#console_format = %(levelname)-8s %(message)s
#debug_format = %(levelname)-8s %(asctime)s [%(process)d:%(threadName)s] %(name)s\n  %(message)s
#debug_file = mopidy.log
#config_file =

[audio]
#mixer = software
mixer_volume = 30
output = alsasink
#buffer_time = 

[proxy]
#scheme = 
#hostname = 
#port = 
#username = 
#password = 

[local-images]
#enabled = true
#library = json
#base_uri = /images/
#image_dir = 
#album_art_files = 
#  *.jpg
#  *.jpeg
#  *.png

[iris]
#enabled = true
country = DE
locale = de_DE
#spotify_authorization_url = https://jamesbarnsley.co.nz/iris/auth_spotify.php
#lastfm_authorization_url = https://jamesbarnsley.co.nz/iris/auth_lastfm.php
#genius_authorization_url = https://jamesbarnsley.co.nz/iris/auth_genius.php
#snapcast_enabled = false
#snapcast_host = localhost
#snapcast_port = 1705

[mpd]
#enabled = true
hostname = 0.0.0.0
#port = 6600
#password = 
#max_connections = 20
#connection_timeout = 60
#zeroconf = Mopidy MPD server on $hostname
#command_blacklist = 
#  listall
#  listallinfo
#default_playlist_scheme = m3u

[http]
#enabled = true
hostname = 0.0.0.0
#port = 6680
#static_dir =
#zeroconf = Mopidy HTTP server on $hostname
#allowed_origins = 

[stream]
#enabled = true
#protocols = 
#  http
#  https
#  mms
#  rtmp
#  rtmps
#  rtsp
#metadata_blacklist = 
#timeout = 5000

[m3u]
#enabled = true
#base_dir = $XDG_MUSIC_DIR
#default_encoding = latin-1
#default_extension = .m3u8
#playlists_dir =

[softwaremixer]
#enabled = true

[file]
#enabled = true
#media_dirs = 
#  $XDG_MUSIC_DIR|Music
#  ~/|Home
#excluded_file_extensions = 
#  .jpg
#  .jpeg
#show_dotfiles = false
#follow_symlinks = false
#metadata_timeout = 1000

[local]
#enabled = true
#library = json
#media_dir = $XDG_MUSIC_DIR
#scan_timeout = 1000
#scan_flush_threshold = 100
#scan_follow_symlinks = false
#excluded_file_extensions = 
#  .directory
#  .html
#  .jpeg
#  .jpg
#  .log
#  .nfo
#  .png
#  .txt

[spotify]
enabled = true
username = spotify_username
password = spotify_password
client_id = spotify_client_id
client_secret = spotify_client_secret
#bitrate = 160
#volume_normalization = true
#private_session = false
#timeout = 10
#allow_cache = true
#allow_network = true
#allow_playlists = true
#search_album_count = 20
#search_artist_count = 10
#search_track_count = 50
#toplist_countries =

[spotify_web]
client_id = spotify_client_id
client_secret = spotify_client_secret
~~~

## Install Phoniebox
~~~
cd; rm stretch-install-default*; wget https://raw.githubusercontent.com/MiczFlor/RPi-Jukebox-RFID/master/scripts/installscripts/stretch-install-default.sh; chmod +x stretch-install-default.sh; ./stretch-install-default.sh
~~~
## Change Playlists_Folders_Path to:
~~~
/var/lib/mopidy/playlists
~~~
## You have to disable MPD because we use mopidy instead and MPD is included there.

If you don't disable MPD here, mopidy will not run!!!
~~~
sudo systemctl disable mpd
~~~
## Charset problems in display?
If you have problems with UTF-8 and ANSI, try to start raspi-config and change localisation to UTF-8.
I don't know if it works, for me it does after several tries.

## How to use Spotify?

When you right-click an album, a track or a playlist in MOPIDY IRIS or Spotify Client (share button), you get a Spotify URI.
This Spotify URI must be used when registering a card with the following syntax:
~~~
Tracks: spotify:track:######################
Albums: spotify:album:######################
Playlists: spotify:user:username:playlist:######################
(e.g. spotify:user:spotify:playlist:37i9dQZF1DWUVpAXiEPK8P or 
spotify:user:tomorrowlandofficial:playlist:0yS25E7g9xQZ1Dst5SqUZn)

Podcast: spotify:show:###################### (This has not been tested yet!)
~~~
The information will be stored in a spotify.txt in an audiofolder.
