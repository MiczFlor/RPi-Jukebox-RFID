#!/usr/bin/env python3

import os
import os.path
import sys
import logging
import pathlib
import glob
import argparse
import subprocess
import requests
import xml.etree.ElementTree as ET
import urllib.parse

from pathlib import Path
from datetime import datetime
from shutil import copyfile
from subprocess import Popen, PIPE
from mpd import MPDClient

# LOGGING
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s [%(threadName)-12.12s] - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("../logs/debug.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger('rfid_trigger_play.py')
#logger.debug('Debug-Nachricht')
#logger.info('Info-Nachricht')
#logger.warning('Warnhinweis')
#logger.error('Fehlermeldung')
#logger.critical('Schwerer Fehler')

# CONNECT WITH MPD
# sudo apt-get install python3-mpd
# see: https://raspberrypi.stackexchange.com/questions/80428/no-module-named-mpd
# https://python-mpd2.readthedocs.io/en/latest/topics/getting-started.html

# Reads the card ID or the folder name with audio files
# from the command line (see Usage).
# Then attempts to get the folder name from the card ID
# or play audio folder content directly

# ADD / EDIT RFID CARDS TO CONTROL THE PHONIEBOX
# All controls are assigned to RFID cards in this
# file:
# settings/rfid_trigger_play.conf
# Please consult this file for more information.
# Do NOT edit anything in this file.

####################################################
# VARIABLES

# ignore files will these extensions in the results:
ignore_file_extension = ('.conf', '.ini', '.jpg', '.db', '.dat')

# The absolute path to the folder which contains all the scripts
path_scripts=str(pathlib.Path(__file__).parent.absolute())

# config file location
path_config_global = path_scripts + "/../settings/global.conf"
path_config_debug = path_scripts + "/../settings/debugLogging.conf"
path_config_rfid = path_scripts + "/../settings/rfid_trigger_play.conf"
path_dir_settings = path_scripts + "/../settings"
path_txt_latestID = path_scripts + "/../shared/latestID.txt"
path_dir_shortcuts = path_scripts + "/../shared/shortcuts"
path_dir_playlists = path_scripts + "/../playlists"

###################################
# parse variables from command line
parser = argparse.ArgumentParser()
parser.add_argument('-i', '--cardid', required=True)
parser.add_argument('-c', '--command')
parser.add_argument('-d', '--dir')
parser.add_argument('-v', '--value')
args = parser.parse_args()
logger.debug('arguments passed on to script:')
logger.debug(args)

# Set the date and time of now
now_string = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

# create the configuration file from sample - if it does not exist
if Path(path_config_rfid).is_file():
    # file exists
    logger.debug("rfid_trigger_play.conf exists")
else:
    # file does NOT exist
    logger.debug("rfid_trigger_play.conf does NOT exist, copying from settings dir")
    copyfile(path_dir_settings + "/rfid_trigger_play.conf.sample", path_config_rfid)

# Read config files for global, debug and rfid
conf = {}
# global config
with open(path_config_global) as myfile:
    for line in myfile:
        if not line.lstrip().startswith('#'):
            name, var = line.partition("=")[::2]
            conf[name.strip()] = var.strip()
# debugging config
with open(path_config_debug) as myfile:
    for line in myfile:
        if not line.lstrip().startswith('#'):
            name, var = line.partition("=")[::2]
            conf[name.strip()] = var.strip()
# debugging rfid
with open(path_config_rfid) as myfile:
    for line in myfile:
        if not line.lstrip().startswith('#'):
            name, var = line.partition("=")[::2]
            conf[name.strip()] = var.strip()
# strip " off values in dictionary conf
conf = {k: v.strip('"') for (k, v) in conf.items()}
if conf['DEBUG_rfid_trigger_play_sh'] == "TRUE":
    logger.debug('configuration found in conf files for global.conf, debugLogging.conf, rfid_trigger_play.conf:')
    logger.debug(conf)

#####################################################################
# We must have a card ID because the argument is required (see above)

# Write info to file, making it easer to monitor cards
with open(path_txt_latestID, "w") as f:
    f.write("Card ID '" + args.cardid + "' was used at '" + now_string + "'.")
with open(path_dir_settings + "/Latest_RFID", "w") as f:
    f.write(args.cardid)

# If the input is of 'special' use, don't treat it like a trigger to play audio.
# Special uses are for example volume changes, skipping, muting sound.
# NOTE: we need to check if the key exists, because older installations might not have
# the key in their copied config file. If we don't, the script will throw an error.
if('CMDSHUFFLE' in conf):
    if(args.cardid == conf['CMDSHUFFLE']):
        # toggles shuffle mode  (random on/off)
        subprocess.run("./playout_controls.sh -c=playershuffle", shell=True)
        quit() # exit script, because we did what we wanted to do
if('CMDMAXVOL30' in conf):
    if(args.cardid == conf['CMDMAXVOL30']):
        # limit volume to 30%
        subprocess.run("./playout_controls.sh -c=setmaxvolume -v=30", shell=True)
        quit() # exit script, because we did what we wanted to do
if('CMDMAXVOL50' in conf):
    if(args.cardid == conf['CMDMAXVOL50']):
        # limit volume to 50%
        subprocess.run("./playout_controls.sh -c=setmaxvolume -v=50", shell=True)
        quit() # exit script, because we did what we wanted to do
if('CMDMAXVOL75' in conf):
    if(args.cardid == conf['CMDMAXVOL75']):
        # limit volume to 75%
        subprocess.run("./playout_controls.sh -c=setmaxvolume -v=75", shell=True)
        quit() # exit script, because we did what we wanted to do
if('CMDMAXVOL80' in conf):
    if(args.cardid == conf['CMDMAXVOL80']):
        # limit volume to 80%
        subprocess.run("./playout_controls.sh -c=setmaxvolume -v=80", shell=True)
        quit() # exit script, because we did what we wanted to do
if('CMDMAXVOL85' in conf):
    if(args.cardid == conf['CMDMAXVOL85']):
        # limit volume to 85%
        subprocess.run("./playout_controls.sh -c=setmaxvolume -v=85", shell=True)
        quit() # exit script, because we did what we wanted to do
if('CMDMAXVOL90' in conf):
    if(args.cardid == conf['CMDMAXVOL90']):
        # limit volume to 90%
        subprocess.run("./playout_controls.sh -c=setmaxvolume -v=90", shell=True)
        quit() # exit script, because we did what we wanted to do
if('CMDMAXVOL95' in conf):
    if(args.cardid == conf['CMDMAXVOL95']):
        # limit volume to 95%
        subprocess.run("./playout_controls.sh -c=setmaxvolume -v=95", shell=True)
        quit() # exit script, because we did what we wanted to do
if('CMDMAXVOL100' in conf):
    if(args.cardid == conf['CMDMAXVOL100']):
        # limit volume to 100%
        subprocess.run("./playout_controls.sh -c=setmaxvolume -v=100", shell=True)
        quit() # exit script, because we did what we wanted to do
if('CMDMUTE' in conf):
    if(args.cardid == conf['CMDMUTE']):
        # amixer sset 'PCM' 0%
        subprocess.run("./playout_controls.sh -c=mute", shell=True)
        quit() # exit script, because we did what we wanted to do
if('CMDVOL30' in conf):
    if(args.cardid == conf['CMDVOL30']):
        # set volume to 30%
        subprocess.run("./playout_controls.sh -c=setvolume -v=30", shell=True)
        quit() # exit script, because we did what we wanted to do
if('CMDVOL50' in conf):
    if(args.cardid == conf['CMDVOL50']):
        # set volume to 50%
        subprocess.run("./playout_controls.sh -c=setvolume -v=50", shell=True)
        quit() # exit script, because we did what we wanted to do
if('CMDVOL75' in conf):
    if(args.cardid == conf['CMDVOL75']):
        # set volume to 75%
        subprocess.run("./playout_controls.sh -c=setvolume -v=75", shell=True)
        quit() # exit script, because we did what we wanted to do
if('CMDVOL80' in conf):
    if(args.cardid == conf['CMDVOL80']):
        # set volume to 80%
        subprocess.run("./playout_controls.sh -c=setvolume -v=80", shell=True)
        quit() # exit script, because we did what we wanted to do
if('CMDVOL85' in conf):
    if(args.cardid == conf['CMDVOL85']):
        # set volume to 85%
        subprocess.run("./playout_controls.sh -c=setvolume -v=85", shell=True)
        quit() # exit script, because we did what we wanted to do
if('CMDVOL90' in conf):
    if(args.cardid == conf['CMDVOL90']):
        # set volume to 90%
        subprocess.run("./playout_controls.sh -c=setvolume -v=90", shell=True)
        quit() # exit script, because we did what we wanted to do
if('CMDVOL95' in conf):
    if(args.cardid == conf['CMDVOL95']):
        # set volume to 95%
        subprocess.run("./playout_controls.sh -c=setvolume -v=95", shell=True)
        quit() # exit script, because we did what we wanted to do
if('CMDVOL100' in conf):
    if(args.cardid == conf['CMDVOL100']):
        # set volume to 100%
        subprocess.run("./playout_controls.sh -c=setvolume -v=100", shell=True)
        quit() # exit script, because we did what we wanted to do
if('CMDVOLUP' in conf):
    if(args.cardid == conf['CMDVOLUP']):
        # increase volume by x% set in Audio_Volume_Change_Step
        subprocess.run("./playout_controls.sh -c=volumeup", shell=True)
        quit() # exit script, because we did what we wanted to do
if('CMDVOLDOWN' in conf):
    if(args.cardid == conf['CMDVOLDOWN']):
        # decrease volume by x% set in Audio_Volume_Change_Step
        subprocess.run("./playout_controls.sh -c=volumedown", shell=True)
        quit() # exit script, because we did what we wanted to do
if('CMDSWITCHAUDIOIFACE' in conf):
    if(args.cardid == conf['CMDSWITCHAUDIOIFACE']):
        # switch between primary/secondary audio iFaces
        subprocess.run("./playout_controls.sh -c=switchaudioiface", shell=True)
        quit() # exit script, because we did what we wanted to do
if('CMDSTOP' in conf):
    if(args.cardid == conf['CMDSTOP']):
        # kill all running audio players
        subprocess.run("./playout_controls.sh -c=playerstop", shell=True)
        quit() # exit script, because we did what we wanted to do
if('CMDSHUTDOWN' in conf):
    if(args.cardid == conf['CMDSHUTDOWN']):
        # shutdown the RPi nicely
        subprocess.run("./playout_controls.sh -c=shutdown", shell=True)
        quit() # exit script, because we did what we wanted to do
if('CMDREBOOT' in conf):
    if(args.cardid == conf['CMDREBOOT']):
        # reboot the RPi 
        subprocess.run("./playout_controls.sh -c=reboot", shell=True)
        quit() # exit script, because we did what we wanted to do
if('CMDNEXT' in conf):
    if(args.cardid == conf['CMDNEXT']):
        # play next track in playlist 
        subprocess.run("./playout_controls.sh -c=playernext", shell=True)
        quit() # exit script, because we did what we wanted to do
if('CMDPREV' in conf):
    if(args.cardid == conf['CMDPREV']):
        # play previous track in playlist 
        subprocess.run("./playout_controls.sh -c=playerprev", shell=True)
        quit() # exit script, because we did what we wanted to do
if('CMDRANDCARD' in conf):
    if(args.cardid == conf['CMDRANDCARD']):
        # activate a random card 
        subprocess.run("./playout_controls.sh -c=randomcard", shell=True)
        quit() # exit script, because we did what we wanted to do
if('CMDRANDFOLD' in conf):
    if(args.cardid == conf['CMDRANDFOLD']):
        # play a random folder 
        subprocess.run("./playout_controls.sh -c=randomfolder", shell=True)
        quit() # exit script, because we did what we wanted to do
if('CMDRANDTRACK' in conf):
    if(args.cardid == conf['CMDRANDTRACK']):
        # jump to a random track in playlist (no shuffle mode required) 
        subprocess.run("./playout_controls.sh -c=randomtrack", shell=True)
        quit() # exit script, because we did what we wanted to do
if('CMDREWIND' in conf):
    if(args.cardid == conf['CMDREWIND']):
        # play the first track in playlist 
        subprocess.run("./playout_controls.sh -c=playerrewind", shell=True)
        quit() # exit script, because we did what we wanted to do
if('CMDSEEKFORW' in conf):
    if(args.cardid == conf['CMDSEEKFORW']):
        # jump 15 seconds ahead 
        subprocess.run("./playout_controls.sh -c=playerseek -v=+15", shell=True)
        quit() # exit script, because we did what we wanted to do
if('CMDSEEKBACK' in conf):
    if(args.cardid == conf['CMDSEEKBACK']):
        # jump 15 seconds back 
        subprocess.run("./playout_controls.sh -c=playerseek -v=-15", shell=True)
        quit() # exit script, because we did what we wanted to do
if('CMDPAUSE' in conf):
    if(args.cardid == conf['CMDPAUSE']):
        # pause current track 
        subprocess.run("./playout_controls.sh -c=playerpause", shell=True)
        quit() # exit script, because we did what we wanted to do
if('CMDPLAY' in conf):
    if(args.cardid == conf['CMDPLAY']):
        # play / resume current track 
        subprocess.run("./playout_controls.sh -c=playerplay", shell=True)
        quit() # exit script, because we did what we wanted to do
if('STOPAFTER5' in conf):
    if(args.cardid == conf['STOPAFTER5']):
        # stop player after -v minutes 
        subprocess.run("./playout_controls.sh -c=playerstopafter -v=5", shell=True)
        quit() # exit script, because we did what we wanted to do
if('STOPAFTER15' in conf):
    if(args.cardid == conf['STOPAFTER15']):
        # stop player after -v minutes 
        subprocess.run("./playout_controls.sh -c=playerstopafter -v=15", shell=True)
        quit() # exit script, because we did what we wanted to do
if('STOPAFTER30' in conf):
    if(args.cardid == conf['STOPAFTER30']):
        # stop player after -v minutes 
        subprocess.run("./playout_controls.sh -c=playerstopafter -v=30", shell=True)
        quit() # exit script, because we did what we wanted to do
if('STOPAFTER60' in conf):
    if(args.cardid == conf['STOPAFTER60']):
        # stop player after -v minutes 
        subprocess.run("./playout_controls.sh -c=playerstopafter -v=60", shell=True)
        quit() # exit script, because we did what we wanted to do
if('SHUTDOWNAFTER5' in conf):
    if(args.cardid == conf['SHUTDOWNAFTER5']):
        # shutdown RPi after -v minutes 
        subprocess.run("./playout_controls.sh -c=shutdownafter -v=5", shell=True)
        quit() # exit script, because we did what we wanted to do
if('SHUTDOWNAFTER15' in conf):
    if(args.cardid == conf['SHUTDOWNAFTER15']):
        # shutdown RPi after -v minutes 
        subprocess.run("./playout_controls.sh -c=shutdownafter -v=15", shell=True)
        quit() # exit script, because we did what we wanted to do
if('SHUTDOWNAFTER30' in conf):
    if(args.cardid == conf['SHUTDOWNAFTER30']):
        # shutdown RPi after -v minutes 
        subprocess.run("./playout_controls.sh -c=shutdownafter -v=30", shell=True)
        quit() # exit script, because we did what we wanted to do
if('SHUTDOWNAFTER60' in conf):
    if(args.cardid == conf['SHUTDOWNAFTER60']):
        # shutdown RPi after -v minutes 
        subprocess.run("./playout_controls.sh -c=shutdownafter -v=60", shell=True)
        quit() # exit script, because we did what we wanted to do
if('SHUTDOWNVOLUMEREDUCTION10' in conf):
    if(args.cardid == conf['SHUTDOWNVOLUMEREDUCTION10']):
        # reduce volume until shutdown in -v minutes 
        subprocess.run("./playout_controls.sh -c=shutdownvolumereduction -v=10", shell=True)
        quit() # exit script, because we did what we wanted to do
if('SHUTDOWNVOLUMEREDUCTION15' in conf):
    if(args.cardid == conf['SHUTDOWNVOLUMEREDUCTION15']):
        # reduce volume until shutdown in -v minutes 
        subprocess.run("./playout_controls.sh -c=shutdownvolumereduction -v=15", shell=True)
        quit() # exit script, because we did what we wanted to do
if('SHUTDOWNVOLUMEREDUCTION30' in conf):
    if(args.cardid == conf['SHUTDOWNVOLUMEREDUCTION30']):
        # reduce volume until shutdown in -v minutes 
        subprocess.run("./playout_controls.sh -c=shutdownvolumereduction -v=30", shell=True)
        quit() # exit script, because we did what we wanted to do
if('SHUTDOWNVOLUMEREDUCTION60' in conf):
    if(args.cardid == conf['SHUTDOWNVOLUMEREDUCTION60']):
        # reduce volume until shutdown in -v minutes 
        subprocess.run("./playout_controls.sh -c=shutdownvolumereduction -v=60", shell=True)
        quit() # exit script, because we did what we wanted to do
if('ENABLEWIFI' in conf):
    if(args.cardid == conf['ENABLEWIFI']):
        subprocess.run("./playout_controls.sh -c=enablewifi", shell=True)
        quit() # exit script, because we did what we wanted to do
if('DISABLEWIFI' in conf):
    if(args.cardid == conf['DISABLEWIFI']):
        subprocess.run("./playout_controls.sh -c=disablewifi", shell=True)
        quit() # exit script, because we did what we wanted to do
if('TOGGLEWIFI' in conf):
    if(args.cardid == conf['TOGGLEWIFI']):
        subprocess.run("./playout_controls.sh -c=togglewifi", shell=True)
        quit() # exit script, because we did what we wanted to do
if('CMDPLAYCUSTOMPLS' in conf):
    if(args.cardid == conf['CMDPLAYCUSTOMPLS']):
        subprocess.run("./playout_controls.sh -c=playlistaddplay -v=PhonieCustomPLS -d=PhonieCustomPLS", shell=True)
        quit() # exit script, because we did what we wanted to do
if('RECORDSTART600' in conf):
    if(args.cardid == conf['RECORDSTART600']):
        # start recorder for -v seconds 
        subprocess.run("./playout_controls.sh -c=recordstart -v=600", shell=True)
        quit() # exit script, because we did what we wanted to do
if('RECORDSTART60' in conf):
    if(args.cardid == conf['RECORDSTART60']):
        # start recorder for -v seconds 
        subprocess.run("./playout_controls.sh -c=recordstart -v=60", shell=True)
        quit() # exit script, because we did what we wanted to do
if('RECORDSTART10' in conf):
    if(args.cardid == conf['RECORDSTART10']):
        # start recorder for -v seconds 
        subprocess.run("./playout_controls.sh -c=recordstart -v=10", shell=True)
        quit() # exit script, because we did what we wanted to do
if('RECORDSTOP' in conf):
    if(args.cardid == conf['RECORDSTOP']):
        # start recorder for -v seconds 
        subprocess.run("./playout_controls.sh -c=recordstop", shell=True)
        quit() # exit script, because we did what we wanted to do
if('RECORDPLAYBACKLATEST' in conf):
    if(args.cardid == conf['RECORDPLAYBACKLATEST']):
        # play the latest recording 
        subprocess.run("./playout_controls.sh -c=recordplaylatest", shell=True)
        quit() # exit script, because we did what we wanted to do
if('CMDREADWIFIIP' in conf):
    if(args.cardid == conf['CMDREADWIFIIP']):
        # read the current WiFi IP address over the speaker 
        subprocess.run("./playout_controls.sh -c=readwifiipoverspeaker", shell=True)
        quit() # exit script, because we did what we wanted to do
if('CMDBLUETOOTHTOGGLE' in conf):
    if(args.cardid == conf['CMDBLUETOOTHTOGGLE']):
        subprocess.run("./playout_controls.sh -c=bluetoothtoggle -v=toggle", shell=True)
        quit() # exit script, because we did what we wanted to do

################################################################
# We checked if the card was a special command, seems it wasn't.
if conf['DEBUG_rfid_trigger_play_sh'] == "TRUE":
    log_message = "Card ID is not linked to a system command"
    logger.info(log_message)

# Now we expect it to be a trigger for one or more audio file(s).
# Let's look at the ID, write a bit of log information and then try to play audio.

# Look for human readable shortcut in folder 'shortcuts'
path_shortcut_id = path_dir_shortcuts + "/" + args.cardid

# check if CARDID has a text file by the same name - which would contain the human readable folder name    
if Path(path_shortcut_id).is_file():
    # file exists
    logger.debug("CARDID does exist as file in shortcuts folder")
    # Read human readable shortcut from file
    folder_name = Path(path_shortcut_id).read_text().strip()
    # Add info into the log, making it easer to monitor cards
    with open(path_txt_latestID, "a") as f:
        f.write("\nThis ID has been used before.")
else:
    # file does NOT exist
    logger.debug("CARDID does NOT exist as file in shortcuts folder")
    # Human readable shortcut does not exist, so create one with the content $CARDID
    # this file can later be edited manually over the samba network
    with open(path_shortcut_id, "w") as f:
        f.write(args.cardid)
    # Add info into the log, making it easer to monitor cards
    with open(path_txt_latestID, "a") as f:
        f.write("\nThis ID was used for the first time.")
    # Create human readable shortcut from card id
    folder_name = args.cardid

if conf['DEBUG_rfid_trigger_play_sh'] == "TRUE":
    logger.debug("Folder name found: " + folder_name)

##############################################################
# We should now have a folder name with the audio files.
# Either from prompt of from the card ID processing above

# check if
# - folder_name is not empty: if folder_name
# - folder_name exists: os.path.exists(path_folder_name)
# - folder_name is a directory: os.path.isdir(path_folder_name)

path_folder_name = conf['AUDIOFOLDERSPATH'] + "/" + folder_name.strip() + "/"

if folder_name and os.path.exists(path_folder_name) and os.path.isdir(path_folder_name):
    if not os.listdir(path_folder_name):
        # Directory is empty
        if conf['DEBUG_rfid_trigger_play_sh'] == "TRUE":
            logger.debug(path_folder_name + " does not exist - if not os.listdir(path_folder_name)")
    else:    
        # Directory is not empty -> PLAY THE FOLDER CONTENT
        if conf['DEBUG_rfid_trigger_play_sh'] == "TRUE":
            logger.debug(path_folder_name + " is not empty")

        # if we play a folder the first time, add some sensible information to the folder.conf file
        if os.path.exists(path_folder_name + "folder.conf"):
            if conf['DEBUG_rfid_trigger_play_sh'] == "TRUE":
                logger.debug("folder.conf file exists")
        else:
            # now we create a default folder.conf file by calling inc.writeFolderConfig.sh
            # with the command param createDefaultFolderConf
            # see inc.writeFolderConfig.sh for details
            if conf['DEBUG_rfid_trigger_play_sh'] == "TRUE":
                logger.debug("folder.conf does not exist, create one")
            subprocess.run("./inc.writeFolderConfig.sh -c=createDefaultFolderConf -d='" + folder_name + "'", shell=True)

        # get the name of the last folder and playlist played. 
        # As mpd doesn't store the name of the last playlist, 
        # we have to keep track of it via the Latest_Folder_Played / Latest_Playlist_Played file
        folder_last_played_name = Path(path_dir_settings + "/Latest_Folder_Played").read_text().strip()
        playlist_last_played_name = Path(path_dir_settings + "/Latest_Playlist_Played").read_text().strip()
        logger.info("folder_last_played_name: " + folder_last_played_name)
        logger.info("playlist_last_played_name: " + playlist_last_played_name)
        
        #####################
        # CREATE THE PLAYLIST
        
        playlist_name = folder_name.replace("/", " % ")

        # is it recursive (folder and subfolders)?
        if args.value == "recursive":
            # the folder_name directory and subdirectories
            dirs_audio = [] # directories
            # read folders recursively into list dirs_audio
            for dirpath, dirs, files in os.walk(path_folder_name):
            	dirs_audio += [dirpath]
            # replace subfolder slashes with " % "
            playlist_name = playlist_name + "-%RCRSV%"
        else:
            # only the folder_name directory
            dirs_audio = [path_folder_name]
            # replace subfolder slashes with " % "

        # go through folders
        playlist_files = [] # final playlist
        for dir_audio in dirs_audio:
            playlist_files_temp = [] # temporary playlist for each folder
            if Path(dir_audio + '/livestream.txt').is_file():
                #######################
                # check for livestreams
                file_check = dir_audio + '/livestream.txt'
                # add content of file to playlist
                file_content = open(file_check,'r').read().strip()
                playlist_files_temp = [file_content]
                # merge files into master playlist
                playlist_files += playlist_files_temp
            elif Path(dir_audio + '/podcast.txt').is_file():
                ###################
                # check for podcast
                file_check = dir_audio + '/podcast.txt'
                # add content of file to playlist
                # read URL content as text to var rss
                file_content = open(file_check,'r').read().strip()
                rss = requests.get(file_content).text
                # parse rss XML to find enclosure tags
                tree = ET.fromstring(rss)
                enclosures = tree.findall(".//enclosure") # Use the XPath to find all enclosure elements 
                for enclosure in  enclosures:
                    #url = enclosure.attrib['url'].split('?')[0] # cuts off the tail, but might not work for all URLs
                    #url = enclosure.attrib['url'] # complete URL
                    playlist_files_temp += [enclosure.attrib['url']]
                # merge files into master playlist
                playlist_files += playlist_files_temp
            elif Path(dir_audio + '/spotify.txt').is_file():
                ############################
                # check for spotify playlist
                file_check = dir_audio + '/spotify.txt'
                # add content of file to playlist
                file_content = open(file_check,'r').read().strip()
                playlist_files_temp = [file_content]
                # merge files into master playlist
                playlist_files += playlist_files_temp
            else:
                ##########################
                # normal files (finally :)
                playlist_files_all = glob.glob(dir_audio + '/*.*')
                # filter file extensions, see tuple with filter at the beginning of this file
                # NOTE: glob has exclusion options, research if this could be done above.
                # example excludes all files ending with a 't': 
                # playlist_files = glob.glob(path_name_audio + '/**/*.[!t]*', recursive=True)
                playlist_files_temp = [file for file in playlist_files_all if not file.endswith(ignore_file_extension)]
                # merge files into master playlist
                playlist_files += playlist_files_temp
        
        # now we need to make sure the local files work for Mopidy
        if conf['EDITION'].strip('"') == "plusSpotify":
            playlist_files = [urllib.parse.quote(file.replace(myvars['AUDIOFOLDERSPATH'].strip('"') + "/", 'local:track:')) for file in playlist_files]
            playlist_files = [file.replace('local%3Atrack%3A', 'local:track:') for file in playlist_files]

        # write file to playlists folder
        with open(path_dir_playlists + "/" + playlist_name + ".m3u", mode='wt', encoding='utf-8') as myfile:
            myfile.write('\n'.join(playlist_files))

        ##############
        # SECOND SWIPE

        # Available 
        # * RESTART => Re-start playlist 
        # * SKIPNEXT => Skip to next track 
        # * PAUSE => Toggle pause / play 
        # * PLAY => Resume playback 
        # * NOAUDIOPLAY => Ignore audio playout triggers, only system commands

        # Setting a VAR to start "play playlist from start"
        # This will be changed in the following checks "if this is the second swipe"
        playlist_play = "from_top"
        
        ####################################
        # Check if the second swipe happened
        
        if(playlist_name == playlist_last_played_name):
            if conf['DEBUG_rfid_trigger_play_sh'] == "TRUE":
                logger.info("Current playlist has been swiped twice")
            
            # Connect with mpd
            client = MPDClient()               # create client object
            client.timeout = 10                # network timeout in seconds (floats allowed), default: None
            client.idletimeout = None          # timeout for fetching the result of the idle command is handled seperately, default: None
            client.connect("localhost", 6600)  # connect to localhost:6600
            mpd_status = client.status()
            # mpd_status playing example:     {'volume': '67', 'repeat': '0', 'random': '0', 'single': '0', 'consume': '0', 'playlist': '32', 'playlistlength': '3', 'mixrampdb': '0.000000', 'state': 'play', 'song': '2', 'songid': '88', 'time': '1:2', 'elapsed': '0.754', 'bitrate': '128', 'duration': '2.324', 'audio': '44100:24:2'}
            # mpd_status not playing example: {'volume': '67', 'repeat': '0', 'random': '0', 'single': '0', 'consume': '0', 'playlist': '34', 'playlistlength': '3', 'mixrampdb': '0.000000', 'state': 'stop'}
            logger.debug("mpd_status:")
            logger.debug(mpd_status)
            # close and disconnect from mpd
            client.close()  # send the close command
            client.disconnect()
    
            if(conf['SECONDSWIPE'] == "RESTART"):
                if conf['DEBUG_rfid_trigger_play_sh'] == "TRUE":
                    logger.debug("RESTART => Re-start playlist")
                # PLAY playlist
                # do nothing, because the playlist will be played from top at the end of this file
                # because still: playlist_play = "from_top"
        
            elif(conf['SECONDSWIPE'] == "SKIPNEXT"):
                if conf['DEBUG_rfid_trigger_play_sh'] == "TRUE":
                    logger.debug("SKIPNEXT => Skip to next track")
                #  
                # We will not play the playlist but skip to the next track
                # $PATHDATA/playout_controls.sh -c=playernext
        
            elif(conf['SECONDSWIPE'] == "PAUSE"):
                if conf['DEBUG_rfid_trigger_play_sh'] == "TRUE":
                    logger.debug("PAUSE => Toggle pause / play")
                # if playlist_length == 0 do always play, bc first swipe after reboot
                if float(mpd_status['playlistlength']) == 0:
                    logger.debug("no playlist")
                else:
                    playlist_play = "ignore" # don't play playlist below
                    # check where we are and toggle
                    if mpd_status['state'] == "play":
                        # MPD state play
                        logger.debug("mpd playing")
                        subprocess.run("./playout_controls.sh -c=playerpause", shell=True)
                    else:
                        # MPD state NOT play
                        logger.debug("mpd NOT playing")
                        subprocess.run("./playout_controls.sh -c=playerplay", shell=True)
        
            elif(conf['SECONDSWIPE'] == "PLAY"):
                if conf['DEBUG_rfid_trigger_play_sh'] == "TRUE":
                    logger.debug("PLAY => Resume playback")
                # -c=playerplay will assure `resume playback`
                subprocess.run("./playout_controls.sh -c=playerplay", shell=True)
                playlist_play = "ignore" # don't play playlist below
        
            elif(conf['SECONDSWIPE'] == "NOAUDIOPLAY"):
                if conf['DEBUG_rfid_trigger_play_sh'] == "TRUE":
                    logger.debug("NOAUDIOPLAY => Ignore audio playout triggers, only system commands")
                # End of playlist? if no 'song' is given in 'mpd_status'
                if('song' not in mpd_status):
                    if conf['DEBUG_rfid_trigger_play_sh'] == "TRUE":
                        logger.debug("Playlist will be played, because playlist ended")
                    # do nothing, because the playlist will be played from top at the end of this file
                    # because still: playlist_play = "from_top"
                else:
                    playlist_play = "ignore" # don't play playlist below
        else:
            if conf['DEBUG_rfid_trigger_play_sh'] == "TRUE":
                logger.debug("Current playlist has not been swiped twice")
        
        # end of second swipe check
        ###########################
        
        # now see if we need to play the playlist or if it has been played already as part of second swipe?
        if(playlist_play == "from_top"):
            if conf['DEBUG_rfid_trigger_play_sh'] == "TRUE":
                logger.debug("Play playlist from top:" + playlist_name)
            # PLAY playlist
            # $PATHDATA/playout_controls.sh -c=playlistaddplay -v="${PLAYLISTNAME}" -d="${FOLDER}"
            subprocess.run("./playout_controls.sh -c=playlistaddplay -v=\"" + playlist_name + "\" -d=\"" + folder_name + "\"", shell=True)
            subprocess.run("sudo echo \"" + playlist_name + "\" > ../settings/Latest_Playlist_Played", shell=True)
            with open(path_dir_settings + "/Latest_RFID", "w") as f:
                f.write(playlist_name)
            subprocess.run("sudo chown pi:www-data ../settings/Latest_Playlist_Played", shell=True)
            subprocess.run("sudo chmod 777 ../settings/Latest_Playlist_Played", shell=True)

else:
    # Given directory doesn't exist
    if conf['DEBUG_rfid_trigger_play_sh'] == "TRUE":
        logger.debug(path_folder_name + " does not exist")

