#!/bin/sh
# kill vlc if running
# NOTE: this is being done as sudo, because the webserver does not have the rights to kill VLC
sudo pkill vlc > /dev/null 2>/dev/null
