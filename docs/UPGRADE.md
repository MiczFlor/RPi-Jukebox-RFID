
# How to upgrade the Phoniebox code

Assuming that you use `git pull` to update the code base of your Phoniebox,
every now and then you need to run some update scripts, like patches.
To make this somewhat consistent, I started this page to document things that need to be done.

If you still encounter problems after running the below upgrade snippets, check inside the folder `scripts/installscripts/` for scripts which contain the entire install process. 

## Which version am I on?

There is a file `settings/version` containing the version number.

**Note:*** This is work in progress, please share experience, improvements and insights in the [issue section](https://github.com/MiczFlor/RPi-Jukebox-RFID/issues).

# Upgrade from Version 1.1.1 to 1.1.7

Not much has changed in the core of this version. There is the new feature: Integrating **Spotify** to your Phoniebox. Currently this is *only* a [HOWTO document](docs/SPOTIFY-INTEGRATION.md) which needs improvement and your input. I invite everybody to use our [spotify thread](https://github.com/MiczFlor/RPi-Jukebox-RFID/issues/18) to post improvements regarding this feature. You might also want to [improve the documentation on *Spotify integration*](docs/SPOTIFY-INTEGRATION.md) and create pull requests so I can merge this with the core.

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
sudo cp /home/pi/RPi-Jukebox-RFID/misc/sampleconfigs/rfid-reader.service.stretch-default.sample /etc/systemd/system/rfid-reader.service 
sudo chown root:root /etc/systemd/system/rfid-reader.service
sudo chmod 644 /etc/systemd/system/rfid-reader.service
sudo systemctl enable rfid-reader
~~~

# Upgrade from Version 1.0.0 to 1.1.1

This upgrade brings the web app UI for file management, recursive folder management, wifi switch off and more. The latest [one-line Phoniebox install script](INSTALL-stretch.md#oneLineInstall) contains all the necessary steps, but will treat your upgrade like a new install. Manual upgrade:
~~~
cd
cd RPi-Jukebox-RFID
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

As of version 1.0 there is a much simpler install procedure: copy and paste one line into your terminal and hit *enter*. Find out more about the [one-line Phoniebox install script](INSTALL-stretch.md#oneLineInstall).

# Upgrade from 0.9.5 to 0.9.7
* Adding a *Settings* page in the web app to control features like 'idle shutdown' and 'max volume' and toggle systemd services
* Documentation / troubleshooting / tricks: how to install via ssh, improve on board audio quality and the like
* Adding auto shutdown when idle for longer than x minutes (see [manual](MANUAL.md#settings) for details)
* Adding maximum volume percent to settings (see [manual](MANUAL.md#settings) for details)
* Fixing bug: settings volume for stereo audio iFace
* Fixing bug: bash code compatible with all shells  
* Web app enhancements (audio level, display 'playing now')
~~~
# services to launch after boot using systmed
sudo cp /home/pi/RPi-Jukebox-RFID/misc/sampleconfigs/idle-watchdog.service.sample /etc/systemd/system/idle-watchdog.service
sudo chown root:root /etc/systemd/system/idle-watchdog.service
sudo chmod 644 /etc/systemd/system/idle-watchdog.service
# the config file where you can add the minutes after which Phoniebox shuts down
echo "0" > /home/pi/RPi-Jukebox-RFID/settings/Idle_Time_Before_Shutdown
# enable and start the service
sudo systemctl enable idle-watchdog.service
sudo systemctl start idle-watchdog.service
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
sudo cp /home/pi/RPi-Jukebox-RFID/misc/sampleconfigs/rfid-reader.service.stretch-default.sample /etc/systemd/system/rfid-reader.service 
sudo cp /home/pi/RPi-Jukebox-RFID/misc/sampleconfigs/startup-sound.service.stretch-default.sample /etc/systemd/system/startup-sound.service
sudo cp /home/pi/RPi-Jukebox-RFID/misc/sampleconfigs/gpio-buttons.service.stretch-default.sample /etc/systemd/system/gpio-buttons.service
sudo chown root:root /etc/systemd/system/rfid-reader.service
sudo chown root:root /etc/systemd/system/startup-sound.service
sudo chown root:root /etc/systemd/system/gpio-buttons.service
sudo chmod 644 /etc/systemd/system/rfid-reader.service
sudo chmod 644 /etc/systemd/system/startup-sound.service
sudo chmod 644 /etc/systemd/system/gpio-buttons.service
# In case the older version of Phoniebox still uses crontab to start daemon script, UNDO the crontab changes
sudo cp /home/pi/RPi-Jukebox-RFID/misc/sampleconfigs/crontab-pi.UNDO-default.sample /var/spool/cron/crontabs/pi
sudo chown pi:crontab /var/spool/cron/crontabs/pi
sudo chmod 600 /var/spool/cron/crontabs/pi
~~~
