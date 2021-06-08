#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# CLI (command line interface) to access the Class for PlayoutControl

import os
import sys
import logging
import logging.config
import pathlib
import argparse
import subprocess
import alsaaudio
# regular expression
import re
from ruamel.yaml import YAML
from pprint import pprint
from functions import *
from PlayoutControl_Class import PlayoutControl

path_current_dir_absolute = str(pathlib.Path(__file__).parent.absolute())
path_dir_root = os.path.abspath(path_current_dir_absolute + "/..")
path_file_debuglog = os.path.abspath(path_dir_root + "/logs/debug.log")

# LOGGING
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s [%(filename)s:%(lineno)s - %(funcName)20s() ] - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(path_file_debuglog),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger('PlayoutControl CLI')

###################################
# parse variables from command line
parser = argparse.ArgumentParser()
parser.add_argument('-i', '--cardid')
parser.add_argument('-c', '--command')#, required=True)
parser.add_argument('-dn', '--dirpath')
parser.add_argument('-fn', '--filename')
parser.add_argument('-fp', '--filepath')
parser.add_argument('-pn', '--playlistname')
parser.add_argument('-pp', '--playlistpos')
parser.add_argument('-v', '--value')
parser.add_argument('-k', '--key')
args = parser.parse_args()
args_main = vars(args)
logger.debug('arguments passed on to script:')
logger.debug(args_main)


# Folder config file sys_switches:
# ./PlayoutControl_CLI.py -c switch_folder_RESUME -v OFF -d "ZZZ/SubMaster Whitespaces/bbb-AudioFormatsTest"
# ./PlayoutControl_CLI.py --command switch_folder_LOOP --value OFF --dirpath "ZZZ/SubMaster Whitespaces/bbb-AudioFormatsTest"
# ./PlayoutControl_CLI.py -c switch_folder_SINGLE -v OFF -d "ZZZ/SubMaster Whitespaces/bbb-AudioFormatsTest"
# ./PlayoutControl_CLI.py -c switch_folder_SHUFFLE -v OFF -d "ZZZ/SubMaster Whitespaces/bbb-AudioFormatsTest"

# ./PlayoutControl_CLI.py -c playout_pause_force -v 0

# ./PlayoutControl_CLI.py --command playout_position_save
# ./PlayoutControl_CLI.py -c playout_resume_play -d "ZZZ/SubMaster Whitespaces/bbb-AudioFormatsTest" --playlistname "ZZZ % SubMaster % bbb-AudioFormatsTest"
# ./PlayoutControl_CLI.py -c playlist_load -pn "ZZZ % SubMaster Whitespaces"
# ./PlayoutControl_CLI.py -c playlist_track_moveup -v 1
# ./PlayoutControl_CLI.py -c playlist_track_movedown -v 1
# ./PlayoutControl_CLI.py -c playlist_track_remove -v 1
# ./PlayoutControl_CLI.py -c playlist_clear
# ./PlayoutControl_CLI.py -c playlist_loop -v playlist
# ./PlayoutControl_CLI.py -c playlist_loop -v track
# ./PlayoutControl_CLI.py -c playlist_loop -v off
# ./PlayoutControl_CLI.py -c playlist_load_play -d "ZZZ/SubMaster Whitespaces/bbb-AudioFormatsTest" --playlistname "ZZZ % SubMaster % bbb-AudioFormatsTest"

# ./PlayoutControl_CLI.py -c volume_up
# ./PlayoutControl_CLI.py -c volume_down
# ./PlayoutControl_CLI.py -c volume_get
# ./PlayoutControl_CLI.py -c volume_set -v 80
# ./PlayoutControl_CLI.py -c volume_system_set
# ./PlayoutControl_CLI.py -c playout_mute_status
# ./PlayoutControl_CLI.py -c playout_mute_toggle

# ./PlayoutControl_CLI.py -c sys_volume_max_set -v 90
# ./PlayoutControl_CLI.py -c sys_volume_max_get
# ./PlayoutControl_CLI.py -c sys_volume_min_set -v 20
# ./PlayoutControl_CLI.py -c sys_volume_min_get

# ./PlayoutControl_CLI.py -c sys_config_value_set -k "hello" -v "world"
# ./PlayoutControl_CLI.py -c sys_config_value_get -k "CMDNEXT"

# ./PlayoutControl_CLI.py -c sys_volume_system_get
# ./PlayoutControl_CLI.py -c sys_volume_system_set -v 30

# ./PlayoutControl_CLI.py -c sys_volume_step_get
# ./PlayoutControl_CLI.py -c sys_volume_step_set -v 3

# ./PlayoutControl_CLI.py -c sys_idle_shutdown_get
# ./PlayoutControl_CLI.py -c sys_idle_shutdown_set -v 20

if(args_main['value']):
    logger.debug('Convert --value "%s" argument str int or float type.' % (args_main['value']))
    logger.debug('Current type: %s' % (type(args_main['value'])))
    if(is_int(args_main['value'])):
        args_main['value'] = int(args_main['value'])
    else:
        if(is_float(args_main['value'])):
            args_main['value'] = float(args_main['value'])
    logger.debug('New type: %s' % (type(args_main['value'])))

if(args_main['key']):
    logger.debug('Convert --key "%s" argument str int or float type.' % (args_main['key']))
    logger.debug('Current type: %s' % (type(args_main['key'])))
    if(is_int(args_main['key'])):
        args_main['key'] = int(args_main['key'])
    else:
        if(is_float(args_main['key'])):
            args_main['key'] = float(args_main['key'])
    logger.debug('New type: %s' % (type(args_main['key'])))

#####################################
# START actual command line interface

