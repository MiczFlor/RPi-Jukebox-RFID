#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# requirements:
# pip3 install python-mpd2
# pip3 install pyalsaaudio
# YAML: https://yaml.readthedocs.io/en/latest/install.html

__name__ = "PlayoutControl"
__author__ = "Micz Flor"
__copyright__ = "Copyright 2021, the authors"
__license__ = "MIT"
__maintainer__ = "Micz Flor"
__email__ = "micz.flor@web.de"
__status__ = "Draft"

# OLD bash [= NEW python | > other script]
# shutdown >
# shutdownsilent >
# shutdownafter >
# shutdownvolumereduction >
# reboot >
# scan >
# mute = mute_toggle
# = mute_status
# = switch_folder_RESUME
# = switch_folder_LOOP
# = switch_folder_SINGLE
# = switch_folder_SHUFFLE
# setvolume = volume_set
# setmaxvolume = sys_volume_max_set
# setstartupvolume = sys_volume_system_get
# getstartupvolume = sys_volume_system_set
# setvolumetostartup = volume_system_set
# volumeup = volume_up
# volumedown = volume_down
# getchapters >
# getvolume = volume_get
# getmaxvolume = sys_volume_max_get
# setvolstep = volume_step_set
# getvolstep = volume_step_get
# playerstop = playout_stop
# ?playerstopafter
# playernext = playout_next
# playerprev = playout_prev
# ?playernextchapter
# ?playerprevchapter
# playerpause = playout_pause_toggle
# playerpauseforce = playout_pause_force
# ?playerplay
# playerremove = playlist_track_remove
# playermoveup = playlist_track_moveup
# playermovedown = playlist_track_movedown
# playerreplay = playout_restart
# playerrepeat = playlist_loop
# playershuffle = playlist_shuffle
# playlistclear = playlist_clear
# ?playlistaddplay
# playlistadd = playlist_load
# playlistappend = playlist_track_append (new: don't start playout)
# playlistreset = playlist_replay
# playsinglefile = playout_track_single
# getidletime = sys_idle_shutdown_get
# setidletime = sys_idle_shutdown_set
# disablewifi
# enablewifi
# togglewifi
# recordstart
# recordstop
# recordplaylatest
# readwifiipoverspeaker
# bluetoothtoggle
# switchaudioiface

# Available methods in alphabetical order:
# playout_mute_status
# playout_mute_toggle
# playout_next
# playout_pause_force
# playout_pause_toggle
# playout_playlist_clear
# playout_playlist_load
# playout_playlist_loop
# playout_playlist_replay
# playout_playlist_shuffle
# playout_playlist_track_append
# playout_playlist_track_movedown
# playout_playlist_track_moveup
# playout_playlist_track_remove
# playout_position_save
# playout_prev
# playout_restart
# playout_resume_play
# playout_stop
# playout_track_single
# playout_volume_down
# playout_volume_get
# playout_volume_set
# playout_volume_set_raw
# playout_volume_system_set
# playout_volume_up
# read_config_bash
# read_config_debug_dict
# read_config_folder_dict
# read_config_global_dict
# read_config_rfidcontrol_dict
# read_file_latest_folder_played
# read_file_volume_level
# read_folder_config_path
# read_mpd_vars
# sys_config_value_get
# sys_config_value_set
# sys_idle_shutdown_get
# sys_idle_shutdown_set
# sys_switches
# sys_volume_max_get
# sys_volume_max_set
# sys_volume_min_get
# sys_volume_min_set
# sys_volume_step_get
# sys_volume_step_set
# sys_volume_system_get
# sys_volume_system_set
# write_config_folder
# write_config_global

import os
import sys
import logging
import pathlib
import time
import subprocess
import alsaaudio
from ruamel.yaml import YAML
# from ruamel.yaml.compat import StringIO
from pathlib import Path
from mpd import MPDClient
from functions import *

path_current_dir_absolute = str(pathlib.Path(__file__).parent.absolute())
path_dir_root = os.path.abspath(path_current_dir_absolute + "/..")
path_file_debuglog = os.path.abspath(path_dir_root + "/logs/debug.log")


