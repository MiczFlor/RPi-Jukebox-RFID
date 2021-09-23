# -*- coding: utf-8 -*-
"""
Package for interfacing with the MPD Music Player Daemon

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
"""
import re

import mpd
import threading
import logging
import time
import functools
import jukebox.cfghandler
import jukebox.utils as utils
import jukebox.plugs as plugs
import jukebox.multitimer as multitimer
import jukebox.publishing as publishing
from jukebox.NvManager import nv_manager
import jukebox.pubsub as pubsub
import misc


logger = logging.getLogger('jb.PlayerMPD')
cfg = jukebox.cfghandler.get_handler('jukebox')


class PlayerMPD:
    """Interface to MPD Music Player Daemon"""

    def __init__(self):
        self.nvm = nv_manager()
        self.mpd_host = cfg.getn('playermpd', 'host')
        self.music_player_status = self.nvm.load(cfg.getn('playermpd', 'status_file'))

        self.second_swipe_action_dict = {'toggle': self.toggle,
                                         'play': self.play,
                                         'skip': self.next,
                                         'rewind': self.rewind,
                                         'replay': self.replay,
                                         'replay_if_stopped': self.replay_if_stopped}
        self.second_swipe_action = None
        self.decode_2nd_swipe_option()

        self.mpd_client = mpd.MPDClient()
        self.mpd_client.timeout = 0.5               # network timeout in seconds (floats allowed), default: None
        self.mpd_client.idletimeout = 0.5           # timeout for fetching the result of the idle command
        self.connect()
        logger.info(f"Connected to MPD Version: {self.mpd_client.mpd_version}")

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
                # Restore the playlist status in mpd
                # But what about playback position?
                self.mpd_client.clear()
                self.mpd_client.add(last_played_folder)
                logger.info(f"Last Played Folder: {last_played_folder}")

        # Clear last folder played, as we actually did not play any folder yet
        # Needed for second swipe detection
        # TODO: This will loose the last_played_folder information is the box is started and closed with playing anything...
        # Change this to last_played_folder and shutdown_state (for restoring)
        self.music_player_status['player_status']['last_played_folder'] = ''

        self.old_song = None
        self.mpd_status = {}
        self.mpd_status_poll_interval = 0.25
        self.mpd_mutex = threading.Lock()
        self.status_is_closing = False
        # self.status_thread = threading.Timer(self.mpd_status_poll_interval, self._mpd_status_poll).start()

        self.status_thread = multitimer.GenericEndlessTimerClass('mpd.timer_status',
                                                                 self.mpd_status_poll_interval, self._mpd_status_poll)
        self.status_thread.start()

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

    def decode_2nd_swipe_option(self):
        cfg_2nd_swipe_action = cfg.setndefault('playermpd', 'second_swipe_action', 'quick_select', value='none').lower()
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
                except mpd.base.ConnectionError:
                    # Maybe now? TODO: this is not working properly yet, we are alwas anding up in the Exception!
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

    def _mpd_status_poll(self, **ignored_kwargs):
        """
        this method polls the status from mpd and stores the important inforamtion in the music_player_status,
        it will repeat itself in the intervall specified by self.mpd_status_poll_interval
        """
        self.mpd_status.update(self.mpd_retry_with_mutex(self.mpd_client.status))

        # get song name just if the song has changed
        if self.mpd_status.get('song') != self.old_song:
            self.mpd_status.update(self.mpd_retry_with_mutex(self.mpd_client.currentsong))
            self.old_song = self.mpd_status['song']

        # If volume ctrl is over mpd, volume is always retrieve via a full call to client status
        # To avoid double calls to status with evey status poll, we need a case differentiation here
        # In case MPD is the active volume manager, we can directly use the volume value
        if plugs.get('volume').factory.get_active != 'mpd':
            # This will log all plugin calls in logger and spams the debug messages:
            # self.mpd_status['volume'] = plugs.call_ignore_errors('volume', 'ctrl', 'get_volume')
            # Do the same, but prevent the debug logging:
            try:
                self.mpd_status['volume'] = plugs.get('volume', 'ctrl').get_volume()
            except Exception:
                pass

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
        publishing.get_publisher().send('playerstatus', self.mpd_status)

    @plugs.tag
    def get_player_type_and_version(self):
        return self.mpd_retry_with_mutex(self.mpd_client.mpd_version)

    @plugs.tag
    def update(self):
        logger.info("MPC music library update")
        return self.mpd_retry_with_mutex(self.mpd_client.update)

    @plugs.tag
    def play(self, songid=None):
        logger.debug("Play")
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
        logger.debug("Prev")
        self.mpd_retry_with_mutex(self.mpd_client.previous)
        return self.mpd_status

    @plugs.tag
    def next(self):
        """Play next track in current playlist"""
        logger.debug("Next")
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
    def rewind(self):
        """Re-start current playlist from first track

        Note: Will not re-read folder config, but leave settings untouched"""
        logger.debug("Rewind")
        self.mpd_retry_with_mutex(self.mpd_client.play, 1)

    @plugs.tag
    def replay(self):
        """Re-start playing the last-played folder

        Note: Will reset settings to folder config"""
        logger.debug("Replay")
        self.playlistaddplay(self.music_player_status['player_status']['last_played_folder'])

    @plugs.tag
    def toggle(self):
        """Toggle pause state, i.e. do a pause / resume depending on current state"""
        logger.debug("Toggle")
        self.mpd_retry_with_mutex(self.mpd_client.pause)

    @plugs.tag
    def replay_if_stopped(self):
        """Re-start playing the last-played folder unless playlist is still playing

        Note: To me this seems much like the behaviour of play,
        but we keep it as it is specifically implemented in box 2.X"""
        if self.mpd_status['state'] == 'stop':
            self.replay()

    @plugs.tag
    def play_card(self, folder=None):
        """Main entry point for trigger music playing from RFID reader

        Checks for second (or multiple) trigger of the same folder and calls first swipe / second swipe action
        accordingly.

        Developers notes:
        - 2nd swipe trigger may also happen, if playlist has already stopped playing
          --> Generally, treat as first swipe
        - 2nd swipe of same Card ID may also happen if a different song has been played in between from WebUI
          --> Treat as first swipe
        - With place-not-swipe: Card is placed on reader until playlist expieres. Music stop. Card is removed and
          placed again on the reader: Should be like first swipe
        - TODO: last_played_folder is restored after box start, so first swipe of last played card may look like second swipe
         """
        logger.debug(f"last_played_folder = {self.music_player_status['player_status']['last_played_folder']}")
        is_second_swipe = self.music_player_status['player_status']['last_played_folder'] == folder
        if self.second_swipe_action is not None and is_second_swipe:
            logger.debug('Calling second swipe action')
            self.second_swipe_action()
        else:
            logger.debug('Calling first swipe action')
            self.playlistaddplay(folder)

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

    def get_volume(self):
        """Get the current volume

        For volume control do not use directly, but use through the plugin 'volume',
        as the user may have configured a volume control manager other than MPD"""
        volume = self.mpd_retry_with_mutex(self.mpd_client.status).get('volume')
        return volume

    def set_volume(self, volume):
        """Set the volume

        For volume control do not use directly, but use through the plugin 'volume',
        as the user may have configured a volume control manager other than MPD"""
        self.mpd_retry_with_mutex(self.mpd_client.volume, volume)


