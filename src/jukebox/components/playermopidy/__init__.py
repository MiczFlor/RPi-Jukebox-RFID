# -*- coding: utf-8 -*-
"""
TODO change comments to match mopidy
Package for interfacing with the mopidy 

Status information in three topics
1) Player Status: published only on change
  This is a subset of the MPD status (and not the full MPD status) ??
  - folder
  - song
  - volume (volume is published only via player status, and not separatly to avoid too many Threads)
  - ...
2) Elapsed time: published every 250 ms, unless constant
  - elapsed
3) Folder Config: published only on change
   This belongs to the folder being played
   Publish:
   - random, resume, single, loop
   On save store this information:
   Contains the information for resume functionality of each folder
   - random, resume, single, loop
   - if resume:
     - current song, elapsed
   - what is PLAYSTATUS for?
   When to save
   - on stop
   Angstsave:
   - on pause (only if box get turned off without proper shutdown - else stop gets implicitly called)
   - on status change of random, resume, single, loop (for resume omit current status if currently playing- this has now meaning)
   Load checks:
   - if resume, but no song, elapsed -> log error and start from the beginning

Status storing:
  - Folder config for each folder (see above)
  - Information to restart last folder playback, which is:
    - last_folder -> folder_on_close
    - song, elapsed
    - random, resume, single, loop
    - if resume is enabled, after start we need to set last_played_folder, such that card swipe is detected as second swipe?!
      on the other hand: if resume is enabled, this is also saved to folder.config -> and that is checked by play card

Internal status
  - last played folder: Needed to detect second swipe


Saving {'player_status': {'last_played_folder': 'TraumfaengerStarkeLieder', 'CURRENTSONGPOS': '0', 'CURRENTFILENAME': 'TraumfaengerStarkeLieder/01.mp3'},
'audio_folder_status':
{'TraumfaengerStarkeLieder': {'ELAPSED': '1.0', 'CURRENTFILENAME': 'TraumfaengerStarkeLieder/01.mp3', 'CURRENTSONGPOS': '0', 'PLAYSTATUS': 'stop', 'RESUME': 'OFF', 'SHUFFLE': 'OFF', 'LOOP': 'OFF', 'SINGLE': 'OFF'},
'Giraffenaffen': {'ELAPSED': '1.0', 'CURRENTFILENAME': 'TraumfaengerStarkeLieder/01.mp3', 'CURRENTSONGPOS': '0', 'PLAYSTATUS': 'play', 'RESUME': 'OFF', 'SHUFFLE': 'OFF', 'LOOP': 'OFF', 'SINGLE': 'OFF'}}}

References:
https://github.com/Mic92/python-mpd2
https://python-mpd2.readthedocs.io/en/latest/topics/commands.html
https://mpd.readthedocs.io/en/latest/protocol.html

sudo -u mpd speaker-test -t wav -c 2
"""  # noqa: E501
# Warum ist "Second Swipe" im Player und nicht im RFID Reader?
# Second swipe ist abhängig vom Player State - nicht vom RFID state.
# Beispiel: RFID triggered Folder1, Webapp triggered Folder2, RFID Folder1: Dann muss das 2. Mal Folder1 auch als "first swipe"
# gewertet werden. Wenn der RFID das basierend auf IDs macht, kann der nicht  unterscheiden und glaubt es ist 2. Swipe.
# Beispiel 2: Jemand hat RFID Reader (oder 1x RFID und 1x Barcode Scanner oder so) angeschlossen. Liest zuerst Karte mit
# Reader 1 und dann mit Reader 2: Reader 2 weiß nicht, was bei Reader 1 passiert ist und denkt es ist 1. swipe.
# Beispiel 3: RFID trigered Folder1, Playlist läuft durch und hat schon gestoppt, dann wird die Karte wieder vorgehalten.
# Dann muss das als 1. Swipe gewertet werden
# Beispiel 4: RFID triggered "Folder1", dann wird Karte "Volume Up" aufgelegt, dann wieder Karte "Folder1": Auch das ist
# aus Sicht ders Playbacks 2nd Swipe
# 2nd Swipe ist keine im Reader festgelegte Funktion extra fur den Player.
#
# In der aktuellen Implementierung weiß der Player (der second "swipe" dekodiert) überhaupt nichts vom RFID.
# Im Prinzip gibt es zwei "Play" Funktionen: (1) play always from start und (2) play with toggle action.
# Die Webapp ruft immer (1) auf und die RFID immer (2). Jetzt kann man sogar für einige Karten sagen
# immer (1) - also kein Second Swipe und für andere (2).
# Sollte der Reader das Swcond swipe dekodieren, muss aber der Reader den Status des Player kennen.
# Das ist allerdings ein Problem. In Version 2 ist das nicht aufgefallen,
# weil alles uber File I/Os lief - Thread safe ist das nicht!
#
# Beispiel: Second swipe bei anderen Funktionen, hier: WiFi on/off.
# Was die Karte Action tut ist ein Toggle. Der Toggle hängt vom Wifi State ab, den der RFID Kartenleser nicht kennt.
# Den kann der Leser auch nicht tracken. Der State kann ja auch über die WebApp oder Kommandozeile geändert werden.
# Toggle (und 2nd Swipe generell) ist immer vom Status des Zielsystems abhängig und kann damit nur vom Zielsystem geändert
# werden. Bei Wifi also braucht man 3 Funktionen: on / off / toggle. Toggle ist dann first swipe / second swipe

