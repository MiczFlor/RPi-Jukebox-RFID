#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import i2c_lcd_driver
from time import *
import time
import subprocess
import numpy
# import datetime
from mpd import MPDClient
# constants
mylcd = i2c_lcd_driver.lcd()
info_at_lines_play = [" "] * 4
info_at_lines_pause = [" "] * 4
info_at_lines_stop = [" "] * 4
info_at_lines_mpd_not_running = [" "] * 4
################# CHANGE YOUR SETTINGS HERE!!! ###########################################
## Display settings                                                                     ##
n_cols = 20                 # EDIT!!!  <-- number of cols your display has              ##
n_rows = 4                  # EDIT!!!  <-- number of rows your display has              ##
val_delay = 0.4             # EDIT!!!  <-- speed of the scolling text                   ##
start_stop_sc_delay = 4                                                                 ##
use_state_icons = "yes"   # choose "yes" if you want to use this                        ##
blinking_icons = "no"  # its an add-on for "use_state_icons", so "use_state_icons" must be "yes" ##
backlight_off_while_waiting = "yes"  # not active in state "play" and "pause"           ##
backlight_off_delay = 10  # Delay in seconds                                            ##
#### change the following strings to give your box a personal style                     ##
mpd_not_running_string = "MPD not running"                                              ##
music_stopped_string = "Music stopped!"                                                 ##
music_paused_string = "paused!"                                                         ##
##                                                                                      ##
################## CHANGE YOUR INFOS, WHICH WILL BE SHOWN ON THE DISPLAY #################
##                                                                                      ##
##  You can choose between the following infos:                                         ##
##  'date_and_time', 'artist', 'nothing', 'track_title', 'track_artist_title'           ##
##  'track_time', 'pause_string', 'stop_string', 'mpd_not_running_string'               ##
##  'track_time_and_number'                                                             ##
##                                                                                      ##
##  if you have less than 4 lines, you can leave the unused lines by default            ##
##                                                                                      ##
##  Choose infos while state is "play"                                                  ##
##                                                                                      ##
info_at_lines_play[0] = 'date_and_time'  # <-- Choose your favorite                    ##
info_at_lines_play[1] = 'artist'  # <-- Choose your favorite                           ##
info_at_lines_play[2] = 'title'  # <-- Choose your favorite                            ##
info_at_lines_play[3] = 'track_time_and_number'  # <-- Choose your favorite            ##
##                                                                                      ##
##  Choose infos while state is "pause"                                                 ##
##                                                                                      ##
info_at_lines_pause[0] = 'date_and_time'  # <-- Choose your favorite                    ##
info_at_lines_pause[1] = 'artist'  # <-- Choose your favorite                           ##
info_at_lines_pause[2] = 'title'  # <-- Choose your favorite                            ##
info_at_lines_pause[3] = 'pause_string'  # <-- Choose your favorite                     ##
##                                                                                      ##
##  Choose infos while state is "stop"                                                  ##
##                                                                                      ##
info_at_lines_stop[0] = 'date_and_time'  # <-- Choose your favorite                     ##
info_at_lines_stop[1] = 'nothing'  # <-- Choose your favorite                           ##
info_at_lines_stop[2] = 'nothing'  # <-- Choose your favorite                           ##
info_at_lines_stop[3] = 'stop_string'  # <-- Choose your favorite                       ##
##                                                                                      ##
##  Choose infos while state is "not_running"                                           ##
##                                                                                      ##
info_at_lines_mpd_not_running[0] = 'date_and_time'  # <-- Choose your favorite          ##
info_at_lines_mpd_not_running[1] = 'nothing'  # <-- Choose your favorite                ##
info_at_lines_mpd_not_running[2] = 'nothing'  # <-- Choose your favorite                ##
info_at_lines_mpd_not_running[3] = 'mpd_not_running_string'  # <-- Choose your favorite ##
##                                                                                      ##
##########################################################################################

## DO NOT EDIT!!!
clearline = " " * n_cols
string_track_title = " "
string_track_artist_title = " "
string_date_time = " "
track_number = " "
title = " "
playlist_length = " "
last_title = " "
i_counter = 0
state = " "
last_state = "not_running"
track_time = " "
current_time = time.time()
last_time = time.time()
if n_cols > 16:  # select date_string dependent on how many columns the display has (usually either 16 or 20 rows)
    date_string = "%d.%m.%Y %H:%M"
