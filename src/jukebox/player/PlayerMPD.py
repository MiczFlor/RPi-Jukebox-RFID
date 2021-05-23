#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import mpd
import threading
import logging
import time

logger = logging.getLogger('jb.PlayerMPD')


class player_control:
    def __init__(self, mpd_host, music_player_status, volume_control=None):
        self.mpd_host = mpd_host
        self.volume_control = volume_control
        self.music_player_status = music_player_status

        self.mpd_client = mpd.MPDClient()
        self.mpd_client.timeout = 0.5               # network timeout in seconds (floats allowed), default: None
        self.mpd_client.idletimeout = 0.5           # timeout for fetching the result of the idle command
        self.connect()
        logger.info(f"Connected to MPD Version: {self.mpd_client.mpd_version}")

        if not self.music_player_status:
            self.music_player_status['player_status'] = {}
            self.music_player_status['audio_folder_status'] = {}
            self.music_player_status.save_to_json()
            self.current_folder_status = {}
        else:
            last_played_folder = self.music_player_status['player_status']['last_played_folder']
            if last_played_folder is not None:
                self.current_folder_status = self.music_player_status['audio_folder_status'][last_played_folder]
                self.mpd_client.clear()
                self.mpd_client.add(last_played_folder)
                logger.info(f"Last Played Folder: {last_played_folder}")

        self.old_song = None
        self.mpd_status = {}
        self.mpd_status_poll_interval = 0.25
        self.mpd_mutex = threading.Lock()
        self.status_thread = threading.Timer(self.mpd_status_poll_interval, self._mpd_status_poll).start()

    def connect(self):
        self.mpd_client.connect(self.mpd_host, 6600)

    def mpd_retry_with_mutex(self, mpd_cmd, params=None):
        '''
        This method adds thread saftey for acceses to mpd via a mutex lock,
        it shall be used for each access to mpd to ensure thread safety
        In case of a communication error the connection will be reestablished and the pending command will be repeated 2 times
        '''
        retry = 2
        with self.mpd_mutex:
            while retry:
                try:
                    if params is None:
                        ret = mpd_cmd()
                    else:
                        ret = mpd_cmd(params)
                    break
                except ConnectionError:     # TODO: this is not working properly yet, we are alwas anding up in the Exception!
                    logger.info(f"MPD Connection Error, retry {retry}")
                    self.connect()
                    retry -= 1
                except Exception as e:
                    if retry:
                        retry -= 1
                        self.connect()      # TODO: Workaround, since the above ConnectionError is not properly caught
                        logger.info(f"MPD Error, retry {retry}")
                        logger.info(f"{e.__class__}")
                        logger.info(f"{e}")
                    else:
                        logger.error(f"{e}")
                        ret = {}
                        break
            return ret

    def _mpd_status_poll(self):
        '''
        this method polls the status from mpd and stores the important inforamtion in the music_player_status,
        it will repeat itself in the intervall specified by self.mpd_status_poll_interval
        '''
        self.mpd_status.update(self.mpd_retry_with_mutex(self.mpd_client.status))

        # get song name just if the song has changed
        if self.mpd_status.get('song') != self.old_song:
            self.mpd_status.update(self.mpd_retry_with_mutex(self.mpd_client.currentsong))
            self.old_song = self.mpd_status['song']

        self.mpd_status['volume'] = self.volume_control.volume

        if self.mpd_status.get('elapsed') is not None:
            self.current_folder_status["ELAPSED"] = self.mpd_status['elapsed']
            self.music_player_status['player_status']["CURRENTSONGPOS"] = self.mpd_status['song']
            self.music_player_status['player_status']["CURRENTFILENAME"] = self.mpd_status['file']

        # the repetation is intentionally at the end, to avoid overruns in case of delays caused by communication
        self.status_thread = threading.Timer(self.mpd_status_poll_interval, self._mpd_status_poll).start()
        return ()

    def get_player_type_and_version(self, param):
        return ({'result': 'mpd', 'version': self.mpd_retry_with_mutex(self.mpd_client.mpd_version)})

    def play(self, param):
        if param is not None and isinstance(param, dict):
            songid = param.get("songid")
            if songid is None:
                songid = 0
        else:
            songid = 0

        if songid == 0:
            self.mpd_retry_with_mutex(self.mpd_client.play)
        else: 
            self.mpd_retry_with_mutex(self.mpd_client.play, songid)

        song = self.mpd_client.currentsong()

        return ({'object': 'player', 'method': 'play', 'params': song})

    def stop(self, param):
        self.mpd_retry_with_mutex(self.mpd_client.stop)
        song = self.mpd_client.currentsong()

        return ({'object': 'player', 'method': 'stop', 'params': song})

    def pause(self, param):
        self.mpd_retry_with_mutex(self.mpd_client.pause, 1)
        song = self.mpd_client.currentsong()
        
        return ({'object': 'player', 'method': 'pause', 'params': song})

    def prev(self, param):
        self.mpd_retry_with_mutex(self.mpd_client.previous)
        song = self.mpd_client.currentsong()
        
        return ({'object': 'player', 'method': 'prev', 'params': song})

    def next(self, param):
        self.mpd_retry_with_mutex(self.mpd_client.next)
        song = self.mpd_client.currentsong()
        
        return ({'object': 'player', 'method': 'next', 'params': song})

    def seek(self, param):
        val = param.get('time')
        if val is not None:
            self.mpd_retry_with_mutex(self.mpd_client.seekcur, val)
        return ({})

    def replay(self, param):
        return ({})

    def repeatmode(self, param):
        if param is not None and isinstance(param, dict):
            mode = param.get("mode")

            if mode == 'repeat':
                repeat = 1
                single = 0
            elif mode == 'single':
                repeat = 1
                single = 1
            else:
                repeat = 0
                single = 0

            self.mpd_retry_with_mutex(self.mpd_client.repeat, repeat)
            self.mpd_retry_with_mutex(self.mpd_client.single, single)
        return ({})

    def get_current_song(self, param):
        return {'resp': self.mpd_retry_with_mutex(self.mpd_client.currentsong)}

    def map_filename_to_playlist_pos(self, filename):
        logger.error("map_filename_to_playlist_pos not yet implemented")
        # self.mpd_client.playlistfind()
        return 0

    def remove(self, param):
        logger.error("remove not yet implemented")
        return ({})

    def move(self, param):
        # song_id = param.get("song_id")
        # step = param.get("step")
        # MPDClient.playlistmove(name, from, to)
        # MPDClient.swapid(song1, song2)

        logger.error("move not yet implemented")
        return ({})

    def test_mutex(self, param):
        self.mpd_mutex.acquire()
        time.sleep(1)
        self.mpd_mutex.release()

    def playsingle(self, param):
        logger.error("playsingle not yet implemented")
        return ({})

    def playlistaddplay(self, param):
        # add to playlist (and play)
        # this command clears the playlist, loads a new playlist and plays it. It also handles the resume play feature.
        # FOLDER = rel path from audiofolders
        # VALUE = name of playlist

        # NEW VERSION:
        # Read the current config file (include will execute == read)
        # . "$AUDIOFOLDERSPATH/$FOLDER/folder.conf"

        folder = param.get("folder")

        logger.info(f"playing folder: {folder}")

        if folder is not None:
            # load playlist
            self.mpd_retry_with_mutex(self.mpd_client.clear)

            # TODO: why dealing with playlists? at least partially redundant with folder.config,
            # so why not combine if needed alternative solution, just add folders recursively to quene
            self.mpd_retry_with_mutex(self.mpd_client.add, folder)

            self.music_player_status['player_status']['last_played_folder'] = folder

            self.current_folder_status = self.music_player_status['audio_folder_status'].get(folder)
            if self.current_folder_status is None:
                self.current_folder_status = self.music_player_status['audio_folder_status'][folder] = {}

            self.mpd_retry_with_mutex(self.mpd_client.play)

        if 0:
            # Change some settings according to current folder IF the folder.conf exists
            # . ${PATHDATA}/inc.settingsFolderSpecific.sh

            # check if we switch to single file playout
            # #${PATHDATA}/single_play.sh -c=single_check -d="${FOLDER}"

            # single_check)
            # Check if SINGLE is switched on. As this is called for each playlist change,
            # it will overwrite temporary shuffle mode
            # if [ $SINGLE == "ON" ]
            # then
            # mpc single on
            # else
            #  mpc single off
            # fi

            if self.current_folder_status["SINGLE"] == "OFF":
                self.mpd_client.single(0)
            else:
                self.mpd_client.single(1)

            # check if we shuffle the playlist
            # ${PATHDATA}/shuffle_play.sh -c=shuffle_check -d="${FOLDER}"
            # shuffle_check)
            # #Check if SHUFFLE is switched on. As this is called for each playlist change,
            # it will overwrite temporary shuffle mode
            # if [ $SHUFFLE == "ON" ];
            # then
            #   mpc shuffle
            # else
            #   mpc random off
            # fi

            if self.current_folder_status["SHUFFLE"] == "OFF":
                self.mpd_client.random(0)
            else:
                self.mpd_client.shuffle()

            # TODO: player controls volume
            # need a setter for mute/unmute from volume class?

            # Unmute if muted
            # if [ -f $VOLFILE ]; then
            #   $VOLFILE DOES exist == audio off
            #  read volume level from $VOLFILE and set as percent
            #   echo -e setvol `<$VOLFILE`\\nclose | nc -w 1 localhost 6600
            # volume handling alternative with amixer not mpd (2020-06-12 related to ticket #973)
            # amixer sset \'$AUDIOIFACENAME\' `<$VOLFILE`%
            # delete $VOLFILE
            #  rm -f $VOLFILE
            # fi

            # Now load and play
            # ${PATHDATA}/resume_play.sh -c=resume -d="${FOLDER}"

            # # Check if RESUME is switched on
            # if [ $RESUME == "ON" ] || [ $SINGLE == "ON" ];
            # then
            #
            #    # Check if we got a "savepos" command after the last "resume".
            #      Otherwise we assume that the playlist was played until the end.
            #    # In this case, start the playlist from beginning
            #    if [ $PLAYSTATUS == "Stopped" ]
            #    then
            #        # Get the playlist position of the file from mpd
            #        # Alternative approach: "mpc searchplay xx && mpc seek yy"
            #        PLAYLISTPOS=$(echo -e playlistfind filename \"$CURRENTFILENAME\"\\nclose |
            #                                            nc -w 1 localhost 6600 | grep -o -P '(?<=Pos: ).*')
            #
            #        # If the file is found, it is played from ELAPSED, otherwise start playlist from beginning.
            #          If we got a playlist position
            #        # play from that position, not the saved one.
            #        if [ ! -z $PLAYLISTPOS ] && [ -z $VALUE ] ;
            #        then
            #            # doesnt work correctly
            #            # echo -e seek $PLAYLISTPOS $ELAPSED \\nclose | nc -w 1 localhost 6600
            #            # workaround, see https://github.com/MiczFlor/RPi-Jukebox-RFID/issues/878#issuecomment
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
            # else
            #    # if no last played data exists (resume play disabled),
            #    we play the playlist from the beginning or the given playlist position
            #    echo -e "play $VALUE" | nc -w 1 localhost 6600
            # fi

            if self.current_folder_status["RESUME"] != "OFF" or self.current_folder_status["SINGLE"] != "OFF":
                if self.current_folder_status["PLAYSTATUS"] == "Stopped":

                    self.map_filename_to_playlist_pos()

                    # PLAYLISTPOS=$(echo -e playlistfind filename \"$CURRENTFILENAME\"\\nclose |
                    #          nc -w 1 localhost 6600 | grep -o -P '(?<=Pos: ).*')

                    self.current_folder_status["PLAYSTATUS"] = "Playing"
                else:
                    self.mpd_client.play()  # what is in value here? songpos
            else:
                # Begins playing the playlist at song number SONGPOS.
                self.mpd_client.play()  # what is in value here? songpos

        # write latest folder played to settings file
        # sudo echo ${FOLDER} > ${PATHDATA}/../settings/Latest_Folder_Played

        song = self.mpd_retry_with_mutex(self.mpd_client.currentsong)

        self.current_folder_status["CURRENTFILENAME"] = song.get('file')
        self.current_folder_status["ELAPSED"] = 0
        self.current_folder_status["PLAYSTATUS"] = "Stopped"
        self.current_folder_status["RESUME"] = "OFF"
        self.current_folder_status["SHUFFLE"] = "OFF"
        self.current_folder_status["LOOP"] = "OFF"
        self.current_folder_status["SINGLE"] = "OFF"

        return ({'object': 'player', 'method': 'playlistaddplay', 'params': song})

    def playerstatus(self, param):
        status = self.mpd_status
        
        return ({'object': 'player', 'method': 'playerstatus', 'params': status})

    def playlistinfo(self, param):
        playlistinfo = (self.mpd_retry_with_mutex(self.mpd_client.playlistinfo))
        return ({'object': 'player', 'method': 'playlistinfo', 'params': playlistinfo})
