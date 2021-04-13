#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from mpd import MPDClient

class player_control:
    def __init__(self,music_player_status,volume_control=None):
        self.volume_control = volume_control
        self.music_player_status = music_player_status
        if not self.music_player_status:
            self.music_player_status['player_status'] = {}
            self.music_player_status['audio_folder_status'] = {}
            self.music_player_status.save_to_json()

        self.mpd_client = MPDClient()               # create client object
        self.mpd_client.timeout = 0.5               # network timeout in seconds (floats allowed), default: None
        self.mpd_client.idletimeout = 0.5           # timeout for fetching the result of the idle command is handled seperately, default: None
        self.connect()
        print("Connected to MPD Version: "+self.mpd_client.mpd_version)

    def connect(self):
        self.mpd_client.connect("localhost", 6600)  # connect to localhost:6600
    
    def mpd_retry(self,mpd_cmd,params=None):
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
        
        if param is not None and isinstance(param, dict):
            songid = param.get("songid")
            if songid is None:
                songid = 1
        else:
            songid = 1

        try:
            self.mpd_client.play(songid)
        except ConnectionError: 
            print ("MPD Connection Error, retry")
            self.conncet()
            self.mpd_client.play(songid)
        except  Exception as e:
            print(e)
        song = self.mpd_client.currentsong()
        return ({})
        
    def stop(self,param):
        self.mpd_client.stop()
        return ({})

    def pause(self, param):
        self.mpd_client.pause(1)
        return ({})

    def prev(self, param):
        self.mpd_client.previous()
        return ({})

    def next(self, param):
        self.mpd_client.next()
        return ({})

    def seek(self, param):
        val = param.get('time')
        if val is not None:
            self.mpd_client.seekcur(val)
        return ({})

    def get_current_song(self, param):
        return {'resp': self.mpd_client.currentsong()}

    def map_filename_to_playlist_pos(self,filename):
        print ("map_filename_to_playlist_pos not yet implemented")
        #self.mpd_client.playlistfind()
        return 0
    
    def remove(self, param):
        print ("remove not yet implemented")
        return ({})

    def move(self, param):
        song_id = param.get("song_id")
        step = param.get("step")
        #MPDClient.playlistmove(name, from, to)
        #MPDClient.swapid(song1, song2)

        print ("move not yet implemented")
        return ({})

    def playsingle(self, param):
        print ("playsingle not yet implemented")
        return ({})    
    
    def playlistaddplay(self, param):
        
            # add to playlist (and play)
        # this command clears the playlist, loads a new playlist and plays it. It also handles the resume play feature.
        # FOLDER = rel path from audiofolders
        # VALUE = name of playlist

        # NEW VERSION:
        # Read the current config file (include will execute == read)
        #. "$AUDIOFOLDERSPATH/$FOLDER/folder.conf"

        folder = param.get("folder")

        print("playing folder: {}".format(folder))

        if folder is not None:
            # load playlist
            #mpc clear
            self.mpd_client.clear()
            #mpc load "${VALUE//\//SLASH}"   
            #why dealing with playlists? at least partially redundant with folder.config, so why not combine if needed
            #alternative solution, just add folders recursively to quene
            self.mpd_client.add(folder)

            self.music_player_status['player_status']['last_played_folder'] = folder

            current_status = self.music_player_status['audio_folder_status'].get(folder)
            if current_status is None:
                current_status = self.music_player_status['audio_folder_status'][folder] = {}

            self.mpd_client.play()
       
        
        if 0:
        # Change some settings according to current folder IF the folder.conf exists
        #. ${PATHDATA}/inc.settingsFolderSpecific.sh

        # check if we switch to single file playout
        ##${PATHDATA}/single_play.sh -c=single_check -d="${FOLDER}" 

            #single_check)
            #Check if SINGLE is switched on. As this is called for each playlist change, it will overwrite temporary shuffle mode
            #if [ $SINGLE == "ON" ]
            #then
              #  mpc single on
            #else
              #  mpc single off
            #fi
        
            if currecnt_status["SINGLE"] == "OFF":
                self.mpd_client.single(0)
            else:
                self.mpd_client.single(1)
        
        # check if we shuffle the playlist
        #${PATHDATA}/shuffle_play.sh -c=shuffle_check -d="${FOLDER}"
            #shuffle_check)
            ##Check if SHUFFLE is switched on. As this is called for each playlist change, it will overwrite temporary shuffle mode
	        #if [ $SHUFFLE == "ON" ];
	        #then 
	        #	mpc shuffle
	        #else
	        #	mpc random off
	        #fi
            #;;    def playerstop(self,param):

            if currecnt_status["SHUFFLE"] == "OFF":
                self.mpd_client.random(0)
            else:
                self.mpd_client.shuffle()

        ## oh, player controls volume
        #need a setter for mute/unmute from volume class

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
        #${PATHDATA}/resume_play.sh -c=resume -d="${FOLDER}" 
    
        ## Check if RESUME is switched on
        #if [ $RESUME == "ON" ] || [ $SINGLE == "ON" ];
        #then
        #   
        #    # Check if we got a "savepos" command after the last "resume". Otherwise we assume that the playlist was played until the end.
        #    # In this case, start the playlist from beginning 
        #    if [ $PLAYSTATUS == "Stopped" ] 
        #    then
        #        # Get the playlist position of the file from mpd
        #        # Alternative approach: "mpc searchplay xx && mpc seek yy" 
        #        PLAYLISTPOS=$(echo -e playlistfind filename \"$CURRENTFILENAME\"\\nclose | nc -w 1 localhost 6600 | grep -o -P '(?<=Pos: ).*')
        #        
        #        # If the file is found, it is played from ELAPSED, otherwise start playlist from beginning. If we got a playlist position
        #        # play from that position, not the saved one.
        #        if [ ! -z $PLAYLISTPOS ] && [ -z $VALUE ] ;
        #        then
        #            # doesnt work correctly 
        #            # echo -e seek $PLAYLISTPOS $ELAPSED \\nclose | nc -w 1 localhost 6600
        #            # workaround, see https://github.com/MiczFlor/RPi-Jukebox-RFID/issues/878#issuecomment-672283454
        #            echo -e "play $PLAYLISTPOS" | nc -w 1 localhost 6600
        #            echo -e seekcur $ELAPSED \\nclose | nc -w 1 localhost 6600
        #        else
        #            echo -e "play $VALUE" | nc -w 1 localhost 6600
        #        fi
        #        # If the playlist ends without any stop/shutdown/new swipe (you've listened to all of the tracks), 
        #        # there's no savepos event and we would resume at the last position anywhere in the playlist. 
        #        # To catch these, we signal it to the next "resume" call via writing it to folder.conf that 
        #        # we still assume that the audio is playing. 
        #        # be anything here, as we won't use the information if "Playing" is found by "resume".
        #        
        #        # set the vars we need to change
        #        PLAYSTATUS="Playing"
        #        
        #    else
        #        # We assume that the playlist ran to the end the last time and start from the beginning.
        #        # Or: playlist is playing and we've got a play from playlist position command.
        #        echo -e "play $VALUE" | nc -w 1 localhost 6600
        #    fi
        #else
        #    # if no last played data exists (resume play disabled), we play the playlist from the beginning or the given playlist position
        #    echo -e "play $VALUE" | nc -w 1 localhost 6600
        #fi

            if currecnt_status["RESUME"] is not "OFF" or currecnt_status["SINGLE"] is not "OFF":
                if currecnt_status["PLAYSTATUS"] is "Stopped":

                    self.map_filename_to_playlist_pos()

                    #PLAYLISTPOS=$(echo -e playlistfind filename \"$CURRENTFILENAME\"\\nclose | nc -w 1 localhost 6600 | grep -o -P '(?<=Pos: ).*')

                    currecnt_status["PLAYSTATUS"] = "Playing"
                else:
                    self.mpd_client.play()  # what is in value here? songpos
            else:
                #Begins playing the playlist at song number SONGPOS.
                self.mpd_client.play()  # what is in value here? songpos

        # write latest folder played to settings file
        #sudo echo ${FOLDER} > ${PATHDATA}/../settings/Latest_Folder_Played

        song = self.mpd_client.currentsong()
        
        current_status["CURRENTFILENAME"] = song.get('file')
        current_status["ELAPSED"] = 0
        current_status["PLAYSTATUS"] = "Stopped"
        current_status["RESUME"] = "OFF"
        current_status["SHUFFLE"] = "OFF"
        current_status["LOOP"] = "OFF"
        current_status["SINGLE"] = "OFF"

        return ({'song':song})

    def playerstatus(self,param):
        status = self.mpd_client.currentsong()
        status.update(self.mpd_client.status())
        status['volume'] = self.volume_control.volume

        #for k in status:
        #    print ("{} : {}".format(k,status.get(k)))
        return (status)

    def playlistinfo(self,param):
        playlistinfo = (self.mpd_client.playlistinfo())
        return (playlistinfo)
