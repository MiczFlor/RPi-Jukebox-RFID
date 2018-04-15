#!/bin/sh
PATHDATA=dirname "$(readlink -f "$0")"
find "$PATHDATA/../shared/audiofolders/$1" -type f | sort -n > "$PATHDATA/../playlists/$1.m3u"
# pipe playlist into VLC
# NOTE: this is being done as sudo, because the webserver does not have the rights to start VLC
sudo cvlc --no-video -I rc --rc-host localhost:4212 "$PATHDATA/../playlists/$1.m3u" > /dev/null 2>/dev/null &
