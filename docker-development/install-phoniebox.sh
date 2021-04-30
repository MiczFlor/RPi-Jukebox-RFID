#!/usr/bin/env bash
DIRaudioFolders="${HOME}/shared/audiofolders"
AUDIOiFace="Master"

pip3 install --no-cache-dir -r ${HOME}/Phoniebox/requirements.txt

# Install Sample config
cp ./misc/sampleconfigs/startupsound.mp3.sample ./shared/startupsound.mp3
cp ./misc/audiofiletype02.wav ./shared/startupsound.wav
cp ./misc/sampleconfigs/shutdownsound.mp3.sample ./shared/shutdownsound.mp3

# Web Server Configuration
local lighthttpd_conf="/etc/lighttpd/lighttpd.conf"
local fastcgi_php_conf="/etc/lighttpd/conf-available/15-fastcgi-php.conf"
local php_ini="/etc/php/7.3/cgi/php.ini"

cp "${HOME}"/misc/sampleconfigs/lighttpd.conf.buster-default.sample "${lighthttpd_conf}"
cp "${HOME}"/misc/sampleconfigs/15-fastcgi-php.conf.buster-default.sample ${fastcgi_php_conf}
cp "${HOME}"/misc/sampleconfigs/php.ini.buster-default.sample ${php_ini}
# cp "${HOME}"/htdocs/config.php.sample "${HOME}"/htdocs/config.php

# MPD Configuration
# local mpd_conf="/etc/mpd.conf"
# chown mpd:audio "${mpd_conf}"
# chmod 640 "${mpd_conf}"
rm -rf /var/lib/apt/lists/* ; \
	mkdir /var/log/mpd/data/ ; \
	mkdir -p /run/mpd/ ; \
	chown -R mpd:audio /var/lib/mpd ; \
	chown -R mpd:audio /run/mpd/ ; \
	chown mpd:audio /etc/mpd.conf ; \
	cp /etc/mpd.conf /etc/mpd.conf.backup

cp "${HOME}"/misc/sampleconfigs/mpd.conf.buster-default.sample /etc/mpd.conf
sed -i 's/%AUDIOiFace%/'"$AUDIOiFace"'/' /etc/mpd.conf
sed -i 's|%DIRaudioFolders%|'"$DIRaudioFolders"'|' /etc/mpd.conf

# Global Configuration
echo "AUDIOFOLDERSPATH=\"${DIRaudioFolders}\"
PLAYLISTSFOLDERPATH=\"${HOME}/playlists\"
SECONDSWIPE=\"RESTART\"
SECONDSWIPEPAUSE=\"2\"
SECONDSWIPEPAUSECONTROLS=\"ON\"
AUDIOIFACENAME=\"${AUDIOiFace}\"
VOLUMEMANAGER=\"mpd\"
AUDIOVOLCHANGESTEP=\"3\"
AUDIOVOLMAXLIMIT=\"70\"
AUDIOVOLMINLIMIT=\"1\"
AUDIOVOLSTARTUP=\"45\"
VOLCHANGEIDLE=\"TRUE\"
IDLETIMESHUTDOWN=\"0\"
POWEROFFCMD=\"sudo poweroff\"
SHOWCOVER=\"ON\"
READWLANIPYN=\"OFF\"
EDITION=\"classic\"
LANG=\"en-UK\"
VERSION=\"2.2 - 305325d - master\"
CMDVOLUP=\"\"
CMDVOLDOWN=\"\"
CMDNEXT=\"\"
CMDPREV=\"\"
CMDREWIND=\"\"
CMDSEEKFORW=\"\"
CMDSEEKBACK=\"\"
" >> "${HOME}"/settings/global.conf

chmod 777 "${HOME}"/settings

mkdir "${HOME}"/playlists
chmod 777 "${HOME}"/playlists