import threading
import logging
import json

import functools
import components.player
import jukebox.cfghandler
import jukebox.utils as utils
import jukebox.plugs as plugs
import jukebox.multitimer as multitimer
import jukebox.publishing as publishing
import jukebox.playlistgenerator as playlistgenerator
import misc

from jsonrpcclient import Ok, parse_json, request_json
from json import JSONDecoder
from websocket import create_connection, WebSocket, WebSocketException
from jukebox.NvManager import nv_manager



logger = logging.getLogger('jb.PlayerMopidy')
cfg = jukebox.cfghandler.get_handler('jukebox')


class MpdLock:
    def __init__(self, client: WebSocket, connection_url: str):
        self._lock = threading.RLock()
        self.client = client
        self.connection_url = connection_url

    def _try_connect(self):
        try:
            self.client.connect(self.connection_url)
        except WebSocketException:
            pass

    def __enter__(self):
        self._lock.acquire()
        self._try_connect()
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        self._lock.release()

    def acquire(self, blocking: bool = True, timeout: float = -1) -> bool:
        locked = self._lock.acquire(blocking, timeout)
        if locked:
            self._try_connect()
        return locked

    def release(self):
        self.client.close()
        self._lock.release()

    def locked(self):
        return self._lock.locked()


class PlayerMopidy:
    """Interface to Mopidy Daemon via RFC Json"""

    def __init__(self):
        #todo
        self.mopidy_url = cfg.getn('playermopidy', 'mopidy_url')
        self.mopidy_ws_client = None
        self.mopidy_status = {}
        self.nvm = nv_manager()
        self.music_player_status = self.nvm.load(cfg.getn('playermopidy', 'status_file'))

        self.second_swipe_action_dict = {'toggle': self.mopidy_toggle,
                                         'play': self.mopidy_play,
                                         'skip': self.mopidy_next,
                                         'rewind': self.mopidy_rewind,
                                         'replay': self.mopidy_play,
                                         'replay_if_stopped': self.mopidy_play}
        self.second_swipe_action = None
        #self.decode_2nd_swipe_option()

        # The timeout refer to the low-level socket time-out
        # If these are too short and the response is not fast enough (due to the PI being busy),
        # the current MPC command times out. Leave these at blocking calls, since we do not react on a timed out socket
        # in any relevant matter anyway
        self.mopidy_client_timeout = None               # network timeout in seconds (floats allowed), default: None
        self.mopidy_client_idletimeout = None           # timeout for fetching the result of the idle command

        logger.info(f"Instantiated to Mopidy Version")

        #TODO what do we do since we have no folders?
        
        self.current_folder_status = {}
        if not self.music_player_status:
            self.music_player_status['player_status'] = {}
            self.music_player_status['audio_folder_status'] = {}
            self.music_player_status['audio_stream_status'] = {}
            #self.music_player_status.save_to_json()
            self.current_folder_status = {}
            self.music_player_status['player_status']['last_played_folder'] = ''
        #else:
        #    last_played_tracklist = self.music_player_status['player_status'].get('last_played_folder')
        #    if last_played_tracklist:
        #        # current_folder_status is a dict, but last_played_folder a str
        #        self.current_folder_status = self.music_player_status['audio_folder_status'][last_played_folder]
        #        # Restore the playlist status in mpd
        #        # But what about playback position?
        #        self.mpd_client.clear()
        #        #  This could fail and cause load fail of entire package:
        #        # self.mpd_client.add(last_played_folder)
        #        logger.info(f"Last Played Folder: {last_played_folder}")

        # Clear last folder played, as we actually did not play any folder yet
        # Needed for second swipe detection
        # TODO: This will loose the last_played_folder information is the box is started and closed with playing anything...
        # Change this to last_played_folder and shutdown_state (for restoring)
        #self.music_player_status['player_status']['last_played_folder'] = ''

        self.old_song = None
        self.mpd_status = {}
        self.mpd_status_poll_interval = 0.25
        #self.mpd_lock = MpdLock(self.mpd_client, self.mpd_host, 6600)
        self.status_is_closing = False
        # self.status_thread = threading.Timer(self.mpd_status_poll_interval, self._mpd_status_poll).start()

        #self.status_thread = multitimer.GenericEndlessTimerClass('mopidy.timer_status',
        #                                                         self.mopidy_status_poll_interval, self._mpd_status_poll)
        #self.status_thread.start()

        

    def exit(self):
        logger.debug("Exit routine of playermopidy started")
        self.status_is_closing = True
        #self.status_thread.cancel()
        self.mopidy_ws_client.close()
        #self.nvm.save_all()
        #return self.status_thread.timer_thread

    def connect(self):
        self.mopidy_ws_client = create_connection(self.mopidy_url)
    """def decode_2nd_swipe_option(self):
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
    """

    def _send_get_json(self, method, parameters = None):
        """Shortcut for a back and forth message to mopidy through websocket"""
        self.mopidy_ws_client = create_connection(self.mopidy_url)
        req_json = self._build_rpc_message(method, parameters)
        self.mopidy_ws_client.send(req_json)
        response_json =  self.mopidy_ws_client.recv()
        return self._read_json_response(response_json)

    def _build_rpc_message(self, method, parameters = None):
        """Helper function to easily build the rpc json"""
        req_json = request_json(method,parameters)
        logger.debug("Request is:")
        logger.debug(req_json)
        return req_json
    
    def _read_json_response(self, response):
        """Helper function to either return rpc json or event"""
        try:
            response = parse_json(response).result 
        except:
            response = json.loads(response) #events cannot be parsed by parse_json

        logger.debug("Response is:")
        logger.debug(response)
        return response

    def _is_current_tracklist_same_as_uri_tracklist(self, uri):
        """Helper function to compare tracklist from new uri to current loaded tracklist"""
        tracklist_current = self.mopidy_get_tracklist()
        tracklist_to_compare = self.mopidy_lookup(uri)
        if tracklist_current.result == tracklist_to_compare.result[uri]: #the result from lookup includes uri
            True
        else:
            False

    def _mopidy_status_poll(self):
        """
        this method polls the status from mopidy and stores the important inforamtion in the music_player_status,
        it will repeat itself in the intervall specified by self.mopidy_status_poll_interval
        """
        #TODO thread handling
        self.mopidy_status['state'] = self._send_get_json("core.playback.get_state")
        self.mopidy_status['elapsed'] = self._send_get_json("core.playback.get_time_position")
        self.mopidy_status['tracklist'] = self._send_get_json("core.tracklist.get_tl_tracks")
        self.mopidy_status['tracklist_length'] = self._send_get_json("core.tracklist.get_length")
        self.mopidy_status['tracklist_current_position'] = self._send_get_json("core.tracklist.index")
        self.mopidy_status['song'] = self._send_get_json("core.playback.get_current_track")
        self.mopidy_status['time'] = self.mopidy_status['elapsed']
        self.mopidy_status['random'] = self._send_get_json("core.tracklist.get_random")
        self.mopidy_status['repeat'] = self._send_get_json("core.tracklist.get_repeat")
        self.mopidy_status['single'] = self._send_get_json("core.tracklist.get_single")
        self.mopidy_status['consume'] = self._send_get_json("core.tracklist.get_consume")
        self.mopidy_status['volume'] = self._send_get_json("core.mixer.get_volume")
        
        if self.mopidy_status['song'] is not None:
            self.mopidy_status['song_name'] = self.mopidy_status['song']['name']
            self.mopidy_status['song_uri'] = self.mopidy_status['song']['uri']
            self.mopidy_status['playlist'] = self._send_get_json("core.playlists.as_list")
            self.mopidy_status['playlist_uri'] = self.mopidy_status['playlist']
            self.mopidy_status['album'] =  self.mopidy_status['song']['album']
            self.mopidy_status['album_name'] =  self.mopidy_status['song']['album']['name']
            self.mopidy_status['album_uri'] = self.mopidy_status['song']['album']['uri']
            self.mopidy_status['artists'] = self.mopidy_status['song']['artists'] #TODO get all artists
            self.mopidy_status['artists_name'] = self.mopidy_status['song']['artists'][0]['name']
            self.mopidy_status['artists_uri'] = self.mopidy_status['song']['artists'][0]['uri']
            self.mopidy_status['duration'] = self.mopidy_status['song']['length']
            self.music_player_status['player_status']["CURRENTSONGPOS"] = self.mopidy_status['tracklist_current_position'] 
            self.music_player_status['player_status']["CURRENTFILENAME"] = self.mopidy_status['song']
            self.current_folder_status["CURRENTFILENAME"] = self.mopidy_status['song']
            self.current_folder_status["CURRENTSONGPOS"] = self.mopidy_status['elapsed']
            self.current_folder_status["ELAPSED"] = self.mopidy_status['elapsed']
            self.current_folder_status["PLAYSTATUS"] = self.mopidy_status['state']
            #self.current_folder_status["RESUME"] = "OFF"
            self.current_folder_status["SHUFFLE"] = self.mopidy_status['random']
            self.current_folder_status["LOOP"] = self.mopidy_status['repeat']
            self.current_folder_status["SINGLE"] = self.mopidy_status['single']

        #self.mopidy_status.update(self.mpd_retry_with_mutex(self.mpd_client.status))
        #self.mopidy_status.update(self.mpd_retry_with_mutex(self.mpd_client.currentsong))
        
        if self.mopidy_status['elapsed'] > 0:
            self.current_folder_status["ELAPSED"] = self.mopidy_status['elapsed']
            self.music_player_status['player_status']["CURRENTSONGPOS"] = self.mopidy_status['elapsed']
            self.music_player_status['player_status']["CURRENTFILENAME"] = self.mopidy_status['song']

        # Delete the volume key to avoid confusion
        # Volume is published via the 'volume' component!
        try:
            del self.mopidy_status['volume']
        except KeyError:
            pass
        
        publishing.get_publisher().send('playerstatus', self.mopidy_status)

    @plugs.tag
    def get_player_type_and_version(self):
        #with self.mpd_lock:
        #value = self.mopidy_ws_client.mpd_version()
        #return value
        pass

    @plugs.tag
    def update(self):
        #with self.mpd_lock:
            #state = self.mpd_client.update()
        #return state
        pass

    @plugs.tag
    def mopidy_play(self, position_in_tracklist):
        #with self.mpd_lock:
        if position_in_tracklist >= 0:
            self._send_get_json("core.tracklist.index", {"tlid": position_in_tracklist})
        return self._send_get_json("core.playback.play")

    @plugs.tag
    def mopidy_stop(self):
        #with self.mpd_lock:
            
        return self._send_get_json("core.playback.stop")

    @plugs.tag
    def mopidy_pause(self, state: int = 1):
        #TODO check card removal and re placement stuff
        """Enforce pause to state (1: pause, 0: resume)

        This is what you want as card removal action: pause the playback, so it can be resumed when card is placed
        on the reader again. What happens on re-placement depends on configured second swipe option
        """
        #with self.mpd_lock:
            #self.mpd_client.pause(state)
        state = self._send_get_json("core.playback.get_state")    
        if(state.result == "paused"):
            self._send_get_json("core.playback.resume")
        
        self._send_get_json("core.playback.pause")
    
    
    @plugs.tag
    def mopidy_prev(self):
        logger.debug("Prev")
        #with self.mpd_lock:
        self._send_get_json("core.playback.previous")
        

    @plugs.tag
    def mopidy_next(self):
        """Play next track in current playlist"""
        logger.debug("Next")
        #with self.mpd_lock:
        self._send_get_json("core.playback.next")

    @plugs.tag
    def mopidy_seek(self, new_time):
        #with self.mpd_lock:
        self._send_get_json("core.playback.seek",{"time_positino":new_time})


    @plugs.tag
    def mopidy_shuffle(self):
        # As long as we don't work with waiting lists (aka playlist), this implementation is ok!
        shuffle_state = self._send_get_json("core.tracklist.get_random")    
        if(shuffle_state.result == True):
            return self._send_get_json("core.tracklist.set_random",{"value":False})
        
        return self._send_get_json("core.tracklist.set_random",{"value":True})

    @plugs.tag
    def mopidy_get_shuffle_state(self):
        # As long as we don't work with waiting lists (aka playlist), this implementation is ok!
        return self._send_get_json("core.tracklist.get_random") 
    
    @plugs.tag
    def mopidy_toggle(self):
        """Toggle pause state, i.e. do a pause / resume depending on current state"""
        logger.debug("Toggle")
        #with self.mpd_lock:
        self.mopidy_pause()
    
    @plugs.tag
    def mopidy_rewind(self):
        """
        Re-start current playlist from first track
        """
        #Note: Will not re-read folder config, but leave settings untouched""
        logger.debug("Rewind")
        #with self.mpd_lock:
        self.mpd_client.play(0)

    """
    @plugs.tag
    def replay(self):
        ""
        Re-start playing the last-played folder

        Will reset settings to folder config""
        logger.debug("Replay")
        with self.mpd_lock:
            self.play_folder(self.music_player_status['player_status']['last_played_folder'])



    @plugs.tag
    def replay_if_stopped(self):
        ""
        Re-start playing the last-played folder unless playlist is still playing

        .. note:: To me this seems much like the behaviour of play,
            but we keep it as it is specifically implemented in box 2.X""
        with self.mpd_lock:
            if self.mopidy_status['state'] == 'stop':
                self.play_folder(self.music_player_status['player_status']['last_played_folder'])
    """
    
    @plugs.tag
    def mopidy_repeatmode(self, mode):
        if mode == 'repeat':
            repeat = True
            single = False
        elif mode == 'single':
            repeat = True
            single = True
        else:
            repeat = False
            single = False

        #with self.mpd_lock:
        self._send_get_json("core.tracklist.set_repeat",{"value":repeat})
        self._send_get_json("core.tracklist.set_single",{"value":single})

    @plugs.tag
    def get_current_song(self, param):
        return self._send_get_json("core.playback.get_current_track")
    
    """
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
    """

    @plugs.tag
    def mopidy_play_single(self, song_url):
        #with self.mpd_lock:
        #    self.mpd_client.clear()
        #    self.mpd_client.addid(song_url)
        #    self.mpd_client.play()
        self._send_get_json("core.tracklist.clear")
        self._send_get_json("core.tracklist.add",{'uris':{song_url}})
        self.play()

    @plugs.tag
    def mopidy_play_url(self, url):
        #with self.mpd_lock:
        #    self.mpd_client.clear()
        #    self.mpd_client.addid(song_url)
        #    self.mpd_client.play()
        self._send_get_json("core.tracklist.clear")
        self._send_get_json("core.tracklist.add",{'uris':[url]})
        self.mopidy_play()
    
    @plugs.tag
    def mopidy_get_tracklist(self):
        #with self.mpd_lock:
        #    self.mpd_client.clear()
        #    self.mpd_client.addid(song_url)
        #    self.mpd_client.play()
        return self._send_get_json("core.tracklist.get_tracks")

    @plugs.tag
    def mopidy_lookup(self, uri):
        #with self.mpd_lock:
        #    self.mpd_client.clear()
        #    self.mpd_client.addid(song_url)
        #    self.mpd_client.play()
        return self._send_get_json("core.library.lookup",{'uris':[uri]})

    """
    @plugs.tag
    def resume(self):
        with self.mpd_lock:
            songpos = self.current_folder_status["CURRENTSONGPOS"]
            elapsed = self.current_folder_status["ELAPSED"]
            self.mpd_client.seek(songpos, elapsed)
            self.mpd_client.play()
    """

    @plugs.tag
    def mopidy_play_card(self, uri): #folder: str, recursive: bool = False):
        """
        Main entry point for trigger music playing from RFID reader. Decodes second swipe options before playing folder content

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
        #logger.debug(f"last_played_folder = {self.music_player_status['player_status']['last_played_folder']}")
        #with self.mpd_lock:
    
        is_second_swipe = self._is_current_tracklist_same_as_uri_tracklist(uri)
        if self.second_swipe_action is not None and is_second_swipe:
            logger.debug('Calling second swipe action')
            self.second_swipe_action()
        else:
            logger.debug('Calling first swipe action')
            self.mopidy_play_url(uri)
    
    """
    @plugs.tag
    def get_folder_content(self, folder: str):
        ""
        Get the folder content as content list with meta-information. Depth is always 1.

        Call repeatedly to descend in hierarchy

        :param folder: Folder path relative to music library path
        ""
        plc = playlistgenerator.PlaylistCollector(components.player.get_music_library_path())
        plc.get_directory_content(folder)
        return plc.playlist

    @plugs.tag
    def play_folder(self, folder: str, recursive: bool = False) -> None:
        ""
        Playback a music folder.

        Folder content is added to the playlist as described by :mod:`jukebox.playlistgenerator`.
        The playlist is cleared first.

        :param folder: Folder path relative to music library path
        :param recursive: Add folder recursively
        ""
        # TODO: This changes the current state -> Need to save last state
        with self.mpd_lock:
            logger.info(f"Play folder: '{folder}'")
            self.mpd_client.clear()

            plc = playlistgenerator.PlaylistCollector(components.player.get_music_library_path())
            plc.parse(folder, recursive)
            uri = '--unset--'
            try:
                for uri in plc:
                    self.mpd_client.addid(uri)
            except mpd.base.CommandError as e:
                logger.error(f"{e.__class__.__qualname__}: {e} at uri {uri}")
            except Exception as e:
                logger.error(f"{e.__class__.__qualname__}: {e} at uri {uri}")

            self.music_player_status['player_status']['last_played_folder'] = folder

            self.current_folder_status = self.music_player_status['audio_folder_status'].get(folder)
            if self.current_folder_status is None:
                self.current_folder_status = self.music_player_status['audio_folder_status'][folder] = {}

            self.mpd_client.play()
    """
    @plugs.tag
    def mopidy_play_album(self, album_url):
        """
        Playback a album from url
        TODO check whether url has album in it
        """
        #with self.mpd_lock:
        logger.info(f"Play album_url: '{album_url}")
        self.mopidy_play_url(album_url)

    """
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
    """

    @plugs.tag
    def mopidy_player_status(self):
        return self.mopidy_status

    @plugs.tag
    def mopidy_playlist_info(self):
        #with self.mpd_lock:
        #    value = self.mopidy_status.playlist
        return self.mopidy_status['playlist']

    """
    # Attention: MPD.listal will consume a lot of memory with large libs.. should be refactored at some point
    @plugs.tag
    def list_all_dirs(self):
        with self.mpd_lock:
            result = self.mpd_client.listall()
            # list = [entry for entry in list if 'directory' in entry]
        return result
    
    @plugs.tag
    def list_albums(self):
        with self.mpd_lock:
            albums = self.mpd_retry_with_mutex(self.mpd_client.list, 'album', 'group', 'albumartist')

        return albums

    @plugs.tag
    def list_song_by_artist_and_album(self, albumartist, album):
        with self.mpd_lock:
            albums = self.mpd_retry_with_mutex(self.mpd_client.find, 'albumartist', albumartist, 'album', album)

        return albums

    @plugs.tag
    def get_song_by_url(self, song_url):
        with self.mpd_lock:
            song = self.mpd_retry_with_mutex(self.mpd_client.find, 'file', song_url)

        return song


    def get_volume(self):
        ""
        Get the current volume

        For volume control do not use directly, but use through the plugin 'volume',
        as the user may have configured a volume control manager other than MPD""
        #with self.mpd_lock:
        #   volume = self.mpd_client.status().get('volume')
        #return int(volume)

    def set_volume(self, volume):
        ""
        Set the volume

        For volume control do not use directly, but use through the plugin 'volume',
        as the user may have configured a volume control manager other than MPD""
        #with self.mpd_lock:
            #self.mpd_client.setvol(volume)
        #return self.get_volume()
    """

# ---------------------------------------------------------------------------
# Plugin Initializer / Finalizer
# ---------------------------------------------------------------------------

playermopidy: PlayerMopidy


@plugs.initialize
def initialize():
    global playermopidy
    playermopidy = PlayerMopidy()
    plugs.register(playermopidy, name='playermopidy')

    # Update mopidy library
    #library_update = cfg.setndefault('playermopidy', 'library', 'update_on_startup', value=True)
    #if library_update:
    #    player_mopidy.update()

    
@plugs.atexit
def atexit(**ignored_kwargs):
    global playermopidy
    return playermopidy.exit()
