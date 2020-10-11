
# How to upgrade the Phoniebox code

Assuming that you use `git pull` to update the code base of your Phoniebox,
every now and then you need to run some update scripts, like patches.
To make this somewhat consistent, I started this page to document things that need to be done.

If you still encounter problems after running the below upgrade snippets, check inside the folder `scripts/installscripts/` for scripts which contain the entire install process.

## Which version am I on?

There is a file `settings/version` containing the version number.

**Note:*** This is work in progress, please share experience, improvements and insights in the [issue section](https://github.com/chbuehlmann/RPi-Jukebox-RFID/issues).

# Upgrade from Version 1.1.7 to 1.1.8

**NOTE**: version `1.1.8` is the `master` branch. If you run into issues, please ask them on the "issues" board on GitHub. [2018-12-10].

And in capital letters: **YOUR BEST CHOICE IS TO GET A NEW SD CARD AND DO A FRESH INSTALL FOR THE NEW 1.1.8 VERSION, BECAUSE A LOT HAS CHANGED AS YOU CAN SEE IN THE UPGRADE SCRIPT BELOW** (now you can't say you didn't know...)

We introduce Phoniebox Editions. To distinguish them, we call them "Phoniebox Classic" (out of the box, no Spotify) and "Phoniebox +Spotify" (Phoniebox with Spotify integration).

**This is a bugfix-version.** After release of "Phoniebox +Spotify" there were reported some problems, which are bugfixed now, hopefully. e.g. Improved loading time of local music **(please go to "Folders & Files" and scan your library ONCE after update and everytime you upload new files to your box!)**. To reduce the boot up time of Phoniebox, be sure you are using the newest version of mopidy-spotify. The upgrade is integrated into the following steps.

**Please use our [spotify thread](https://github.com/chbuehlmann/RPi-Jukebox-RFID/issues/18) to post improvements regarding this feature.**

~~~
cd /home/pi/RPi-Jukebox-RFID
git checkout master
git fetch origin
git reset --hard origin/master
git pull
sudo systemctl stop mpd
sudo systemctl stop mopidy

USERNAME=$(sudo grep 'username' /etc/mopidy/mopidy.conf|sed 's/username = //g'|sed 's/"//g'|tr -d "\n")
PASSWORD=$(sudo grep 'password' /etc/mopidy/mopidy.conf|sed 's/password = //g'|sed 's/"//g'|tr -d "\n")
CLIENT_ID=$(sudo grep 'client_id' /etc/mopidy/mopidy.conf|sed 's/client_id = //g'|sed 's/"//g'|tr -d "\n")
CLIENT_SECRET=$(sudo grep 'client_secret' /etc/mopidy/mopidy.conf|sed 's/client_secret = //g'|sed 's/"//g'|tr -d "\n")

sudo cp /home/pi/RPi-Jukebox-RFID/misc/sampleconfigs/mpd.conf.sample /etc/mpd.conf
sudo cp /home/pi/RPi-Jukebox-RFID/misc/sampleconfigs/mopidy-etc.sample /etc/mopidy/mopidy.conf
sudo cp /home/pi/RPi-Jukebox-RFID/misc/sampleconfigs/mopidy.sample /home/pi/.config/mopidy/mopidy.conf

sudo sed -i 's/%spotify_username%/'"$USERNAME"'/' /etc/mopidy/mopidy.conf
sudo sed -i 's/%spotify_password%/'"$PASSWORD"'/' /etc/mopidy/mopidy.conf
sudo sed -i 's/%spotify_client_id%/'"$CLIENT_ID"'/' /etc/mopidy/mopidy.conf
sudo sed -i 's/%spotify_client_secret%/'"$CLIENT_SECRET"'/' /etc/mopidy/mopidy.conf
sudo sed -i 's/%spotify_username%/'"$USERNAME"'/' ~/.config/mopidy/mopidy.conf
sudo sed -i 's/%spotify_password%/'"$PASSWORD"'/' ~/.config/mopidy/mopidy.conf
sudo sed -i 's/%spotify_client_id%/'"$CLIENT_ID"'/' ~/.config/mopidy/mopidy.conf
sudo sed -i 's/%spotify_client_secret%/'"$CLIENT_SECRET"'/' ~/.config/mopidy/mopidy.conf

# services to launch after boot using systemd
# -rw-r--r-- 1 root root  304 Apr 30 10:07 phoniebox-rfid-reader.service
# 1. delete old services (this is legacy, might throw errors but is necessary. Valid for versions < 1.1.8-beta)
echo "### Deleting older versions of service daemons. This might throw errors, ignore them"
sudo systemctl disable idle-watchdog
sudo systemctl disable rfid-reader
sudo systemctl disable startup-sound
sudo systemctl disable gpio-buttons
sudo rm /etc/systemd/system/rfid-reader.service 
sudo rm /etc/systemd/system/startup-sound.service
sudo rm /etc/systemd/system/gpio-buttons.service
sudo rm /etc/systemd/system/idle-watchdog.service
echo "### Done with erasing old daemons. Stop ignoring errors!" 
# 2. install new ones - this is version > 1.1.8-beta
sudo cp /home/pi/RPi-Jukebox-RFID/misc/sampleconfigs/phoniebox-rfid-reader.service.stretch-default.sample /etc/systemd/system/phoniebox-rfid-reader.service 
sudo cp /home/pi/RPi-Jukebox-RFID/misc/sampleconfigs/phoniebox-startup-sound.service.stretch-default.sample /etc/systemd/system/phoniebox-startup-sound.service
sudo cp /home/pi/RPi-Jukebox-RFID/misc/sampleconfigs/phoniebox-gpio-buttons.service.stretch-default.sample /etc/systemd/system/phoniebox-gpio-buttons.service
sudo cp /home/pi/RPi-Jukebox-RFID/misc/sampleconfigs/phoniebox-idle-watchdog.service.sample /etc/systemd/system/phoniebox-idle-watchdog.service
sudo chown root:root /etc/systemd/system/phoniebox-rfid-reader.service
sudo chown root:root /etc/systemd/system/phoniebox-startup-sound.service
sudo chown root:root /etc/systemd/system/phoniebox-gpio-buttons.service
sudo chown root:root /etc/systemd/system/phoniebox-idle-watchdog.service
sudo chmod 644 /etc/systemd/system/phoniebox-rfid-reader.service
sudo chmod 644 /etc/systemd/system/phoniebox-startup-sound.service
sudo chmod 644 /etc/systemd/system/phoniebox-gpio-buttons.service
sudo chmod 644 /etc/systemd/system/phoniebox-idle-watchdog.service
# enable the services needed
sudo systemctl enable phoniebox-idle-watchdog
sudo systemctl enable phoniebox-rfid-reader
sudo systemctl enable phoniebox-startup-sound
sudo systemctl enable phoniebox-gpio-buttons

echo "classic" > /home/pi/RPi-Jukebox-RFID/settings/edition
EDITION=$(grep 'SPOTinstall' /home/pi/PhonieboxInstall.conf|sed 's/SPOTinstall="//g'|sed 's/"//g'); if [ $EDITION == "YES" ]; then echo "plusSpotify"; else echo "classic"; fi > /home/pi/RPi-Jukebox-RFID/settings/edition

sudo apt-get install libspotify12 python-cffi python-ply python-pycparser python-spotify
sudo rm -rf /usr/lib/python2.7/dist-packages/mopidy_spotify*
sudo rm -rf /usr/lib/python2.7/dist-packages/Mopidy_Spotify-*
sudo rm -rf /usr/local/lib/python2.7/dist-packages/mopidy_spotify*
sudo rm -rf /usr/local/lib/python2.7/dist-packages/Mopidy_Spotify-*
cd
sudo rm -rf mopidy-spotify
git clone -b fix/web_api_playlists --single-branch https://github.com/princemaxwell/mopidy-spotify.git
cd mopidy-spotify
sudo python setup.py install

sudo sed -i '/level/s/\bINFO\b/WARNING/g' /etc/mopidy/logging.conf
sudo rm /var/log/mopidy/mopidy.log

sudo reboot
~~~

# Upgrade from Version 1.1.1 to 1.1.7

Not much has changed in the core of this version. There is the new feature: Integrating **Spotify** to your Phoniebox. Currently this is *only* a [HOWTO document](docs/SPOTIFY-INTEGRATION.md) which needs improvement and your input. I invite everybody to use our [spotify thread](https://github.com/chbuehlmann/RPi-Jukebox-RFID/issues/18) to post improvements regarding this feature. You might also want to [improve the documentation on *Spotify integration*](docs/SPOTIFY-INTEGRATION.md) and create pull requests so I can merge this with the core.

Upgrading is therefore fairly simple. The following will overwrite any local changes to your code but NOT to your configruation files and systemd services, GPIO and the like. Only core code:

~~~
cd /home/pi/RPi-Jukebox-RFID
git checkout master
git fetch origin
git reset --hard origin/master
git pull
~~~

# Upgrade from Version 1.1.1 to 1.1.6

A few important bug fixes. And a new design. 
And the option to decide what the 'second swipe' of a card does (see settings in the web app).
The following should get you all you need, without running the install script if you
only want to upgrade. 

~~~
cd /home/pi/RPi-Jukebox-RFID
git checkout master
git fetch origin
git reset --hard origin/master
git pull
sudo chown -R pi:www-data /home/pi/RPi-Jukebox-RFID/shared
sudo chmod -R 775 /home/pi/RPi-Jukebox-RFID/shared
sudo chown -R pi:www-data /home/pi/RPi-Jukebox-RFID/htdocs
sudo chmod -R 775 /home/pi/RPi-Jukebox-RFID/htdocs
sudo chown -R pi:www-data /home/pi/RPi-Jukebox-RFID/settings
sudo chmod -R 777 /home/pi/RPi-Jukebox-RFID/settings
sudo cp /home/pi/RPi-Jukebox-RFID/misc/sampleconfigs/phoniebox-rfid-reader.service.stretch-default.sample /etc/systemd/system/phoniebox-rfid-reader.service 
sudo chown root:root /etc/systemd/system/phoniebox-rfid-reader.service
sudo chmod 644 /etc/systemd/system/phoniebox-rfid-reader.service
sudo systemctl enable rfid-reader
~~~

# Upgrade from Version 1.0.0 to 1.1.1

This upgrade brings the web app UI for file management, recursive folder management, wifi switch off and more. The latest [one-line Phoniebox install script](https://github.com/chbuehlmann/RPi-Jukebox-RFID/wiki/CONFIGURE-stretch#oneLineInstall) contains all the necessary steps, but will treat your upgrade like a new install. Manual upgrade:
~~~
cd
cd /home/pi/RPi-Jukebox-RFID
git fetch
git checkout master
git pull
# settings for php.ini to support upload
# make backup
sudo cp /etc/php/7.0/fpm/php.ini /etc/php/7.0/fpm/php.ini.backup
# replace file
sudo cp /home/pi/RPi-Jukebox-RFID/misc/sampleconfigs/php.ini.stretch-default.sample /etc/php/7.0/fpm/php.ini
sudo chown root:root /etc/php/7.0/fpm/php.ini
sudo chmod 644 /etc/php/7.0/fpm/php.ini
sudo service lighttpd force-reload
sudo service php7.0-fpm restart
~~~

# Upgrade to Version 1.0

As of version 1.0 there is a much simpler install procedure: copy and paste one line into your terminal and hit *enter*. Find out more about the [one-line Phoniebox install script](https://github.com/chbuehlmann/RPi-Jukebox-RFID/wiki/CONFIGURE-stretch#oneLineInstall).

# Upgrade from 0.9.5 to 0.9.7
* Adding a *Settings* page in the web app to control features like 'idle shutdown' and 'max volume' and toggle systemd services
* Documentation / troubleshooting / tricks: how to install via ssh, improve on board audio quality and the like
* Adding auto shutdown when idle for longer than x minutes (see [manual](https://github.com/chbuehlmann/RPi-Jukebox-RFID/wiki/MANUAL#settings) for details)
* Adding maximum volume percent to settings (see [manual](https://github.com/chbuehlmann/RPi-Jukebox-RFID/wiki/MANUAL#settings) for details)
* Fixing bug: settings volume for stereo audio iFace
* Fixing bug: bash code compatible with all shells  
* Web app enhancements (audio level, display 'playing now')
~~~
# services to launch after boot using systmed
sudo cp /home/pi/RPi-Jukebox-RFID/misc/sampleconfigs/phoniebox-idle-watchdog.service.sample /etc/systemd/system/phoniebox-idle-watchdog.service
sudo chown root:root /etc/systemd/system/phoniebox-idle-watchdog.service
sudo chmod 644 /etc/systemd/system/phoniebox-idle-watchdog.service
# the config file where you can add the minutes after which Phoniebox shuts down
echo "0" > /home/pi/RPi-Jukebox-RFID/settings/Idle_Time_Before_Shutdown
# enable and start the service
sudo systemctl enable phoniebox-idle-watchdog.service
sudo systemctl start phoniebox-idle-watchdog.service
~~~

# Upgrade from 0.9.4 to 0.9.5
* Configuration of RFID card control in extra file `settings/rfid_trigger_play.conf`
* Playout control config now uses `settings` folder to store iFace value (e.g. PCM) and percentage of relative volume change
* both bash scripts `scripts/rfid_trigger_play.sh` and `scripts/playout_controls.sh` are not created from `.sample` versions anymore, because the config has been moved to external files.

~~~
# make backups of the current scripts
mv /home/pi/RPi-Jukebox-RFID/scripts/rfid_trigger_play.sh /home/pi/RPi-Jukebox-RFID/scripts/rfid_trigger_play.sh.backup.0.9.4
mv /home/pi/RPi-Jukebox-RFID/scripts/playout_controls.sh /home/pi/RPi-Jukebox-RFID/scripts/playout_controls.sh.backup.0.9.4
rm /home/pi/RPi-Jukebox-RFID/scripts/rfid_trigger_play.sh.sample
rm /home/pi/RPi-Jukebox-RFID/scripts/playout_controls.sh.sample
cp /home/pi/RPi-Jukebox-RFID/htdocs/config.php /home/pi/RPi-Jukebox-RFID/htdocs/config.php.backup.0.9.4
# update with git
git checkout master
git pull
# copy config file for RFID chips from sample to "live"
# you need to manually edit the created files and add the values from the backup version of `scripts/rfid_trigger_play.sh`
cp /home/pi/RPi-Jukebox-RFID/settings/rfid_trigger_play.conf.sample /home/pi/RPi-Jukebox-RFID/settings/rfid_trigger_play.conf
sudo chown pi:pi /home/pi/RPi-Jukebox-RFID/settings/rfid_trigger_play.conf
sudo chmod 775 /home/pi/RPi-Jukebox-RFID/settings/rfid_trigger_play.conf
~~~

# Upgrade to 0.9.4
* The following script refers to the OS version 'Stretch' in some places but this should also work for 'Jessie'.
* OS 'Stretch' and 'Jessie' require different `lighttpd.conf` parameters. Samples can be found in `misc/sampleconfigs`
~~~
# make backups of the current scripts
cp /home/pi/RPi-Jukebox-RFID/scripts/rfid_trigger_play.sh /home/pi/RPi-Jukebox-RFID/scripts/rfid_trigger_play.sh.backup.0.9.3
cp /home/pi/RPi-Jukebox-RFID/scripts/playout_controls.sh /home/pi/RPi-Jukebox-RFID/scripts/playout_controls.sh.backup.0.9.3
cp /home/pi/RPi-Jukebox-RFID/htdocs/config.php /home/pi/RPi-Jukebox-RFID/htdocs/config.php.backup.0.9.3
# update with git
git checkout master
git pull
# copy shell script for player
cp /home/pi/RPi-Jukebox-RFID/scripts/rfid_trigger_play.sh.sample /home/pi/RPi-Jukebox-RFID/scripts/rfid_trigger_play.sh
sudo chown pi:pi /home/pi/RPi-Jukebox-RFID/scripts/rfid_trigger_play.sh
sudo chmod 775 /home/pi/RPi-Jukebox-RFID/scripts/rfid_trigger_play.sh
# copy bash script for player controls
cp /home/pi/RPi-Jukebox-RFID/scripts/playout_controls.sh.sample /home/pi/RPi-Jukebox-RFID/scripts/playout_controls.sh
sudo chown pi:pi /home/pi/RPi-Jukebox-RFID/scripts/playout_controls.sh
sudo chmod 775 /home/pi/RPi-Jukebox-RFID/scripts/playout_controls.sh
# create config file for web app from sample
sudo cp /home/pi/RPi-Jukebox-RFID/htdocs/config.php.sample /home/pi/RPi-Jukebox-RFID/htdocs/config.php
# make sure the shared folder is accessible by the web server
sudo chown -R pi:www-data /home/pi/RPi-Jukebox-RFID/shared
sudo chmod -R 775 /home/pi/RPi-Jukebox-RFID/shared
# make sure the htdocs folder can be changed by the web server
sudo chown -R pi:www-data /home/pi/RPi-Jukebox-RFID/htdocs
sudo chmod -R 775 /home/pi/RPi-Jukebox-RFID/htdocs
# services to launch after boot using systmed
sudo cp /home/pi/RPi-Jukebox-RFID/misc/sampleconfigs/phoniebox-rfid-reader.service.stretch-default.sample /etc/systemd/system/phoniebox-rfid-reader.service 
sudo cp /home/pi/RPi-Jukebox-RFID/misc/sampleconfigs/phoniebox-startup-sound.service.stretch-default.sample /etc/systemd/system/phoniebox-startup-sound.service
sudo cp /home/pi/RPi-Jukebox-RFID/misc/sampleconfigs/phoniebox-gpio-buttons.service.stretch-default.sample /etc/systemd/system/phoniebox-gpio-buttons.service
sudo chown root:root /etc/systemd/system/phoniebox-rfid-reader.service
sudo chown root:root /etc/systemd/system/phoniebox-startup-sound.service
sudo chown root:root /etc/systemd/system/phoniebox-gpio-buttons.service
sudo chmod 644 /etc/systemd/system/phoniebox-rfid-reader.service
sudo chmod 644 /etc/systemd/system/phoniebox-startup-sound.service
sudo chmod 644 /etc/systemd/system/phoniebox-gpio-buttons.service
# In case the older version of Phoniebox still uses crontab to start daemon script, UNDO the crontab changes
sudo cp /home/pi/RPi-Jukebox-RFID/misc/sampleconfigs/crontab-pi.UNDO-default.sample /var/spool/cron/crontabs/pi
sudo chown pi:crontab /var/spool/cron/crontabs/pi
sudo chmod 600 /var/spool/cron/crontabs/pi
~~~
