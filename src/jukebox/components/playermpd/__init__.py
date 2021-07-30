# -*- coding: utf-8 -*-
"""
Package for interfacing with the MPD Music Player Daemon
"""
import mpd
import threading
import logging
import time
import jukebox.cfghandler
import jukebox.plugs as plugs
from jukebox.NvManager import nv_manager
import jukebox.pubsub as pubsub

logger = logging.getLogger('jb.PlayerMPD')
cfg = jukebox.cfghandler.get_handler('jukebox')


class PlayerMPD:
    """Interface to MPD Music Player Daemon"""

    def __init__(self):
        self.nvm = nv_manager()
        self.pubsubserver = pubsub.get_publisher()
        self.mpd_host = cfg.getn('playermpd', 'host')
        self.music_player_status = self.nvm.load(cfg.getn('playermpd', 'status_file'))

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
            last_played_folder = self.music_player_status['player_status'].get('last_played_folder')
            if last_played_folder is not None:
                self.current_folder_status = self.music_player_status['audio_folder_status'][last_played_folder]
                self.mpd_client.clear()
                self.mpd_client.add(last_played_folder)
                logger.info(f"Last Played Folder: {last_played_folder}")

        self.old_song = None
        self.mpd_status = {}
        self.mpd_status_poll_interval = 0.25
        self.mpd_mutex = threading.Lock()
        self.status_is_closing = False
        self.status_thread = threading.Timer(self.mpd_status_poll_interval, self._mpd_status_poll).start()

    def exit(self):
        logger.debug("Exit routine of playermpd started")
        self.status_is_closing = True
        # Need to make sure we are not in the process of a status poll
        # This currently causes 250 ms delay in shutdown (which otherwise takes 6 ms)
        # --> Change it (self.status_thread.cancel() ?)
        time.sleep(self.mpd_status_poll_interval)
        # self.status_thread.cancel()
        self.mpd_client.disconnect()
        self.nvm.save_all()

    def connect(self):
        self.mpd_client.connect(self.mpd_host, 6600)

    def mpd_retry_with_mutex(self, mpd_cmd, param1=None, param2=None):
        """
        This method adds thread saftey for acceses to mpd via a mutex lock,
        it shall be used for each access to mpd to ensure thread safety
        In case of a communication error the connection will be reestablished and the pending command will be repeated 2 times

        I think this should be refactored to a decorator
        """
        retry = 2
        with self.mpd_mutex:
            while retry:
                try:
                    if param2 is not None:
                        ret = mpd_cmd(param1, param2)
                    elif param1 is not None:
                        ret = mpd_cmd(param1)
                    else:
                        ret = mpd_cmd()
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
        """
        this method polls the status from mpd and stores the important inforamtion in the music_player_status,
        it will repeat itself in the intervall specified by self.mpd_status_poll_interval
        """
        self.mpd_status.update(self.mpd_retry_with_mutex(self.mpd_client.status))

        # get song name just if the song has changed
        if self.mpd_status.get('song') != self.old_song:
            self.mpd_status.update(self.mpd_retry_with_mutex(self.mpd_client.currentsong))
            self.old_song = self.mpd_status['song']

        # This will log all plugin calls in logger and spams the debug messages which might be needed to debug actual issues:
        # self.mpd_status['volume'] = plugs.call_ignore_errors('volume', 'ctrl', 'get_volume')
        # Do the same, but prevent the debug logging:
        try:
            self.mpd_status['volume'] = plugs.get('volume', 'ctrl').get_volume()
        except Exception as e:
            pass

        if self.mpd_status.get('elapsed') is not None:
            self.current_folder_status["ELAPSED"] = self.mpd_status['elapsed']
            self.music_player_status['player_status']["CURRENTSONGPOS"] = self.mpd_status['song']
            self.music_player_status['player_status']["CURRENTFILENAME"] = self.mpd_status['file']

        if self.mpd_status.get('file') is not None:
            self.current_folder_status["CURRENTFILENAME"] = self.mpd_status['file']
            self.current_folder_status["CURRENTSONGPOS"] = self.mpd_status['song']
            self.current_folder_status["ELAPSED"] = self.mpd_status['elapsed']
            self.current_folder_status["PLAYSTATUS"] = self.mpd_status['state']
            self.current_folder_status["RESUME"] = "OFF"
            self.current_folder_status["SHUFFLE"] = "OFF"
            self.current_folder_status["LOOP"] = "OFF"
            self.current_folder_status["SINGLE"] = "OFF"
        # the repetation is intentionally at the end, to avoid overruns in case of delays caused by communication
        self.pubsubserver.publish('playerstatus', self.mpd_status)
        if self.status_is_closing is False:
            self.status_thread = threading.Timer(self.mpd_status_poll_interval, self._mpd_status_poll).start()

    @plugs.tag
    def get_player_type_and_version(self):
        return self.mpd_retry_with_mutex(self.mpd_client.mpd_version)

    @plugs.tag
    def play(self, songid=None):
        if songid is None:
            songid = 0

        if songid == 0:
            self.mpd_retry_with_mutex(self.mpd_client.play)
        else:
            self.mpd_retry_with_mutex(self.mpd_client.play, songid)

        status = self.mpd_status

        return status

    @plugs.tag
    def stop(self):
        self.mpd_retry_with_mutex(self.mpd_client.stop)

        status = self.mpd_status

        return status

    @plugs.tag
    def pause(self):
        self.mpd_retry_with_mutex(self.mpd_client.pause, 1)

        status = self.mpd_status

        return status

    @plugs.tag
    def prev(self):
        self.mpd_retry_with_mutex(self.mpd_client.previous)
        return self.mpd_status

    @plugs.tag
    def next(self):
        self.mpd_retry_with_mutex(self.mpd_client.next)
        return self.mpd_status

    @plugs.tag
    def seek(self, new_time):
        if new_time is not None:
            self.mpd_retry_with_mutex(self.mpd_client.seekcur, new_time)
        return self.mpd_status

    @plugs.tag
    def shuffle(self, random):
        self.mpd_retry_with_mutex(self.mpd_client.random, 1 if random else 0)

        return self.mpd_status

    @plugs.tag
    def repeatmode(self, mode):
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

        return self.mpd_status

    @plugs.tag
    def get_current_song(self, param):
        return self.mpd_status

    @plugs.tag
    def map_filename_to_playlist_pos(self, filename):
        # self.mpd_client.playlistfind()
        raise NotImplementedError

    @plugs.tag
    def remove(self):
        raise NotImplementedError

    @plugs.tag
    def move(self):
        # song_id = param.get("song_id")
        # step = param.get("step")
        # MPDClient.playlistmove(name, from, to)
        # MPDClient.swapid(song1, song2)
        raise NotImplementedError

    def test_mutex(self, delay):
        self.mpd_mutex.acquire()
        time.sleep(delay)
        self.mpd_mutex.release()

    @plugs.tag
    def playsingle(self):
        raise NotImplementedError

    @plugs.tag
    def resume(self):
        songpos = self.current_folder_status["CURRENTSONGPOS"]
        elapsed = self.current_folder_status["ELAPSED"]
        self.mpd_retry_with_mutex(self.mpd_client.seek, songpos, elapsed)
        self.mpd_retry_with_mutex(self.mpd_client.play)

    @plugs.tag
    def playlistaddplay(self, folder):
        # add to playlist (and play)
        # this command clears the playlist, loads a new playlist and plays it. It also handles the resume play feature.
        logger.info(f"playing folder: {folder}")
        self.mpd_retry_with_mutex(self.mpd_client.clear)

        if folder is not None:
            # TODO: why dealing with playlists? at least partially redundant with folder.config,
            # so why not combine if needed alternative solution, just add folders recursively to quene
            self.mpd_retry_with_mutex(self.mpd_client.add, folder)

            self.music_player_status['player_status']['last_played_folder'] = folder

            self.current_folder_status = self.music_player_status['audio_folder_status'].get(folder)
            if self.current_folder_status is None:
                self.current_folder_status = self.music_player_status['audio_folder_status'][folder] = {}

            self.mpd_retry_with_mutex(self.mpd_client.play)

        return self.mpd_status

    @plugs.tag
    def playerstatus(self):
        return self.mpd_status

    @plugs.tag
    def playlistinfo(self):
        playlistinfo = (self.mpd_retry_with_mutex(self.mpd_client.playlistinfo))
        return playlistinfo

    # Attention: MPD.listal will consume a lot of memory with large libs.. should be refactored at some point
    @plugs.tag
    def list_all_dirs(self):
        result = self.mpd_retry_with_mutex(self.mpd_client.listall)
        # list = [entry for entry in list if 'directory' in entry]
        return result

    @plugs.tag
    def list_albums(self):
        albums = self.mpd_retry_with_mutex(self.mpd_client.lsinfo)
        # albums = filter(lambda x: x, albums)

        time.sleep(0.3)

        return albums


# The initializer stuff gets executed directly
player_ctrl = PlayerMPD()
plugs.register(player_ctrl, name='ctrl')


@plugs.atexit
def atexit(signal: int):
    global player_ctrl
    player_ctrl.exit()
