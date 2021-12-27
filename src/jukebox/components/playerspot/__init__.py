# -*- coding: utf-8 -*-
"""
Package for interfacing with the librespot-java API

Saving
{'player_status': {'last_played_folder': 'TraumfaengerStarkeLieder', 'CURRENTSONGPOS': '0',
                     'CURRENTFILENAME': 'TraumfaengerStarkeLieder/01.mp3'},
    'audio_folder_status':
       {'TraumfaengerStarkeLieder': {'ELAPSED': '1.0', 'CURRENTFILENAME': 'TraumfaengerStarkeLieder/01.mp3',
                                     'CURRENTSONGPOS': '0', 'PLAYSTATUS': 'stop', 'RESUME': 'OFF',
                                     'SHUFFLE': 'OFF', 'LOOP': 'OFF', 'SINGLE': 'OFF'},
        'Giraffenaffen': {'ELAPSED': '1.0', 'CURRENTFILENAME': 'TraumfaengerStarkeLieder/01.mp3',
                          'CURRENTSONGPOS': '0', 'PLAYSTATUS': 'play', 'RESUME': 'OFF', 'SHUFFLE': 'OFF',
                          'LOOP': 'OFF', 'SINGLE': 'OFF'}}}

References:
https://github.com/librespot-org/librespot-java
https://github.com/librespot-org/librespot-java/tree/dev/api
https://github.com/spocon/spocon
"""

import logging
import functools
import threading
import urllib.parse
import requests

import components.player
import jukebox.cfghandler
import jukebox.utils as utils
import jukebox.plugs as plugs
import jukebox.multitimer as multitimer
import jukebox.publishing as publishing
import misc

from jukebox.NvManager import nv_manager

logger = logging.getLogger('jb.PlayerSpot')
cfg = jukebox.cfghandler.get_handler('jukebox')

test_dict = {'player_status': {'last_played_folder': 'TraumfaengerStarkeLieder', 'CURRENTSONGPOS': '0',
                               'CURRENTFILENAME': 'TraumfaengerStarkeLieder/01.mp3'},
             'audio_folder_status':
                 {'TraumfaengerStarkeLieder': {'ELAPSED': '1.0', 'CURRENTFILENAME': 'TraumfaengerStarkeLieder/01.mp3',
                                               'CURRENTSONGPOS': '0', 'PLAYSTATUS': 'stop', 'RESUME': 'OFF',
                                               'SHUFFLE': 'OFF', 'LOOP': 'OFF', 'SINGLE': 'OFF'},
                  'Giraffenaffen': {'ELAPSED': '1.0', 'CURRENTFILENAME': 'TraumfaengerStarkeLieder/01.mp3',
                                    'CURRENTSONGPOS': '0', 'PLAYSTATUS': 'play', 'RESUME': 'OFF', 'SHUFFLE': 'OFF',
                                    'LOOP': 'OFF', 'SINGLE': 'OFF'}}}