class MpdVolumeCtrl:
    """The Volume Ctrl Service for the plugin 'volume'

    This allows volume ctrl through MPD rather than e.g. ALSA
    """

    def __init__(self, mpd_player_inst):
        self._mpd_player_inst = mpd_player_inst

    @plugs.tag
    def get_volume(self):
        return self._mpd_player_inst.get_volume()

    @plugs.tag
    def set_volume(self, volume):
        return self._mpd_player_inst.set_volume(volume)

    @plugs.tag
    def inc_volume(self, step=3):
        return self.set_volume(self.get_volume() + step)

    @plugs.tag
    def dec_volume(self, step=3):
        return self.set_volume(self.get_volume() - step)


class MpdVolumeCtrlBuilder:

    def __init__(self, mpd_player_inst):
        self._mpd_player_inst = mpd_player_inst
        self._instance = None

    def __call__(self, *args, **kwargs):
        if not self._instance:
            self._instance = MpdVolumeCtrl(self._mpd_player_inst)
        return self._instance


def get_music_directory(conf_file='/etc/mpd.conf'):
    """Extract the music directory from the mpd.conf file"""
    pattern = re.compile(r'^\s*music_directory\s*"(.*)"', re.I)
    directory = None
    with open(conf_file, 'r') as f:
        for line in f:
            res = pattern.match(line)
            if res:
                directory = res.group(1)
                break
    return directory


# ---------------------------------------------------------------------------
# Plugin Initializer / Finalizer
# ---------------------------------------------------------------------------

player_ctrl: PlayerMPD


@plugs.initialize
def initialize():
    global player_ctrl
    player_ctrl = PlayerMPD()
    plugs.register(player_ctrl, name='ctrl')
    volume = plugs.get('volume')
    volume.factory.register("mpd", MpdVolumeCtrlBuilder(player_ctrl))

    # Update mpc library
    library_update = cfg.setndefault('playermpd', 'library', 'update_on_startup', value=True)
    if library_update:
        player_ctrl.update()

    # Check user rights: Where to get the music directory from? Should be mpd.conf, right?
    audio_folder_path = None
    mpd_conf_file = cfg.setndefault('playermpd', 'mpd_conf', value='/etc/mpd.conf')
    try:
        audio_folder_path = get_music_directory(mpd_conf_file)
    except Exception as e:
        logger.error(f"Could not determine music library directory from '{mpd_conf_file}'")
        logger.error(f"Reason: {e.__class__.__name__}: {e}")

    library_check_user_rights = cfg.setndefault('playermpd', 'library', 'check_user_rights', value=True)
    if library_check_user_rights is True and audio_folder_path is not None:
        logger.info(f"Change user rights for {audio_folder_path}")
        misc.recursive_chmod(audio_folder_path, mode_files=0o666, mode_dirs=0o777)


@plugs.atexit
def atexit(**ignored_kwargs):
    global player_ctrl
    player_ctrl.exit()