class PlayoutControl:

    def __init__(self, path_dir_root=path_dir_root):

        # vars
        self.path_dir_settings = os.path.abspath(path_dir_root + "/settings")
        self.path_config_global_bash = os.path.abspath(self.path_dir_settings + "/global.conf")
        self.path_config_global_yaml = os.path.abspath(self.path_dir_settings + "/global.conf.yaml")
        self.path_config_debug = os.path.abspath(self.path_dir_settings + "/debugLogging.conf")
        self.path_config_rfid = os.path.abspath(self.path_dir_settings + "/rfid_trigger_play.conf")

        path_file_debuglog = os.path.abspath(path_dir_root + "/logs/debug.log")
        # LOGGING
        logging.basicConfig(
            # level=logging.DEBUG,
            format='%(asctime)s [%(filename)s:%(lineno)s - %(funcName)20s() ] - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler(path_file_debuglog),
                logging.StreamHandler()
            ]
        )
        self.logger = logging.getLogger('PlayoutControl')
        self.logger.setLevel("NOTSET")

        # config
        self.conf = {}
        self.read_config_global_dict()

    def playout_playlist_loop(self, loop):

        # open new mpd_client to be used in this method:
        self.mpd_client = MPDClient()               # create client object
        self.mpd_client.timeout = 10                # network timeout in seconds (floats allowed), default: None
        self.mpd_client.idletimeout = None          # timeout for fetching the result of the idle command
        self.mpd_client.connect("localhost", 6600)  # connect to localhost:6600

        self.logger.info("Use argument ['track'|'playlist'|'off']")

        if(loop == "track" or loop == "single"):
            self.logger.debug("Loop single track '%s'" % (loop))
            self.mpd_client.repeat(1)
            self.mpd_client.single(1)
        elif(loop == "playlist" or loop == "all"):
            self.logger.debug("Loop playlist '%s'" % (loop))
            self.mpd_client.repeat(1)
            self.mpd_client.single(0)
        elif(loop == "off" or loop == "none"):
            self.logger.debug("Loop off '%s'" % (loop))
            self.mpd_client.repeat(0)
            self.mpd_client.single(0)
        else:
            self.logger.warning("Loop argument '%s' not valid." % (loop))

        # close and disconnect from mpd
        self.mpd_client.close()  # send the close command
        self.mpd_client.disconnect()

    def playout_playlist_load(self, playlist_name):
        '''
        Clears current playout queue and loads playlist from file (by name).
        '''

        # open new mpd_client to be used in this method:
        self.mpd_client = MPDClient()               # create client object
        self.mpd_client.timeout = 10                # network timeout in seconds (floats allowed), default: None
        self.mpd_client.idletimeout = None          # timeout for fetching the result of the idle command
        self.mpd_client.connect("localhost", 6600)  # connect to localhost:6600

        self.logger.debug("Clear current queue and load playlist")
        self.mpd_client.clear()
        self.mpd_client.load(playlist_name)

        # close and disconnect from mpd
        self.mpd_client.close()  # send the close command
        self.mpd_client.disconnect()

    def playout_playlist_replay(self):
        '''
        Re-start current playout queue from first track.
        '''

        # open new mpd_client to be used in this method:
        self.mpd_client = MPDClient()               # create client object
        self.mpd_client.timeout = 10                # network timeout in seconds (floats allowed), default: None
        self.mpd_client.idletimeout = None          # timeout for fetching the result of the idle command
        self.mpd_client.connect("localhost", 6600)  # connect to localhost:6600

        self.logger.debug("Re-start current playout queue from first track (pos: 1)")
        self.mpd_client.play(1)

        # close and disconnect from mpd
        self.mpd_client.close()  # send the close command
        self.mpd_client.disconnect()

    def playout_track_single(self, file_name):
        '''
        Clear playout queue, add file to queue and play.
        '''

        # open new mpd_client to be used in this method:
        self.mpd_client = MPDClient()               # create client object
        self.mpd_client.timeout = 10                # network timeout in seconds (floats allowed), default: None
        self.mpd_client.idletimeout = None          # timeout for fetching the result of the idle command
        self.mpd_client.connect("localhost", 6600)  # connect to localhost:6600

        self.logger.debug("Append file to end of current queue")
        self.mpd_client.clear()
        self.mpd_client.single(1)
        self.mpd_client.add(file_name)
        self.mpd_client.play()

        # close and disconnect from mpd
        self.mpd_client.close()  # send the close command
        self.mpd_client.disconnect()

    def playout_playlist_track_append(self, file_name):
        '''
        Add file to end of current playout queue.
        '''

        # open new mpd_client to be used in this method:
        self.mpd_client = MPDClient()               # create client object
        self.mpd_client.timeout = 10                # network timeout in seconds (floats allowed), default: None
        self.mpd_client.idletimeout = None          # timeout for fetching the result of the idle command
        self.mpd_client.connect("localhost", 6600)  # connect to localhost:6600

        self.logger.debug("Append file to end of current queue")
        self.mpd_client.add(file_name)

        # close and disconnect from mpd
        self.mpd_client.close()  # send the close command
        self.mpd_client.disconnect()

    def playout_playlist_shuffle(self):

        self.logger.debug("Shuffle loaded playlist")
        # open new mpd_client to be used in this method:
        self.mpd_client = MPDClient()               # create client object
        self.mpd_client.timeout = 10                # network timeout in seconds (floats allowed), default: None
        self.mpd_client.idletimeout = None          # timeout for fetching the result of the idle command
        self.mpd_client.connect("localhost", 6600)  # connect to localhost:6600

        self.mpd_client.shuffle()

        # close and disconnect from mpd
        self.mpd_client.close()  # send the close command
        self.mpd_client.disconnect()

    def playout_playlist_track_movedown(self, track_position):

        # open new mpd_client to be used in this method:
        self.mpd_client = MPDClient()               # create client object
        self.mpd_client.timeout = 10                # network timeout in seconds (floats allowed), default: None
        self.mpd_client.idletimeout = None          # timeout for fetching the result of the idle command
        self.mpd_client.connect("localhost", 6600)  # connect to localhost:6600

        track_position_new = track_position + 1
        self.logger.debug("Move in playlist track from pos '%s' to '%s'" % (track_position, track_position_new))
        self.mpd_client.move(track_position, track_position_new)

        # close and disconnect from mpd
        self.mpd_client.close()  # send the close command
        self.mpd_client.disconnect()
        
    def playout_playlist_track_moveup(self, track_position):

        # open new mpd_client to be used in this method:
        self.mpd_client = MPDClient()               # create client object
        self.mpd_client.timeout = 10                # network timeout in seconds (floats allowed), default: None
        self.mpd_client.idletimeout = None          # timeout for fetching the result of the idle command
        self.mpd_client.connect("localhost", 6600)  # connect to localhost:6600
        
        track_position_new = track_position - 1
        self.logger.debug("Move in playlist track from pos '%s' to '%s'" % (track_position, track_position_new))
        self.mpd_client.move(track_position, track_position_new)

        # close and disconnect from mpd
        self.mpd_client.close()  # send the close command
        self.mpd_client.disconnect()

    def playout_playlist_track_remove(self, track_position):

        # open new mpd_client to be used in this method:
        self.mpd_client = MPDClient()               # create client object
        self.mpd_client.timeout = 10                # network timeout in seconds (floats allowed), default: None
        self.mpd_client.idletimeout = None          # timeout for fetching the result of the idle command
        self.mpd_client.connect("localhost", 6600)  # connect to localhost:6600
        
        self.logger.debug("Remove from playlist track from pos : '%s'" % (track_position))
        self.mpd_client.delete(track_position)

        # close and disconnect from mpd
        self.mpd_client.close()  # send the close command
        self.mpd_client.disconnect()

    def playout_playlist_clear(self):

        self.playout_position_save()

        # open new mpd_client to be used in this method:
        self.mpd_client = MPDClient()               # create client object
        self.mpd_client.timeout = 10                # network timeout in seconds (floats allowed), default: None
        self.mpd_client.idletimeout = None          # timeout for fetching the result of the idle command
        self.mpd_client.connect("localhost", 6600)  # connect to localhost:6600
        
        self.mpd_client.clear()

        # close and disconnect from mpd
        self.mpd_client.close()  # send the close command
        self.mpd_client.disconnect()

    def playout_next(self):

        # open new mpd_client to be used in this method:
        self.mpd_client = MPDClient()               # create client object
        self.mpd_client.timeout = 10                # network timeout in seconds (floats allowed), default: None
        self.mpd_client.idletimeout = None          # timeout for fetching the result of the idle command
        self.mpd_client.connect("localhost", 6600)  # connect to localhost:6600

        if(self.mpd_client.status()['state'] == "play"):
            # unmute if mute
            if(self.read_file_volume_level()):
                # audio off => bc file
                self.logger.debug(
                    "Mute? True! -> Action: unmute. Audio level read from 'Audio_Volume_Level' : '%s'" %
                    (self.audio_volume_level_file))
                volume_now = self.audio_volume_level_file
                # set volume
                self.playout_volume_set(int(volume_now))
                # remove file 'Audio_Volume_Level'
                os.remove(self.path_dir_settings + "/Audio_Volume_Level")
            # skip to next track
            self.mpd_client.next()

        # close and disconnect from mpd
        self.mpd_client.close()  # send the close command
        self.mpd_client.disconnect()

    def playout_prev(self):

        # open new mpd_client to be used in this method:
        self.mpd_client = MPDClient()               # create client object
        self.mpd_client.timeout = 10                # network timeout in seconds (floats allowed), default: None
        self.mpd_client.idletimeout = None          # timeout for fetching the result of the idle command
        self.mpd_client.connect("localhost", 6600)  # connect to localhost:6600

        if(self.mpd_client.status()['state'] == "play"):
            # unmute if mute
            if(self.read_file_volume_level()):
                # audio off => bc file
                self.logger.debug(
                    "Mute? True! -> Action: unmute. Audio level read from 'Audio_Volume_Level' : '%s'" %
                    (self.audio_volume_level_file))
                volume_now = self.audio_volume_level_file
                # set volume
                self.playout_volume_set(int(volume_now))
                # remove file 'Audio_Volume_Level'
                os.remove(self.path_dir_settings + "/Audio_Volume_Level")
            # skip to previous track
            self.mpd_client.prev()

        # close and disconnect from mpd
        self.mpd_client.close()  # send the close command
        self.mpd_client.disconnect()

    def playout_restart(self):

        # open new mpd_client to be used in this method:
        self.mpd_client = MPDClient()               # create client object
        self.mpd_client.timeout = 10                # network timeout in seconds (floats allowed), default: None
        self.mpd_client.idletimeout = None          # timeout for fetching the result of the idle command
        self.mpd_client.connect("localhost", 6600)  # connect to localhost:6600

        if(self.mpd_client.status()['state'] == "play"):
            # unmute if mute
            if(self.read_file_volume_level()):
                # audio off => bc file
                self.logger.debug(
                    "Mute? True! -> Action: unmute. Audio level read from 'Audio_Volume_Level' : '%s'" %
                    (self.audio_volume_level_file))
                volume_now = self.audio_volume_level_file
                # set volume
                self.playout_volume_set(int(volume_now))
                # remove file 'Audio_Volume_Level'
                os.remove(self.path_dir_settings + "/Audio_Volume_Level")
            # skip to next track
            self.mpd_client.play(0)  # 0 or 1 ???

        # close and disconnect from mpd
        self.mpd_client.close()  # send the close command
        self.mpd_client.disconnect()

    def playout_stop(self):

        # save postiton if need be
        self.playout_position_save()

        # open new mpd_client to be used in this method:
        self.mpd_client = MPDClient()               # create client object
        self.mpd_client.timeout = 10                # network timeout in seconds (floats allowed), default: None
        self.mpd_client.idletimeout = None          # timeout for fetching the result of the idle command
        self.mpd_client.connect("localhost", 6600)  # connect to localhost:6600

        # stop mpd
        self.logger.debug("mpd initial 'status state': " + self.mpd_client.status()['state'])
        self.mpd_client.stop()
        self.logger.debug("mpd stopped 'status state': " + self.mpd_client.status()['state'])

        # close and disconnect from mpd
        self.mpd_client.close()  # send the close command
        self.mpd_client.disconnect()

    def playout_position_save(self):

        self.logger.debug("Saving position: 1. file in playlist and 2. position in file")
        # "saveposition" can be written without knowing the dirpath of the audio folder.
        # The dirpath is read from the latest settings/Latest_Folder_Played
        if(self.read_file_latest_folder_played()):
            self.logger.debug("Latest_Folder_Played: " + self.folder_name)
            # self.read_folder_config_path(self.folder_name)
            if(self.read_config_folder_dict(self.folder_name)):
                if(self.conf['folder']['RESUME'] == "ON" or self.conf['folder']['SINGLE'] == "ON"):
                    self.read_config_global_dict()  # read global and debug conf
                    self.read_mpd_vars()  # read vars from mpd
                    folder_config_new = {}  # *new* variables for folder.conf
                    # elapsed time => mpd_status['elapsed']
                    folder_config_new['ELAPSED'] = float(self.mpd_status['elapsed'])
                    # current file name played  => mpd_currentsong['file']
                    folder_config_new['CURRENTFILENAME'] = self.mpd_currentsong['file']
                    folder_config_new['PLAYSTATUS'] = "Stopped"
                    self.write_config_folder(self.folder_config_path, folder_config_new)
                else:
                    self.logger.warning("WARNING: not writing values bc folder conf 'RESUME' nor 'SINGLE' == 'ON'.")
            else:
                self.logger.error("ERROR: directory given in 'Latest_Folder_Played' not found.")
        else:
            self.logger.error("ERROR: settings file 'Latest_Folder_Played' not found or readable")

    def playout_resume_play(self, args_func):

        if(args_func['dirpath']):
            self.logger.debug("args_func['dirpath']: '%s'" % (args_func['dirpath']))
        else:
            self.logger.error("ERROR: args_func['dirpath'] not given.")
            sys.exit()
        if(args_func['playlistname']):
            self.logger.debug("args_func['playlistname']: '%s'" % (args_func['playlistname']))
        else:
            self.logger.warning("WARNING: args_func['playlistname'] not given.")

        # folder conf read
        self.read_config_folder_dict(args_func['dirpath'])
        self.logger.debug("self.conf['folder']:")
        self.logger.debug(self.conf['folder'])

        # read (usual) vars from mpd:
        self.read_mpd_vars()
        # open new mpd_client to be used in this method:
        self.mpd_client = MPDClient()               # create client object
        self.mpd_client.timeout = 10                # network timeout in seconds (floats allowed), default: None
        self.mpd_client.idletimeout = None          # timeout for fetching the result of the idle command
        self.mpd_client.connect("localhost", 6600)  # connect to localhost:6600
        # take a look
        mpd_playlistfind = self.mpd_client.playlistfind("file", self.conf['folder']['CURRENTFILENAME'])
        self.logger.debug("self.mpd_client.playlistfind('file', self.conf['folder']['CURRENTFILENAME'])")
        self.logger.debug(mpd_playlistfind)
        self.logger.debug("self.conf['folder']['CURRENTFILENAME']: '%s'" % (self.conf['folder']['CURRENTFILENAME']))
        self.logger.debug(mpd_playlistfind)

        if(self.conf['folder']['RESUME'] == "ON" or self.conf['folder']['SINGLE'] == "ON"):

            # We know *resume* is an issue (RESUME|SINGLE==ON). What are our ideal options?
            #   1.  Playlist was stopped with 'playout_saveposition' => we have a good folder conf file
            #       TRUE IF self.conf['folder']['PLAYSTATUS'] == "Stopped"
            #   2.  Found position in playlist for self.conf['folder']['CURRENTFILENAME']
            #       FALSE IF len(mpd_playlistfind) == 0
            #   3.  Found elapsed time of file from last playout
            #       TRUE IF self.conf['folder']['ELAPSED'] (exists and float)
            # Otherwise we assume that the playlist was played until the end.
            # In this case, start the playlist from beginning

            if(self.conf['folder']['PLAYSTATUS'] == "Stopped"):
                self.logger.debug("Folder conf file seems valid (self.conf['folder']['PLAYSTATUS'] == 'Stopped').")
                # Did we get the playlist position of the file from mpd?

                if(len(mpd_playlistfind) == 0):
                    self.logger.debug("No playlist position. Try loading playlist.")
                    if(args_func['playlistname']):
                        self.mpd_client.clear()                         # clear cue
                        self.mpd_client.load(args_func['playlistname'])  # load playlist
                        self.mpd_client.play()                          # play
                    else:
                        self.logger.error("ERROR: No playlistname, no position. We know too little to do anything.")

                else:
                    # If the file is found, it is played from ELAPSED, otherwise start playlist from beginning.
                    # WARNING: what if the file is in the playlist more than once???
                    #          Currently we take the first (0) match: mpd_playlistfind[0]['pos']
                    self.logger.debug(
                        "Playlist position: mpd_playlistfind[0]['pos']: '%s'" %
                        (mpd_playlistfind[0]['pos']))
                    self.mpd_client.play(mpd_playlistfind[0]['pos'])  # playlist from position
                    # seek time in current file (needs float() ???)
                    self.mpd_client.seekcur(float(self.conf['folder']['ELAPSED']))

                # NOTE: If the playlist ends without any stop/shutdown/new swipe (you've listened to all of the tracks),
                # there's no savepos event and we would resume at the last position anywhere in the playlist.

            else:
                self.logger.debug("Folder conf file seems invalid (self.conf['folder']['PLAYSTATUS'] != 'Stopped').")
                # We assume that the playlist ran to the end the last time and start from the beginning.
                # Or: playlist is playing and we've got a play from playlist position command.
                if(args_func['playlistname']):
                    self.mpd_client.clear()                         # clear cue
                    self.mpd_client.load(args_func['playlistname'])  # load playlist
                    self.mpd_client.play()                          # play
                else:
                    self.mpd_client.play()  # play whatever is loaded
        else:
            # if no last played data exists (resume play disabled),
            # we play the playlist from the beginning or the given playlist position
            if(args_func['playlistname']):
                self.mpd_client.clear()                         # clear cue
                self.mpd_client.load(args_func['playlistname'])  # load playlist
                self.mpd_client.play()                          # play
            else:
                self.mpd_client.play()                          # play whatever is loaded

        if(self.mpd_client.status()['state'] == "play"):
            # Save to folder conf that we are "Playing" (not "Stopped")
            folder_config_new = {}  # *new* variables for folder.conf
            folder_config_new['PLAYSTATUS'] = "Playing"
            self.write_config_folder(self.folder_config_path, folder_config_new)

        # close and disconnect from mpd
        self.mpd_client.close()  # send the close command
        self.mpd_client.disconnect()

    def write_config_folder(self, folder_config_path, folder_config_new):

        # folder_config_new must be a dictionary like {'CURRENTFILENAME': 'filename', 'ELAPSED': '0'}
        # Will create folder conf file, if none exists

        # folder conf default values: read from sample config file
        # Note: this sample config file needs to be extended as new features are implemented
        folder_config_default = {}
        folder_config_default = self.read_config_bash([path_dir_root + "/misc/sampleconfigs/folder.conf.sample"])

        # read current values (if file exists)
        folder_config_current = {}
        if(Path(folder_config_path).is_file()):
            self.logger.debug("Current folder conf file found.")
            folder_config_current = self.read_config_bash([folder_config_path])
        else:
            self.logger.debug("Current folder conf file NOT found: no values read from file.")

        # folder config current values
        self.logger.debug("File config pairs in order of: default, current, new:")
        self.logger.debug(folder_config_default)
        self.logger.debug(folder_config_current)
        self.logger.debug(folder_config_new)

        # merge vars into new config file
        # 1. default 2. current 3. new into merged
        folder_config_merged = {}
        for key, value in folder_config_default.items():
            folder_config_merged[key] = value
        for key, value in folder_config_current.items():
            folder_config_merged[key] = value
        for key, value in folder_config_new.items():
            folder_config_merged[key] = value
        self.logger.debug("File Config pairs to be written:")
        self.logger.debug(folder_config_merged)

        folder_config_write = open(self.folder_config_path, "w")
        for key, value in folder_config_merged.items():
            folder_config_write.write(key + '="' + str(value) + '"\n')

        # make it readable and writeable for everyone
        subprocess.run(['chmod', '0766', self.folder_config_path])

    def read_config_bash(self, paths_all):

        # paths_all must be a list like [a, b, c]
        conf = {}
        for path_config in paths_all:
            # read config
            with open(path_config) as myfile:
                for line in myfile:
                    if not line.lstrip().startswith('#'):
                        name, var = line.partition("=")[::2]
                        conf[name.strip()] = var.strip()
        # strip " off values in dictionary conf
        conf = {k: v.strip('"') for (k, v) in conf.items()}
        return conf

    def read_mpd_vars(self):

        # MPD status / Connect with mpd
        self.mpd_client = MPDClient()               # create client object
        self.mpd_client.timeout = 10                # network timeout in seconds (floats allowed), default: None
        self.mpd_client.idletimeout = None          # timeout for fetching the result of the idle command
        self.mpd_client.connect("localhost", 6600)  # connect to localhost:6600
        self.mpd_status = self.mpd_client.status()
        self.mpd_currentsong = self.mpd_client.currentsong()
        # self.client.clear()
        self.mpd_playlistinfo = self.mpd_client.playlistinfo()
        # close and disconnect from mpd
        self.mpd_client.close()  # send the close command
        self.mpd_client.disconnect()

        self.logger.debug("mpd_client.status() in self.mpd_status:")
        self.logger.debug(self.mpd_status)

        # elapsed time => mpd_status['elapsed']
        # mpd reports an elapsed time only if the audio is playing or is paused. Check if we got an elapsed time
        if "elapsed" not in self.mpd_status:
            self.mpd_status['elapsed'] = float(0)
        # current file name played  => mpd_currentsong['file']
        if "file" not in self.mpd_currentsong:
            self.mpd_currentsong['file'] = "False"

    ######################################
    # GLOBAL CONFIG set new values for key

    def sys_config_value_set(self, args_func):
        self.logger.debug("GLOBAL CONFIG change values for keys")
        if(args_func['key']):
            self.logger.debug('key:' + args_func['key'])
            if(args_func['value']):
                self.logger.debug('value:' + args_func['value'])
                if(args_func['key'] in self.conf['global']):
                    self.conf['global'][args_func['key']] = args_func['value']
                    self.logger.error("Writing global config file.")
                    self.write_config_global()
                else:
                    self.logger.error('ERROR: key "' + args_func['key'] + '" not valid')
            else:
                self.logger.error('ERROR: switch requires --value')
        else:
            self.logger.error('ERROR: switch requires --key')

    def sys_config_value_get(self, args_func):
        self.logger.debug("GLOBAL CONFIG return value for key")
        if(args_func['key']):
            self.logger.debug('key:' + args_func['key'])
            if(args_func['key'] in self.conf['global']):
                self.logger.debug('value:' + self.conf['global'][args_func['key']])
                return(self.conf['global'][args_func['key']])
            else:
                self.logger.error('ERROR: key "' + args_func['key'] + '" not valid')
                return(False)
        else:
            self.logger.error('ERROR: switch requires --key')
            return(False)

    ##################################
    # SWITCHES folder config: on / off

    def sys_switches(self, args_func):
        self.logger.debug("SWITCH start")
        if(args_func['value']):
            self.logger.debug('value:' + args_func['value'])
            if(
               args_func['command'] == "switch_folder_RESUME" or
               args_func['command'] == "switch_folder_SHUFFLE" or
               args_func['command'] == "switch_folder_LOOP" or
               args_func['command'] == "switch_folder_SINGLE"
               ):
                if(args_func['value'] == "ON" or args_func['value'] == "OFF"):
                    if(args_func['dirpath']):
                        if(self.read_folder_config_path(args_func['dirpath'])):
                            self.logger.debug(
                                'Try switching folder conf "' +
                                args_func['command'] +
                                '" to "' +
                                args_func['value'] +
                                '" in "' +
                                args_func['dirpath'] +
                                '"')
                            self.logger.debug('folder_config_path: "' + self.folder_config_path)

                            # save an additional read / write to SD card by checking if value already set
                            # Not checking if value already set, because we are saving more read / write if:
                            # * attempt to write using self.write_config_folder()
                            # * create on attempt, if not found in self.write_config_folder()
                            conf_key = args_func['command'].rsplit('_', 1)[1]  # key in conf file
                            folder_config_new = {}  # *new* variables for folder.conf
                            folder_config_new[conf_key] = args_func['value']
                            self.write_config_folder(self.folder_config_path, folder_config_new)

                        else:
                            self.logger.error('ERROR: --dirpath "' + args_func['dirpath'] + '" is not a directory')
                    else:
                        self.logger.error('ERROR: switch requires --dirpath [relative path to directory]')
                else:
                    self.logger.error('ERROR: switch requires --value [ON|OFF]')
            else:
                self.logger.error('ERROR: command "' + args_func['command'] + '" not valid')
        else:
            self.logger.error('ERROR: switch requires --value')

    ######################################################
    # read (return) values (as string, int, float or dict)
    # all values are assigned to self AND(!) returned or False
    # e.g. read_folder_config_path          => string: absolute path to config file for folder
    # e.g. read_config_global_dict          => dictionary: config as key => value pairs
    # e.g. read_file_latest_folder_played   => string: path of latest folder (or subfolder with relative path)

    def read_folder_config_path(self, dirpath):
        folder_config_path = self.conf['global']['AUDIO_FOLDER_PATH'] + "/" + dirpath
        self.logger.debug("folder_config_path: " + folder_config_path)
        if(Path(folder_config_path).is_dir()):
            self.folder_config_path = folder_config_path + "/folder.conf"
            return(self.folder_config_path)
        else:
            return(False)

    def read_file_volume_level(self):

        # Get folder name of currently played audio
        try:
            with open(self.path_dir_settings + "/Audio_Volume_Level", 'r') as file:
                self.audio_volume_level_file = file.read().strip()
                return(self.audio_volume_level_file)
        except IOError:
            self.logger.error("ERROR: file not found: " + self.path_dir_settings + "/Audio_Volume_Level")
            return(False)

    def read_file_latest_folder_played(self):

        # Get folder name of currently played audio
        try:
            with open(self.path_dir_settings + "/Latest_Folder_Played", 'r') as file:
                self.folder_name = file.read().strip()
                return(self.folder_name)
        except IOError:
            self.logger.error("ERROR: file not found: " + self.path_dir_settings + "/Latest_Folder_Played")
            return(False)

    def read_config_folder_dict(self, dirpath):

        if(self.read_folder_config_path(dirpath)):
            self.logger.debug("Try to read file config: " + self.folder_config_path)
            try:
                with open(self.folder_config_path) as f:
                    self.logger.debug("TRUE (file found): '%s' (value: '%s')" % (self.folder_config_path, f))
            except IOError:
                self.logger.debug("FALSE (file not found): " + self.folder_config_path)
                # create default folder conf file => dict for attributes empty
                self.write_config_folder(self.folder_config_path, {})

            # read config file for folder
            self.conf['folder'] = self.read_config_bash([self.folder_config_path])
            return(self.conf['folder'])
        else:
            return(False)

    def read_config_debug_dict(self):

        # this is a wrapper for reading config vars global and debugging
        # currently read_config_bash is used to read the vars from version 2.x
        self.conf['debug'] = self.read_config_bash([self.path_config_debug])

    def read_config_global_dict(self):

        # this is a wrapper for reading config vars global and debugging
        # currently read_config_bash is used to read the vars from version 2.x

        # legacy bash format exists? Yes: read, convert, delete
        if(Path(self.path_config_global_bash).is_file()):
            self.logger.debug("Found legacy global.conf file from bash")
            self.conf['global'] = self.read_config_bash([self.path_config_global_bash])

            # Start the future now...: convert some of the old naming into new naming
            if('AUDIOVOLCHANGESTEP' in self.conf['global']):
                self.conf['global']['VOL_CHANGE_STEP'] = self.conf['global'].pop('AUDIOVOLCHANGESTEP')
            if('AUDIOVOLMAXLIMIT' in self.conf['global']):
                self.conf['global']['VOL_LIMIT_MAX'] = self.conf['global'].pop('AUDIOVOLMAXLIMIT')
            if('AUDIOVOLMINLIMIT' in self.conf['global']):
                self.conf['global']['VOL_LIMIT_MIN'] = self.conf['global'].pop('AUDIOVOLMINLIMIT')
            if('AUDIOVOLSTARTUP' in self.conf['global']):
                self.conf['global']['VOL_LEVEL_SYSTEM'] = self.conf['global'].pop('AUDIOVOLSTARTUP')
            if('VOLCHANGEIDLE' in self.conf['global']):
                self.conf['global']['VOL_CHANGE_IF_IDLE'] = self.conf['global'].pop('VOLCHANGEIDLE')
            if('VOLUMEMANAGER' in self.conf['global']):
                self.conf['global']['VOL_MANAGER'] = self.conf['global'].pop('VOLUMEMANAGER')
            if('AUDIOFOLDERSPATH' in self.conf['global']):
                self.conf['global']['AUDIO_FOLDER_PATH'] = self.conf['global'].pop('AUDIOFOLDERSPATH')
            if('AUDIOIFACEACTIVE' in self.conf['global']):
                self.conf['global']['AUDIO_IFACE_ACTIVE'] = self.conf['global'].pop('AUDIOIFACEACTIVE')
            if('AUDIOIFACENAME' in self.conf['global']):
                self.conf['global']['AUDIO_IFACE_NAME'] = self.conf['global'].pop('AUDIOIFACENAME')
            if('IDLETIMESHUTDOWN' in self.conf['global']):
                self.conf['global']['SHUTDOWN_IDLE_TIME'] = self.conf['global'].pop('IDLETIMESHUTDOWN')

        # self.write_config_global()
        return(self.conf['global'])

    def write_config_global(self):

        sorted_dict = {k: self.conf['global'][k] for k in sorted(self.conf['global'])}
        folder_config_write = open(self.path_config_global_bash, "w")
        for key, value in sorted_dict.items():
            folder_config_write.write(key + '="' + str(value) + '"\n')

        # YAML config file
        yaml = YAML()
        with open(self.path_config_global_yaml, 'w') as outfile:
            yaml.dump(self.conf['global'], outfile)

    def read_config_rfidcontrol_dict(self):

        # this is a wrapper for reading all config vars
        # currently read_config_bash is used to read the vars from version 2.x
        self.conf['rfidcontrol'] = self.read_config_bash([self.path_config_rfid])
        return(self.conf['rfidcontrol'])

    def playout_volume_get(self):

        if(self.conf['global']['VOL_MANAGER'] == "amixer"):
            my_alsa = alsaaudio.Mixer(self.conf['global']['AUDIO_IFACE_NAME'])
            volume_current = my_alsa.getvolume()[0]  # Get the current Volume - returns list, take first => [0]
            self.logger.debug(
                "VOL_MANAGER: '%s' volume_current: '%s'" %
                (self.conf['global']['VOL_MANAGER'], volume_current))
            return(volume_current)
        elif(self.conf['global']['VOL_MANAGER'] == "mpd"):
            self.read_mpd_vars()
            volume_current = self.mpd_status['volume']  # ??? needs checking, currently returns -1
            self.logger.debug(
                "VOL_MANAGER: '%s' volume_current: '%s'" %
                (self.conf['global']['VOL_MANAGER'], volume_current))
            return(volume_current)
        else:
            self.logger.error("VOL_MANAGER: '" + self.conf['global']['VOL_MANAGER'] + "' not valid")
            return(False)

    def playout_volume_set(self, volume_new):

        if(not is_int(volume_new)):
            self.logger.debug("volume_new '" + volume_new + "' is not an integer number.")
            return(False)
        else:
            self.logger.debug("volume_new '%s' is an integer number." % (volume_new))
            if(
                int(self.conf['global']['VOL_LIMIT_MAX']) > volume_new and
                volume_new > int(self.conf['global']['VOL_LIMIT_MIN'])
            ):
                self.logger.debug(
                    "volume_new %s within limits: %s - %s" %
                    (volume_new,
                        self.conf['global']['VOL_LIMIT_MIN'],
                        self.conf['global']['VOL_LIMIT_MAX']))
            else:
                self.logger.debug(
                    "volume_new %s outside limits: %s - %s" %
                    (volume_new,
                    self.conf['global']['VOL_LIMIT_MIN'],
                    self.conf['global']['VOL_LIMIT_MAX']))
                if(volume_new > int(self.conf['global']['VOL_LIMIT_MAX'])):
                    volume_new = int(self.conf['global']['VOL_LIMIT_MAX'])
                if(volume_new < int(self.conf['global']['VOL_LIMIT_MIN'])):
                    volume_new = int(self.conf['global']['VOL_LIMIT_MIN'])
                self.logger.debug("volume_new set to: '%s'" % (volume_new))

            self.playout_volume_set_raw(volume_new)

    def playout_volume_set_raw(self, volume_new):

        self.logger.debug("Setting volume_new '%s' without any further checks." % volume_new)
        if(self.conf['global']['VOL_MANAGER'] == "amixer"):
            self.logger.debug("VOL_MANAGER: 'amixer'")
            my_alsa = alsaaudio.Mixer(self.conf['global']['AUDIO_IFACE_NAME'])
            my_alsa.setvolume(volume_new)
            return(volume_new)
        elif(self.conf['global']['VOL_MANAGER'] == "mpd"):
            self.logger.debug("VOL_MANAGER: 'mpd' for playout_volume_set not yet implemented")
            #  echo -e setvol $VOL_LIMIT_MAX\\nclose | nc -w 1 localhost 6600
            return(volume_new)
        else:
            self.logger.error("ERROR: VOL_MANAGER: '" + self.conf['global']['VOL_MANAGER'] + "' not valid")
            return(False)

    def playout_volume_system_set(self):
        self.playout_volume_set(int(self.conf['global']['VOL_LEVEL_SYSTEM']))

    def sys_volume_max_get(self):
        return(self.conf['global']['VOL_LIMIT_MAX'])

    def sys_volume_max_set(self, volume_max_new):

        # change settings for 'maximum jukebox volume' and (if needed) 'system volume on startup'
        if(volume_max_new <= int(self.conf['global']['VOL_LIMIT_MIN'])):
            self.logger.error("ERROR: new volume maximum limit < minimum limit (%s < %s)" %
                (volume_max_new, self.conf['global']['VOL_LIMIT_MIN']))
        else:
            if(volume_max_new > 100):
                volume_max_new = 100
            self.conf['global']['VOL_LIMIT_MAX'] = volume_max_new

            # reduce current volume?
            volume_now = int(self.playout_volume_get())
            if(volume_max_new < volume_now):
                self.playout_volume_set(volume_max_new)

            # reduce 'system volume on startup' in config?
            if(volume_max_new < int(self.conf['global']['VOL_LEVEL_SYSTEM'])):
                self.conf['global']['VOL_LEVEL_SYSTEM'] = volume_max_new

            # save config
            self.write_config_global()

    def sys_volume_min_get(self):
        return(self.conf['global']['VOL_LIMIT_MIN'])

    def sys_volume_min_set(self, volume_min_new):

        # change settings for 'minimum jukebox volume' and (if needed) 'system volume on startup'
        if(volume_min_new >= int(self.conf['global']['VOL_LIMIT_MAX'])):
            self.logger.error("ERROR: new volume minimum limit > maximum limit (%s > %s)" %
                (volume_min_new, self.conf['global']['VOL_LIMIT_MAX']))
        else:
            if(volume_min_new < 0):
                volume_min_new = 0
            self.conf['global']['VOL_LIMIT_MIN'] = volume_min_new

            # increase current volume?
            volume_now = int(self.playout_volume_get())
            if(volume_min_new > volume_now):
                self.playout_volume_set(volume_min_new)

            # save config
            self.write_config_global()

    def sys_volume_step_get(self):
        return(self.conf['global']['VOL_CHANGE_STEP'])

    def sys_volume_step_set(self, volume_change_step):

        if(volume_change_step > 100):
            volume_change_step = 100
        if(volume_change_step < 1):
            volume_change_step = 1

        self.logger.debug("Volume system level changed from '%s' to '%s'" %
            (self.conf['global']['VOL_CHANGE_STEP'], volume_change_step))
        self.conf['global']['VOL_CHANGE_STEP'] = volume_change_step
        self.write_config_global()

    def sys_volume_system_get(self):
        return(self.conf['global']['VOL_LEVEL_SYSTEM'])

    def sys_volume_system_set(self, volume_level_system):

        if(volume_level_system > 100):
            volume_level_system = 100
        if(volume_level_system < 0):
            volume_level_system = 0
        if(volume_level_system > int(self.conf['global']['VOL_LIMIT_MAX'])):
            volume_level_system = int(self.conf['global']['VOL_LIMIT_MAX'])

        self.logger.debug("Volume system level changed from '%s' to '%s'" %
            (self.conf['global']['VOL_LEVEL_SYSTEM'], volume_level_system))
        self.conf['global']['VOL_LEVEL_SYSTEM'] = volume_level_system
        self.write_config_global()

    def sys_idle_shutdown_get(self):
        return(self.conf['global']['SHUTDOWN_IDLE_TIME'])

    def sys_idle_shutdown_set(self, idle_shutdown_minutes):

        if(idle_shutdown_minutes > 600):
            idle_shutdown_minutes = 600
        if(idle_shutdown_minutes < 0):
            idle_shutdown_minutes = 0

        self.logger.debug("Shutdown after idle for '%s' minutes (changed from '%s')." %
            (idle_shutdown_minutes, self.conf['global']['SHUTDOWN_IDLE_TIME']))
        self.conf['global']['SHUTDOWN_IDLE_TIME'] = idle_shutdown_minutes
        self.write_config_global()
        # also write to single file => this is read from daemon scripts/idle-watchdog.sh
        self.logger.debug(self.path_dir_settings + "/Idle_Time_Before_Shutdown")
        write_audio_volume_level_file = open(self.path_dir_settings + "/Idle_Time_Before_Shutdown", "w")
        write_audio_volume_level_file.write(str(idle_shutdown_minutes))

        # restart service to apply the new value
        self.logger.critical("Not implemented yet: restart service to apply the new value.")
        # sudo systemctl restart phoniebox-idle-watchdog.service &

    def playout_volume_up(self):

        # must know playout state from mpd
        self.read_mpd_vars()
        self.logger.debug("mpd playout state (in status) : " + self.mpd_status['state'])
        if(
            self.conf['global']['VOL_CHANGE_IF_IDLE'] == "FALSE" or
            self.conf['global']['VOL_CHANGE_IF_IDLE'] == "OnlyDown"
        ):
            if(self.mpd_status['state'] != "play"):
                self.logger.error("Exit, bc not allowed to change volume when playout stopped.")
                sys.exit()

        # see if we can read the audio level from the file
        if(self.read_file_volume_level()):
            # audio off => bc file
            volume_now = self.audio_volume_level_file
            self.logger.debug("Audio level read from 'Audio_Volume_Level' : " + self.audio_volume_level_file)
            # set volume
            # remove file 'Audio_Volume_Level'
            os.remove(self.path_dir_settings + "/Audio_Volume_Level")
        else:
            # audio on => bc no file Audio_Volume_Level
            volume_now = self.playout_volume_get()
            self.logger.debug("'Audio_Volume_Level' file for audio level not available for reading.")
        # set new volume level
        volume_new = int(volume_now) + int(self.conf['global']['VOL_CHANGE_STEP'])
        if(volume_new > 100):
            volume_new = 100
        self.logger.debug("Calculated volume_new: " + str(volume_new))
        volume_set = self.playout_volume_set(volume_new)
        self.logger.debug("volume set: " + str(volume_set))

    def playout_volume_down(self):

        # must know playout state from mpd
        self.read_mpd_vars()
        self.logger.debug("mpd playout state (in status) : " + self.mpd_status['state'])
        if(
            self.conf['global']['VOL_CHANGE_IF_IDLE'] == "FALSE" or
            self.conf['global']['VOL_CHANGE_IF_IDLE'] == "OnlyUp"
        ):
            if(self.mpd_status['state'] != "play"):
                self.logger.error("Exit, because: not allowed to change volume when playout stopped.")
                sys.exit()

        # see if we can read the audio level from the file
        if(self.read_file_volume_level()):
            # audio off => bc file
            volume_now = self.audio_volume_level_file
            self.logger.debug("Audio level read from 'Audio_Volume_Level' : " + self.audio_volume_level_file)
            # set volume
            # remove file 'Audio_Volume_Level'
            os.remove(self.path_dir_settings + "/Audio_Volume_Level")
        else:
            # audio on => bc no file Audio_Volume_Level
            volume_now = self.playout_volume_get()
            self.logger.debug("'Audio_Volume_Level' file for audio level not available for reading.")
        # set new volume level
        volume_new = int(volume_now) - int(self.conf['global']['VOL_CHANGE_STEP'])
        if(volume_new < 0):
            volume_new = 0
        self.logger.debug("Calculated volume_new: " + str(volume_new))
        volume_set = self.playout_volume_set(volume_new)
        self.logger.debug("volume set: " + str(volume_set))

    def playout_pause_toggle(self):

        # open new mpd_client to be used in this method:
        self.mpd_client = MPDClient()               # create client object
        self.mpd_client.timeout = 10                # network timeout in seconds (floats allowed), default: None
        self.mpd_client.idletimeout = None          # timeout for fetching the result of the idle command
        self.mpd_client.connect("localhost", 6600)  # connect to localhost:6600

        if(self.mpd_client.status()['state'] == "play"):
            self.mpd_client.pause()
        else:
            # unmute if mute
            if(self.read_file_volume_level()):
                # audio off => bc file
                self.logger.debug(
                    "Mute? True! -> Action: unmute. Audio level read from 'Audio_Volume_Level' : '%s'" %
                    (self.audio_volume_level_file))
                volume_now = self.audio_volume_level_file
                # set volume
                self.playout_volume_set(int(volume_now))
                # remove file 'Audio_Volume_Level'
                os.remove(self.path_dir_settings + "/Audio_Volume_Level")
            self.mpd_client.play()

        # close and disconnect from mpd
        self.mpd_client.close()  # send the close command
        self.mpd_client.disconnect()

    def playout_pause_force(self, seconds_wait):

        # the waiting was part of the original shell command
        # don't know what it was needed for
        # possibly comment out and see if somebody complains?
        time.sleep(int(seconds_wait))

        # open new mpd_client to be used in this method:
        self.mpd_client = MPDClient()               # create client object
        self.mpd_client.timeout = 10                # network timeout in seconds (floats allowed), default: None
        self.mpd_client.idletimeout = None          # timeout for fetching the result of the idle command
        self.mpd_client.connect("localhost", 6600)  # connect to localhost:6600

        self.mpd_client.pause()

        # close and disconnect from mpd
        self.mpd_client.close()  # send the close command
        self.mpd_client.disconnect()

    def playout_mute_toggle(self):

        # see if we can read the audio level from the file
        if(self.read_file_volume_level()):
            # audio off => bc file
            self.logger.debug(
                "Mute? True! -> Action: unmute. Audio level read from 'Audio_Volume_Level' : %s" %
                (self.audio_volume_level_file))
            volume_now = self.audio_volume_level_file
            # set volume
            self.playout_volume_set(int(volume_now))
            # remove file 'Audio_Volume_Level'
            os.remove(self.path_dir_settings + "/Audio_Volume_Level")
        else:
            # audio on => bc no file Audio_Volume_Level
            self.logger.debug("Mute? False! -> Action: mute. 'Audio_Volume_Level' file not available for reading.")
            # write value to file
            volume_now = self.playout_volume_get()
            self.logger.debug(self.path_dir_settings + "/Audio_Volume_Level")
            write_audio_volume_level_file = open(self.path_dir_settings + "/Audio_Volume_Level", "w")
            write_audio_volume_level_file.write(str(volume_now))
            # mute => volume 0%
            # use method playout_volume_set_raw to force ZERO as volume
            # method playout_volume_set does change the argument to match range set in config
            self.playout_volume_set_raw(0)

    def playout_mute_status(self):

        # mute == 'Audio_Volume_Level' exists, else: not muted
        if(Path(self.path_dir_settings + "/Audio_Volume_Level").is_file()):
            self.logger.debug("Mute? True!")
            return(True)
        else:
            self.logger.debug("Mute? False!")
            return(False)
