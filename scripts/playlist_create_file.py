#!/usr/bin/env python3
import os
import sys
import glob
import argparse
from pathlib import Path
import requests
import xml.etree.ElementTree as ET
import urllib.parse

# Examples
# Run like this:
# ./playlist_create_file.py --name_audiofolder 'SubMaster Whitespaces' --name_playlist 'the test.m3u'
# For playlists created from folder and recursive subfolders:
# ./playlist_create_file.py --name_audiofolder 'SubMaster Whitespaces' --name_playlist 'the test.m3u' --recursive True 

####################################################
# VARIABLES
# ignore files will these extensions in the results:
ignore_file_extension = ('.conf', '.ini', '.jpg', '.db', '.dat')
# config file location
path_config ="../settings/global.conf"
path_debug_config ="../settings/debugLogging.conf"

###################################
# parse variables from command line
parser = argparse.ArgumentParser()
parser.add_argument('--name_audiofolder', required=True)
parser.add_argument('--name_playlist', required=True)
parser.add_argument('--recursive')
args = parser.parse_args()

# the variables we need to create and write the playlist:
name_audiofolder = args.name_audiofolder
name_playlist = args.name_playlist

print("# name_audiofolder: " + name_audiofolder); print("# name_playlist: " + name_playlist)

# reading config files
myvars = {}
# global config
with open(path_config) as myfile:
    for line in myfile:
        name, var = line.partition("=")[::2]
        myvars[name.strip()] = var.strip()
# debugging config
with open(path_debug_config) as myfile:
    for line in myfile:
        name, var = line.partition("=")[::2]
        myvars[name.strip()] = var.strip()

# get relevant vars from dictionary
phoniebox_edition = myvars['EDITION'].strip('"')
DEBUG_playlist_recursive_by_folder = myvars['DEBUG_playlist_recursive_by_folder_php'].strip('"')
path_name_audio = myvars['AUDIOFOLDERSPATH'].strip('"') + "/" + name_audiofolder + "/"
path_name_playlist = myvars['PLAYLISTSFOLDERPATH'].strip('"') + "/" + name_playlist

print("# Phoniebox edition: " + phoniebox_edition)
print("# Debug: " + DEBUG_playlist_recursive_by_folder)
print("# Path to audio: " + path_name_audio)
print("# Name of playlist: " + path_name_playlist)

if DEBUG_playlist_recursive_by_folder == "TRUE":
    with open("../logs/debug.log", "a") as myfile:
        myfile.write("########### SCRIPT playlist_create_file.py\n")


# Check if recursion or not.
# If not specified: playlist_recursive = False
playlist_recursive = False
if not args.recursive:
    playlist_recursive = False
    dirs_audio = [path_name_audio]
else:
    playlist_recursive = True
    dirs_audio = [] # directories
    # read folders recursively into list dirs_audio
    for dirpath, dirs, files in os.walk(path_name_audio):
    	dirs_audio += [dirpath]

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
if phoniebox_edition == "plusSpotify":
    playlist_files = [urllib.parse.quote(file.replace(myvars['AUDIOFOLDERSPATH'].strip('"') + "/", 'local:track:')) for file in playlist_files]
    playlist_files = [file.replace('local%3Atrack%3A', 'local:track:') for file in playlist_files]
    
# write file to playlists folder
with open(path_name_playlist, mode='wt', encoding='utf-8') as myfile:
    myfile.write('\n'.join(playlist_files))
