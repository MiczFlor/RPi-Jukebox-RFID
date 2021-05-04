#!/usr/bin/env bash
DIRaudioFolders="${INSTALLATION_DIR}/shared/audiofolders"
AUDIOiFace="Master"

pip3 install --no-cache-dir -r ${INSTALLATION_DIR}/Phoniebox/requirements.txt

# Install Sample config
cp ./misc/sampleconfigs/startupsound.mp3.sample ./shared/startupsound.mp3
cp ./misc/audiofiletype02.wav ./shared/startupsound.wav
cp ./misc/sampleconfigs/shutdownsound.mp3.sample ./shared/shutdownsound.mp3


# Web Server Configuration
cp ${INSTALLATION_DIR}/misc/sampleconfigs/lighttpd.conf.buster-default.sample /etc/lighttpd/lighttpd.conf
cp ${INSTALLATION_DIR}/misc/sampleconfigs/15-fastcgi-php.conf.buster-default.sample /etc/lighttpd/conf-available/15-fastcgi-php.conf
cp ${INSTALLATION_DIR}/misc/sampleconfigs/php.ini.buster-default.sample /etc/php/7.3/cgi/php.ini
mkdir ${INSTALLATION_DIR}/htdocs
chown -R root:www-data ${INSTALLATION_DIR}/htdocs
chmod -R 750 ${INSTALLATION_DIR}/htdocs

# Global Configuration
echo "AUDIOFOLDERSPATH=\"${DIRaudioFolders}\"
PLAYLISTSFOLDERPATH=\"${INSTALLATION_DIR}/playlists\"
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
" >> "${INSTALLATION_DIR}"/settings/global.conf
