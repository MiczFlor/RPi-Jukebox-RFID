# MPD Configuration
mkdir "${HOME}"/.config/mpd
touch "${HOME}"/.config/mpd/state
mkdir "${INSTALLATION_DIR}"/playlists
cp "${INSTALLATION_DIR}"/misc/sampleconfigs/mpd.conf.buster-docker-dev.sample "${HOME}"/.config/mpd/mpd.conf
# Start mpd and mpc
[ ! -s ~/.config/mpd/pid ] && mpd --stdout "${HOME}"/.config/mpd/mpd.conf
mpc update

# Start Phoniebox backbone
python ${INSTALLATION_DIR}/Phoniebox/PhonieboxDaemon.py

# Start Phoniebox UI
lighttpd-enable-mod fastcgi
lighttpd-enable-mod fastcgi-php
service lighttpd start
