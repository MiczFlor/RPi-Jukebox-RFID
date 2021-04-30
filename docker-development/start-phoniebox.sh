# /usr/bin/mpd --stdout /etc/mpd.conf

lighttpd-enable-mod fastcgi
lighttpd-enable-mod fastcgi-php

python ${HOME}/Phoniebox/PhonieboxDaemon.py
service lighttpd start