else:
    date_string = "%d.%m.%y %H:%M"  # save two character spaces  for displays showing only 16 characters per row

# lines that got to show
lines = [" " * n_cols] * n_rows
last_lines = [" " * n_cols] * n_rows

# User icons
user_icons = [
  [0b10000,  # Play
   0b11000,
   0b11100,
   0b11110,
   0b11100,
   0b11000,
   0b10000,
   0b00000],
  [0b00000,  # Pause
   0b11011,
   0b11011,
   0b11011,
   0b11011,
   0b11011,
   0b11011,
   0b00000],
  [0b00000,  # Stop
   0b11111,
   0b11111,
   0b11111,
   0b11111,
   0b11111,
   0b00000,
   0b00000],
  [0b00000,  # Offline
   0b00000,
   0b01010,
   0b00000,
   0b01110,
   0b10001,
   0b00000,
   0b00000]]


def print_changes(string_new, string_old, row):
    for pos in range(len(string_new)):
        if string_new[pos] != string_old[pos]:
            mylcd.lcd_display_string(string_new[pos], row, pos)


def fill_with_spaces(string1, length):
    if len(string1) <= length:
        return (string1 + " " * (length - len(string1)))
    else:
        return string1


def loop_string(string1, string2):
    my_long_string = string2
    title_max_length = n_cols - len(string1)  # max_len is dependent by len (track_number)
    position = numpy.clip((i_counter % (len(string2) - (title_max_length - 1) + 2 * start_stop_sc_delay)) - start_stop_sc_delay, 0, len(string2) - (title_max_length))
    scroll_text = my_long_string[position:(position + title_max_length)]
    return (string1 + scroll_text)


def print_nothing():
    return clearline


def print_pause_string():
    return (fill_with_spaces(music_paused_string, n_cols))


def print_stop_string():
    return (fill_with_spaces(music_stopped_string, n_cols))


def print_mpd_not_running_string():
    return (fill_with_spaces(mpd_not_running_string, n_cols))


def print_artist():
    if len(artist) <= n_cols:
        return fill_with_spaces(artist, n_cols)
    else:
        return loop_string("", artist)  # SC version


def print_track_title():
    # Write Track number & Title into the row of the display
    string_track_title = track_number + ":" + title
    if len(string_track_title) <= n_cols:
        return fill_with_spaces(string_track_title, n_cols)
    else:
        return loop_string(track_number + ":", title)  # SC version


def print_title():
    # Write Title into the row of the display
    if len(title) <= n_cols:
        return fill_with_spaces(title, n_cols)
    else:
        return loop_string("", title)  # SC version


def print_track_artist_title():
    string_track_artist_title = track_number + ":" + artist + " - " + title
    if len(string_track_artist_title) <= n_cols:
        return fill_with_spaces(string_track_artist_title, n_cols)
    else:
        return loop_string(track_number + ":", artist + " - " + title)  # SC version


def print_artist_title():
    string_artist_title = artist + " - " + title
    if len(string_artist_title) <= n_cols:
        return fill_with_spaces(string_artist_title, n_cols)
    else:
        return loop_string("", artist + " - " + title)  # SC version


def print_track_time():
    return fill_with_spaces(track_time, n_cols)


def print_track_time_and_number():
    song_of_playlist = track_number + "/" + playlist_length
    return (fill_with_spaces(track_time, n_cols))[:(n_cols - len(song_of_playlist))] + song_of_playlist


def print_date_time():
    return fill_with_spaces(time.strftime(date_string), n_cols)


def choose_line(info_text):
    switcher = {
            'pause_string': print_pause_string(),
            'stop_string': print_stop_string(),
            'mpd_not_running_string': print_mpd_not_running_string(),
            'track_title': print_track_title(),
            'track_artist_title': print_track_artist_title(),
            'artist_title': print_artist_title(),
            'artist': print_artist(),
            'title': print_title(),
            'date_and_time': print_date_time(),
            'nothing': print_nothing(),
            'track_time': print_track_time(),
            'track_time_and_number': print_track_time_and_number()
    }
    return switcher.get(info_text, fill_with_spaces("ERROR", n_cols))