def PlayoutControl_cli(args_main):
    if(args_main['command']):
        # COMMAND given
        logger.debug('Try command: ' + args_main['command'])
        if(args_main['command'].startswith("switch_")):
            # SWITCH attempt
            args_func = {}
            args_func['command'] = args_main['command']
            args_func['value'] = args_main['value']
            args_func['dirpath'] = args_main['dirpath']
            playProcess.sys_switches(args_func)
            return

        if(args_main['command'] == "playout_position_save"):
            playProcess.playout_position_save()
            return

        if(args_main['command'] == "playout_resume_play"):
            args_func = {}
            args_func['playlistname'] = args_main['playlistname']
            args_func['dirpath'] = args_main['dirpath']
            # resume is an option - which would override settings in folder conf
            if(args_main['value'] == "RESUME"):
                args_func['value'] = args_main['value']
            playProcess.playout_resume_play(args_func)
            return

        if(args_main['command'] == "playlist_load_play"):
            args_func = {}
            args_func['playlistname'] = args_main['playlistname']
            args_func['dirpath'] = args_main['dirpath']
            playProcess.playout_playlist_load_play(args_func)
            return

        if(args_main['command'] == "playlist_clear"):
            playProcess.playout_playlist_clear()
            return
        if(args_main['command'] == "playlist_shuffle"):
            playProcess.playout_playlist_shuffle()
            return
        if(args_main['command'] == "playlist_replay"):
            playProcess.playout_playlist_replay()
            return
        if(args_main['command'] == "playlist_track_movedown"):
            playProcess.playout_playlist_track_movedown(args_main['value'])
            return
        if(args_main['command'] == "playlist_track_moveup"):
            playProcess.playout_playlist_track_moveup(args_main['value'])
            return
        if(args_main['command'] == "playlist_track_remove"):
            playProcess.playout_playlist_track_remove(args_main['value'])
            return
        if(args_main['command'] == "playlist_loop"):
            playProcess.playout_playlist_loop(args_main['value'])
            return
        if(args_main['command'] == "playlist_load"):
            playProcess.playout_playlist_load(args_main['playlistname'])
            return
        if(args_main['command'] == "playlist_track_append"):
            playProcess.playout_playlist_track_append(args_main['value'])
            return

        if(args_main['command'] == "volume_get"):
            print(playProcess.playout_volume_get())
            return
        if(args_main['command'] == "volume_set"):
            playProcess.playout_volume_set(args_main['value'])
            return
        if(args_main['command'] == "volume_system_set"):
            playProcess.playout_volume_system_set()
            return

        if(args_main['command'] == "volume_up"):
            playProcess.playout_volume_up()
            return
        if(args_main['command'] == "volume_down"):
            playProcess.playout_volume_down()
            return

        if(args_main['command'] == "playout_mute_toggle"):
            playProcess.playout_mute_toggle()
            return
        if(args_main['command'] == "playout_mute_status"):
            if(playProcess.playout_mute_status()):
                print("True is mute")
            else:
                print("False is not mute")
            return

        if(args_main['command'] == "sys_volume_max_set"):
            playProcess.sys_volume_max_set(args_main['value'])
            return
        if(args_main['command'] == "sys_volume_max_get"):
            print(playProcess.sys_volume_max_get())
            return

        if(args_main['command'] == "sys_volume_min_set"):
            playProcess.sys_volume_min_set(args_main['value'])
            return
        if(args_main['command'] == "sys_volume_min_get"):
            print(playProcess.sys_volume_min_get())
            return

        if(args_main['command'] == "sys_volume_system_set"):
            playProcess.sys_volume_system_set(args_main['value'])
            return
        if(args_main['command'] == "sys_volume_system_get"):
            print(playProcess.sys_volume_system_get())
            return

        if(args_main['command'] == "sys_idle_shutdown_set"):
            playProcess.sys_idle_shutdown_set(args_main['value'])
            return
        if(args_main['command'] == "sys_idle_shutdown_get"):
            print(playProcess.sys_idle_shutdown_get())
            return

        if(args_main['command'] == "sys_volume_step_set"):
            playProcess.sys_volume_step_set(args_main['value'])
            return
        if(args_main['command'] == "sys_volume_step_get"):
            print(playProcess.sys_volume_step_get())
            return

        if(args_main['command'] == "playout_stop"):
            playProcess.playout_stop()
            return
        if(args_main['command'] == "playout_next"):
            playProcess.playout_next()
            return
        if(args_main['command'] == "playout_restart"):
            playProcess.playout_restart()
            return
        if(args_main['command'] == "playout_pause_toggle"):
            playProcess.playout_pause_toggle()
            return
        if(args_main['command'] == "playout_pause_force"):
            if(args_main['value']):
                wait_seconds = int(args_main['value'])
            else:
                wait_seconds = 0
            playProcess.playout_pause_force(wait_seconds)
            return
        if(args_main['command'] == "playout_track_single"):
            playProcess.playout_track_single(args_main['value'])
            return

        if(args_main['command'] == "sys_config_value_set"):
            args_func = {}
            args_func['key'] = args_main['key']
            args_func['value'] = args_main['value']
            playProcess.sys_config_value_set(args_func)
            return
        if(args_main['command'] == "sys_config_value_get"):
            args_func = {}
            args_func['key'] = args_main['key']
            print(playProcess.sys_config_value_get(args_func))
            return

    else:
        logger.error('Error: no command given.')

playProcess = PlayoutControl(path_dir_root)

PlayoutControl_cli(args_main)

#print("Available methods:")
#method_list = [func for func in dir(playProcess) if callable(getattr(playProcess, func))]
#for i in method_list:
#    print("# " + i)
#pprint(vars(playProcess))


