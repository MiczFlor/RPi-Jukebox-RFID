#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from mpd import MPDClient

class player_control:
    def __init__(self):
        self.mpd_client = MPDClient()               # create client object
        self.mpd_client.timeout = 0.5               # network timeout in seconds (floats allowed), default: None
        self.mpd_client.idletimeout = 0.5           # timeout for fetching the result of the idle command is handled seperately, default: None
        self.connect()
        print("Connected to MPD Version: "+self.mpd_client.mpd_version)

    def connect(self):
        self.mpd_client.connect("localhost", 6600)  # connect to localhost:6600
    
    def _mpd_retry(self,mpd_cmd,params=None):
        try:
            ret = mpd_cmd(params)
        except ConnectionError: 
            print ("MPD Connection Error, retry")
            self.conncet()
            ret = mpd_cmd(params)
        except  Exception as e:
            print(e)
        return ret

    def get_player_type_and_version(self, param):
        return ({'result':'mpd','version':self.mpd_client.mpd_version})
    
    def play(self, param):
        try:
            self.mpd_client.play()
        except ConnectionError: 
            print ("MPD Connection Error, retry")
            self.conncet()
            self.mpd_client.play()
        except  Exception as e:
            print(e)
        song = self.mpd_client.currentsong()
        return ({'song':song})
        
    def get_current_song(self, param):
        return {'resp': self.mpd_client.currentsong()}

    def playlistaddplay(self, param):
        
            # add to playlist (and play)
        # this command clears the playlist, loads a new playlist and plays it. It also handles the resume play feature.
        # FOLDER = rel path from audiofolders
        # VALUE = name of playlist

        # NEW VERSION:
        # Read the current config file (include will execute == read)
        #. "$AUDIOFOLDERSPATH/$FOLDER/folder.conf"

        # load playlist
        #mpc clear
        #mpc load "${VALUE//\//SLASH}"
        #if [ "${DEBUG_playout_controls_sh}" == "TRUE" ]; then echo "mpc load "${VALUE//\//SLASH} >> ${PATHDATA}/../logs/debug.log; fi

        # Change some settings according to current folder IF the folder.conf exists
        #. ${PATHDATA}/inc.settingsFolderSpecific.sh

        # check if we switch to single file playout
        #${PATHDATA}/single_play.sh -c=single_check -d="${FOLDER}"

        # check if we shuffle the playlist
        #${PATHDATA}/shuffle_play.sh -c=shuffle_check -d="${FOLDER}"

        # Unmute if muted
        #if [ -f $VOLFILE ]; then
            # $VOLFILE DOES exist == audio off
            # read volume level from $VOLFILE and set as percent
         #   echo -e setvol `<$VOLFILE`\\nclose | nc -w 1 localhost 6600
            # volume handling alternative with amixer not mpd (2020-06-12 related to ticket #973)
            # amixer sset \'$AUDIOIFACENAME\' `<$VOLFILE`%
            # delete $VOLFILE
          #  rm -f $VOLFILE
        #fi

        # Now load and play
        #if [ "${DEBUG_playout_controls_sh}" == "TRUE" ]; then echo "mpc load "${VALUE//\//SLASH}" && ${PATHDATA}/resume_play.sh -c=resume -d="${FOLDER}"" >> ${PATHDATA}/../logs/debug.log; fi
        #${PATHDATA}/resume_play.sh -c=resume -d="${FOLDER}"

        # write latest folder played to settings file
        #sudo echo ${FOLDER} > ${PATHDATA}/../settings/Latest_Folder_Played
        #sudo chown pi:www-data ${PATHDATA}/../settings/Latest_Folder_Played
        #sudo chmod 777 ${PATHDATA}/../settings/Latest_Folder_Played
    
        self.mpd_client.add(uri)
        self.mpd_client.load(name[123, start:end])
    
        song = self.mpd_client.currentsong()
        return ({'song':song})