def choose_icon(state):
    switcher = {
            'play': "\x00",
            'pause': "\x01",
            'stop': "\x02",
            'not_running': "\x03",
    }
    return switcher.get(state, " ")


def sec_to_min_and_sec(seconds):
    return (str('%d' % (int(seconds) / 60)) + ":" + str('%0.2d' % (int(seconds) % 60)))


######### BEGIN OF CODE ################################
##  init mpd-client
try:
    client = MPDClient()
    client.timeout = 0.3
    client.connect("localhost", 6600)                               #
except Exception:  # if reconnect isn't possible, client is not running  #
    print("mpd not avalible")
if use_state_icons == "yes":
    mylcd.lcd_load_custom_chars(user_icons)
try:
    while True:
        ##################### RESET ALL VALUES ##########################################
        mpd_info = " "                                                                  #
        track_number = "0"                                                              #
        title = " "                                                                     #
        album = " "                                                                     #
        artist = " "                                                                    #
        track_time = "0.0/0.0"                                                          #
        #################################################################################

        ########################## GET STATE ############################################
        try:                                                                            #
            client.ping()  # test if client is up                                    #
            status = client.status()                                                  #
            state = status['state']                                                   #
            current_song_infos = client.currentsong()                                 #
        except Exception:                                                               #
            try:  # if client is not connected, try to reconnect                     #
                client = MPDClient()                                            #
                client.timeout = 0.3                                              #
                client.connect("localhost", 6600)                               #
                status = client.status()                                          #
                state = status['state']                                           #
                current_song_infos = client.currentsong()                         #
            except Exception:  # if reconnect isn't possible, client is not running  #
                state = "not_running"                                             #
        # it is running, get more details                                               #
        #################################################################################
        ########### RESTART COUNTER, IF STATE CHANGED####################################

        if last_state != state:  # if state changed, the scrolltext starts at position 0 #
            i_counter = 0                                                           #
            mylcd.backlight(1)
        #################################################################################

        ########### GET INFOS, IF STATE IS "NOT_RUNNING" ################################
        if state == "not_running":                                                      #
            for row in range(n_rows):                                               #
                lines[row] = choose_line(info_at_lines_mpd_not_running[row])   #
        #################################################################################

        ########### GET INFOS, IF STATE IS "STOP" #######################################
        elif state == "stop":                                                           #
            for row in range(n_rows):                                               #
                lines[row] = choose_line(info_at_lines_stop[row])              #
        #################################################################################

        else:
            ########## GET MORE SONG-INFOS ####################################################
            # This section reads in certain album informations                                #
            #                                                                                 #
            ## read in track number                                                           #
            try:                                                                              #
                track_number = str(int(status['song'])+1)                                #
            except KeyError:                                                                  #
                track_number = "1"                                                        #
            ## read in playlistlength                                                         #
            try:                                                                              #
                playlist_length = status['playlistlength']                                #
            except KeyError:                                                                  #
                playlist_length = "1"                                                     #
            ## read in track title                                                            #
            try:                                                                              #
                title = current_song_infos['title']                                       #
                title = title.replace("\n", "").replace("ä", "\341").replace("ö", "\357").replace("ü", "\365").replace("ß", "\342").replace("Ä", "\341").replace("Ö", "\357").replace("Ü", "\365")  # weitere codes siehe https://www.mikrocontroller.net/topic/293125                           #
            except KeyError:                                                                  #
                title = ""                                                                #
            ## read in album title                                                            #
            try:                                                                              #
                album = current_song_infos['album']                                       #
                album = album.replace("\n", "").replace("ä", "\341").replace("ö", "\357").replace("ü", "\365").replace("ß", "\342").replace("Ä", "\341").replace("Ö", "\357").replace("Ü", "\365")  # weitere codes siehe https://www.mikrocontroller.net/topic/293125                           #
            except KeyError:                                                                  #
                album = ""                                                                #
            ## read in artist info                                                            #
            try:                                                                              #
                artist = current_song_infos['artist']                                     #
                artist = artist.replace("\n", "").replace("ä", "\341").replace("ö", "\357").replace("ü", "\365").replace("ß", "\342").replace("Ä", "\341").replace("Ö", "\357").replace("Ü", "\365")  # weitere codes siehe https://www.mikrocontroller.net/topic/293125                         #
            except KeyError:                                                                  #
                artist = ""                                                               #
            if (client.mpd_version) >= "0.20":
                try:                                                                              #
                    elapsed = status['elapsed'].split(".")[0]                                   #
                    duration = status['duration'].split(".")[0]                                 #
                    track_time = sec_to_min_and_sec(elapsed) + "/" + sec_to_min_and_sec(duration)  #
                except KeyError:                                                                  #
                    track_time = ""                                                           #
            else:                                                                                     #
                track_time = subprocess.check_output('mpc | head -n2 | tail -n1 | sed "s/  \+/ /g" | cut -d" " -f3', shell=True)
                track_time = track_time.replace("\n", "")                                         #
            ###########################################################################################

            ############# RESET GLOBAL COUNTER, IF TITLE CHANGED ############################
            if last_title != title:  # if title changed, the scrolltext starts at position 0 #
                i_counter = 0                                                           #
            #################################################################################

            ########### GET INFOS, IF STATE IS "PAUSE" ######################################
            if state == "pause":                                                            #
                for row in range(n_rows):                                               #
                    lines[row] = choose_line(info_at_lines_pause[row])             #
            #################################################################################

            ########### GET INFOS, IF STATE IS "PLAY" #######################################
            if state == "play":                                                             #
                for row in range(n_rows):                                               #
                    lines[row] = choose_line(info_at_lines_play[row])              #
            #################################################################################

        ################## EXACT CYCLE TIME ##################################################
        current_time = time.time()                                                             #
        # calculate real sleep-time - if cycle to long, use 0.0                              #
        extra_sleep = (max(val_delay - (current_time - last_time), 0.0))  # calculate real sleep     #
        time.sleep(extra_sleep)  # time the display stays as is before re-running the loop    #
        current_time = time.time()  # get current time after sleep                              #
        # print ("Cycle-time:"+str(current_time-last_time)) #only for debugging              #
        last_time = current_time  # save time for next cycle                                    #
        ######################################################################################

        ######################## ADD STATE ICONS #############################################
        ## add blinking state icon in first row                                              #
        if use_state_icons == "yes":                                                           #
            if blinking_icons == "yes":                                                   #
                if i_counter % 2 == 0:                                                   #
                    icon = choose_icon(state)                                      #
                else:                                                                #
                    icon = " "                                                     #
            else:                                                                        #
                icon = choose_icon(state)                                              #
            lines[0] = lines[0][:n_cols - 2] + " " + icon                                       #
        ######################################################################################

        ######################## DISPLAY OFF AFTER A WHILE ################################
        if (i_counter * val_delay) >= backlight_off_delay and backlight_off_while_waiting == "yes" and (state != "play" and state != "pause"):
            mylcd.backlight(0)
        else:
        ######################################################################################
        ######################## PRINT ALL CHANGES ON DISPLAY ################################
            for row in range(n_rows):                                                            #
                print_changes(lines[row], last_lines[row], row + 1)                             #
        ######################################################################################

        ####################### UPDATE COUNTER ###############################################
        i_counter += 1                                                                       #
        if i_counter >= 65000:                                                               #
            i_counter = 1000  # <-- not 0, cause the display could be off                 #
        ######################################################################################
        
        ####################### REMIND STUFF FOR NEXT CYCLE #################################
        last_state = state                                                                     #
        last_title = title                                                                     #
        for row in range(n_rows):                                                            #
            last_lines[row] = lines[row]                                                   #
        ######################################################################################


except KeyboardInterrupt:
    lines[0] = print_date_time()
    lines[1] = print_nothing()
    if n_rows >= 3:
        lines[2] = print_nothing()
    if n_rows >= 4:
        lines[3] = print_nothing()
    for row in range(n_rows):
        print_changes(lines[row], last_lines[row], row + 1)
    client.close()                     # send the close command
    client.disconnect()                # disconnect from the server