class PlayerSpot:
    """Interface to librespot-java API"""

    # ToDo: spot_state
    # ToDo: response handling
    def __init__(self):
        self.nvm = nv_manager()
        self.spot_host = cfg.getn('playerspot', 'host')
        self.spot_api_port = 24879
        self.spot_api_baseurl = f"{self.spot_host}:{self.spot_api_port}"
        self.music_player_status = self.nvm.load(cfg.getn('playermpd', 'status_file'))

        self.second_swipe_action_dict = {'toggle': self.toggle,
                                         'play': self.play,
                                         'skip': self.next,
                                         'rewind': self.rewind,
                                         'replay': self.replay,
                                         'replay_if_stopped': self.replay_if_stopped}
        self.second_swipe_action = None
        self.decode_2nd_swipe_option()

        self.current_folder_status = {}
        if not self.music_player_status:
            self.music_player_status['player_status'] = {}
            self.music_player_status['audio_folder_status'] = {}
            self.music_player_status.save_to_json()
            self.current_folder_status = {}
            self.music_player_status['player_status']['last_played_folder'] = ''
        else:
            last_played_folder = self.music_player_status['player_status'].get('last_played_folder')
            if last_played_folder:
                # current_folder_status is a dict, but last_played_folder a str
                self.current_folder_status = self.music_player_status['audio_folder_status'][last_played_folder]
                logger.info(f"Last Played Folder: {last_played_folder}")

        # Clear last folder played, as we actually did not play any folder yet
        # Needed for second swipe detection
        # TODO: This will loose the last_played_folder information is the box is started and closed with
        #  playing anything...
        # Change this to last_played_folder and shutdown_state (for restoring)
        self.music_player_status['player_status']['last_played_folder'] = ''

        self.old_song = None
        self.mpd_status = {}
        self.mpd_status_poll_interval = 0.25
        # ToDo: check of spot_lock works
        self.status_is_closing = False
        # self.status_thread = threading.Timer(self.mpd_status_poll_interval, self._mpd_status_poll).start()

        self.status_thread = multitimer.GenericEndlessTimerClass('mpd.timer_status',
                                                                 self.mpd_status_poll_interval, self._mpd_status_poll)
        self.status_thread.start()

        self.old_song = None
        self.spot_status_poll_interval = 0.25
        self.status_is_closing = False

    def exit(self):
        logger.debug("Exit routine of playerspot started")
        self.nvm.save_all()
        api_path = "/instance/close"
        requests.post(urllib.parse.urljoin(self.spot_api_baseurl, api_path))
        return "payerspot exited"

    def decode_2nd_swipe_option(self):
        cfg_2nd_swipe_action = cfg.setndefault('playermpd', 'second_swipe_action', 'alias', value='none').lower()
        if cfg_2nd_swipe_action not in [*self.second_swipe_action_dict.keys(), 'none', 'custom']:
            logger.error(f"Config mpd.second_swipe_action must be one of "
                         f"{[*self.second_swipe_action_dict.keys(), 'none', 'custom']}. Ignore setting.")
        if cfg_2nd_swipe_action in self.second_swipe_action_dict.keys():
            self.second_swipe_action = self.second_swipe_action_dict[cfg_2nd_swipe_action]
        if cfg_2nd_swipe_action == 'custom':
            custom_action = utils.decode_rpc_call(cfg.getn('playermpd', 'second_swipe_action', default=None))
            self.second_swipe_action = functools.partial(plugs.call_ignore_errors,
                                                         custom_action['package'],
                                                         custom_action['plugin'],
                                                         custom_action['method'],
                                                         custom_action['args'],
                                                         custom_action['kwargs'])

    def _spot_status_poll(self):
        """
        this method polls the status from mpd and stores the important inforamtion in the music_player_status,
        it will repeat itself in the intervall specified by self.mpd_status_poll_interval
        """
        self.mpd_status.update(self.mpd_retry_with_mutex(self.mpd_client.status))
        self.mpd_status.update(self.mpd_retry_with_mutex(self.mpd_client.currentsong))

        if self.mpd_status.get('elapsed') is not None:
            self.current_folder_status["ELAPSED"] = self.mpd_status['elapsed']
            self.music_player_status['player_status']["CURRENTSONGPOS"] = self.mpd_status['song']
            self.music_player_status['player_status']["CURRENTFILENAME"] = self.mpd_status['file']

        if self.mpd_status.get('file') is not None:
            self.current_folder_status["CURRENTFILENAME"] = self.mpd_status['file']
            self.current_folder_status["CURRENTSONGPOS"] = self.mpd_status['song']
            self.current_folder_status["ELAPSED"] = self.mpd_status.get('elapsed', '0.0')
            self.current_folder_status["PLAYSTATUS"] = self.mpd_status['state']
            self.current_folder_status["RESUME"] = "OFF"
            self.current_folder_status["SHUFFLE"] = "OFF"
            self.current_folder_status["LOOP"] = "OFF"
            self.current_folder_status["SINGLE"] = "OFF"

        # Delete the volume key to avoid confusion
        # Volume is published via the 'volume' component!
        try:
            del self.mpd_status['volume']
        except KeyError:
            pass
        publishing.get_publisher().send('playerstatus', self.mpd_status)

    @plugs.tag
    def load(self, uri: str, start_playing: bool):
        self.check_uri(uri)
        api_path = f"/player/load?uri={uri}&play={start_playing}"
        requests.post(urllib.parse.urljoin(self.spot_api_baseurl, api_path))

    @plugs.tag
    def play(self):
        api_path = "/player/resume"
        requests.post(urllib.parse.urljoin(self.spot_api_baseurl, api_path))

    @plugs.tag
    def stop(self):
        self.pause(state=1)

    @plugs.tag
    def pause(self, state: int = 1):
        """Enforce pause to state (1: pause, 0: resume)

        This is what you want as card removal action: pause the playback, so it can be resumed when card is placed
        on the reader again. What happens on re-placement depends on configured second swipe option
        """
        if state == 1:
            api_path = "/player/pause"
            requests.post(urllib.parse.urljoin(self.spot_api_baseurl, api_path))
        else:
            self.play()

    @plugs.tag
    def prev(self):
        api_path = "/player/prev"
        requests.post(urllib.parse.urljoin(self.spot_api_baseurl, api_path))

    @plugs.tag
    def next(self):
        api_path = "/player/next"
        requests.post(urllib.parse.urljoin(self.spot_api_baseurl, api_path))

    @plugs.tag
    def seek(self, new_time: int):
        """
        Seek to a given position in milliseconds specified by new_time
        """
        api_path = f"/player/seek?position_ms={new_time}"
        requests.post(urllib.parse.urljoin(self.spot_api_baseurl, api_path))

    @plugs.tag
    def shuffle(self, random: bool):
        api_path = f"/player/shuffle?state={1 if random else 0}"
        requests.post(urllib.parse.urljoin(self.spot_api_baseurl, api_path))

    @plugs.tag
    def rewind(self):
        """
        Re-start current playlist from first track

        Note: Will not re-read folder config, but leave settings untouched"""
        logger.debug("Rewind")
        self.seek(0)

    @plugs.tag
    def replay(self):
        """
        Re-start playing the last-played playlist

        Will reset settings to folder config"""
        logger.debug("Replay")
        self.play_playlist(self.music_player_status['player_status']['last_played_folder'])

    @plugs.tag
    def toggle(self):
        """Toggle pause state, i.e. do a pause / resume depending on current state"""
        logger.debug("Toggle")
        api_path = "/player/play-pause"
        requests.post(urllib.parse.urljoin(self.spot_api_baseurl, api_path))

    @plugs.tag
    def replay_if_stopped(self):
        """
        Re-start playing the last-played folder unless playlist is still playing

        .. note:: To me this seems much like the behaviour of play,
            but we keep it as it is specifically implemented in box 2.X"""
        logger.debug("replay_if_stopped")
        if self.mpd_status['state'] == 'stop':
            self.play_playlist(self.music_player_status['player_status']['last_played_folder'])

    @plugs.tag
    def repeatmode(self, mode: str):
        if mode == 'repeat':
            rep_state = "context"
        elif mode == 'single':
            rep_state = "track"
        else:
            rep_state = "none"
        api_path = f"/player/repeat?state={rep_state}"
        requests.post(urllib.parse.urljoin(self.spot_api_baseurl, api_path))

    @plugs.tag
    def get_current_song(self, param):
        return self.spot_status

    @plugs.tag
    def map_filename_to_playlist_pos(self, filename):
        raise NotImplementedError

    @plugs.tag
    def remove(self):
        raise NotImplementedError

    @plugs.tag
    def move(self):
        raise NotImplementedError

    @plugs.tag
    def play_single(self, song_uri: str):
        self.check_uri(song_uri)
        api_path = f"/player/repeat?uri={song_uri}&play=true"
        requests.post(urllib.parse.urljoin(self.spot_api_baseurl, api_path))

    @plugs.tag
    def resume(self):
        songpos = self.current_folder_status["CURRENTSONGPOS"]
        self.seek(songpos)
        self.play()

    @plugs.tag
    def play_card(self, folder: str, recursive: bool = False):
        """
        Main entry point for trigger music playing from RFID reader. Decodes second swipe options before
        playing folder content

        Checks for second (or multiple) trigger of the same folder and calls first swipe / second swipe action
        accordingly.

        :param folder: Folder path relative to music library path
        :param recursive: Add folder recursively
        """
        # Developers notes:
        #
        #     * 2nd swipe trigger may also happen, if playlist has already stopped playing
        #       --> Generally, treat as first swipe
        #     * 2nd swipe of same Card ID may also happen if a different song has been played in between from WebUI
        #       --> Treat as first swipe
        #     * With place-not-swipe: Card is placed on reader until playlist expieres. Music stop. Card is removed and
        #       placed again on the reader: Should be like first swipe
        #     * TODO: last_played_folder is restored after box start, so first swipe of last played card may look like
        #       second swipe
        #
        logger.debug(f"last_played_folder = {self.music_player_status['player_status']['last_played_folder']}")
        logger.debug(f"last_played_folder = {self.music_player_status['player_status']['last_played_folder']}")
        is_second_swipe = self.music_player_status['player_status']['last_played_folder'] == folder
        if self.second_swipe_action is not None and is_second_swipe:
            logger.debug('Calling second swipe action')
            self.second_swipe_action()
        else:
            logger.debug('Calling first swipe action')
            self.play_playlist(folder, recursive)

    @plugs.tag
    def get_playlist_content(self, playlist_uri: str):
        """
        Get the spotify playlist content as content list with meta-information

        :param playlist_uri: URI for the spotify playlist as string
        """
        # ToDo: implement
        track_list = []
        return track_list

    @plugs.tag
    def play_playlist(self, playlist_uri: str, recursive: bool = False) -> None:
        """
        Playback a spotify playlist.

        :param playlist_uri: Folder path relative to music library path
        :param recursive: Add folder recursively
        """
        logger.debug("play_folder")
        # TODO: This changes the current state -> Need to save last state
        logger.info(f"Play spotify playlist: '{playlist_uri}'")

        self.music_player_status['player_status']['last_played_folder'] = playlist_uri

        self.current_folder_status = self.music_player_status['audio_folder_status'].get(playlist_uri)
        if self.current_folder_status is None:
            self.current_folder_status = self.music_player_status['audio_folder_status'][playlist_uri] = {}

        self.load(self.current_folder_status, start_playing=True)

    @plugs.tag
    def play_album(self, album_uri: str):
        """
        Playback a album from spotify.

        :param album_uri: Album URI from spotify
        """
        logger.debug("play_album")
        with self.spot_lock:
            logger.info(f"Play album: '{album_uri}'")
            self.load(album_uri, start_playing=True)

    @plugs.tag
    def queue_load(self, folder):
        # There was something playing before -> stop and save state
        # Clear the queue
        # Check / Create the playlist
        #  - not needed if same folder is played again? Buf what if files have been added a mpc update has been run?
        #  - and this a re-trigger to start the new playlist
        # If we must update the playlists everytime anyway why write them to file and not just keep them in the queue?
        # Load the playlist
        # Get folder config and apply settings
        pass

    @plugs.tag
    def playerstatus(self):
        return self.spot_status

    @plugs.tag
    def playlistinfo(self):
        # ToDo: implement
        value = ["this is a list"]
        return value

    @plugs.tag
    def list_all_dirs(self):
        raise NotImplementedError

    @plugs.tag
    def list_albums(self):
        albums = ["this is a list"]
        return albums

    @plugs.tag
    def list_song_by_artist_and_album(self, albumartist, album):
        # with self.mpd_lock:
        #     albums = self.mpd_retry_with_mutex(self.mpd_client.find, 'albumartist', albumartist, 'album', album)
        #
        # return albums
        pass

    def get_volume(self):
        """
        Get the current volume

        For volume control do not use directly, but use through the plugin 'volume',
        as the user may have configured a volume control manager other than Spotify"""
        # ToDo: get volume from Playback state
        # https://developer.spotify.com/documentation/web-api/reference/#/operations/get-information-about-the-users-current-playback
        pass

    def set_volume(self, volume):
        """
        Set the volume

        For volume control do not use directly, but use through the plugin 'volume',
        as the user may have configured a volume control manager other than Spotify"""
        api_path = f"/player/volume?volume_percent={volume}"
        requests.post(urllib.parse.urljoin(self.spot_api_baseurl, api_path))
        return self.get_volume()

    @staticmethod
    def check_uri(uri: str):
        """
        Checking that the uri has the right syntax
        """
        check_list = uri.split(":")
        valid_play_type = ["album", "track"]
        if check_list[1] == "user":
            assert len(check_list) == 5, f"URI {uri} is missing information."
            assert check_list[0] == "spotify", f"URI {uri} does not start with spotify"
            assert check_list[1] == "user", f"URI {uri} does not contain a valid type on pos 2"
            assert type(check_list[2]) is int, f"URI {uri} does not contain the right user id on pos 3"
            assert check_list[3] == "playlist", f"URI {uri} does not contain a valid type playlist on pos 4"

        else:
            assert len(check_list) == 3, f"URI {uri} is missing information."
            assert check_list[0] == "spotify", f"URI {uri} does not start with spotify"
            assert check_list[1] in valid_play_type, f"URI {uri} does not contain a valid type on pos 2"


# ---------------------------------------------------------------------------
# Plugin Initializer / Finalizer
# ---------------------------------------------------------------------------

player_ctrl: PlayerSpot


@plugs.initialize
def initialize():
    global player_ctrl
    player_ctrl = PlayerSpot()
    plugs.register(player_ctrl, name='ctrl')

    # Check user rights on music library
    library_check_user_rights = cfg.setndefault('playerspot', 'library', 'check_user_rights', value=True)
    if library_check_user_rights is True:
        music_library_path = components.player.get_music_library_path()
        if music_library_path is not None:
            logger.info(f"Change user rights for {music_library_path}")
            misc.recursive_chmod(music_library_path, mode_files=0o666, mode_dirs=0o777)


@plugs.atexit
def atexit(**ignored_kwargs):
    global player_ctrl
    return player_ctrl.exit()
