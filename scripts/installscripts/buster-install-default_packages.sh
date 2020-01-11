##################################################### 
# INSTALLATION

# power management of wifi: switch off to avoid disconnecting
sudo iwconfig wlan0 power off


# Install required packages
sudo apt-get update
sudo apt-get --yes --allow-downgrades --allow-remove-essential --allow-change-held-packages install apt-transport-https samba samba-common-bin python-dev python-pip gcc raspberrypi-kernel-headers lighttpd php7.3-common php7.3-cgi php7.3 php7.3-fpm at mpd mpc mpg123 git ffmpeg python-mutagen python3-gpiozero resolvconf spi-tools python-spidev python3-spidev

# Install required spotify packages
	wget -q -O - https://apt.mopidy.com/mopidy.gpg | sudo apt-key add -
	sudo wget -q -O /etc/apt/sources.list.d/mopidy.list https://apt.mopidy.com/buster.list
	sudo apt-get update

  sudo apt-get install --yes libspotify-dev mopidy=2.3.1-1
	sudo python2.7 -m pip install Mopidy==2.3.*

	sudo apt-get --yes --allow-downgrades --allow-remove-essential --allow-change-held-packages install libspotify12 python-cffi python-ply python-pycparser python-spotify
	sudo rm -rf /usr/lib/python2.7/dist-packages/mopidy_spotify*
	sudo rm -rf /usr/lib/python2.7/dist-packages/Mopidy_Spotify-*
	cd
	sudo rm -rf mopidy-spotify
	git clone -b fix/web_api_playlists --single-branch https://github.com/princemaxwell/mopidy-spotify.git
	cd mopidy-spotify
	sudo python setup.py install
	cd
	# should be removed, if Mopidy-Iris can be installed normally
	# pylast >= 3.0.0 removed the python2 support
	sudo pip install pylast==2.4.0
  sudo pip install 'tornado==5.0'
	sudo pip install Mopidy-Iris

# Get github code
cd /home/pi/
git clone https://github.com/MiczFlor/RPi-Jukebox-RFID.git

# Jump into the Phoniebox dir
cd RPi-Jukebox-RFID

# Install more required packages
sudo pip install -r requirements.txt

# actually, for the time being most of the requirements are run here.
# the requirements.txt version seems to throw errors. Help if you can to fix this:

sudo pip install "evdev == 0.7.0"
sudo pip install --upgrade youtube_dl
sudo pip install git+git://github.com/lthiery/SPI-Py.git#egg=spi-py
sudo pip install pyserial
# spidev is currently installed via apt-get
#sudo pip install spidev
sudo pip install RPi.GPIO
sudo pip install pi-rc522

# Switch of WiFi power management
sudo iwconfig wlan0 power off

