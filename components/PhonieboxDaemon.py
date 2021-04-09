#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import threading
import sys, os.path
import signal
from time import sleep, time

import PhonieboxVolume
from player import PhonieboxPlayerMPD
from rpc.PhonieboxRpcServer import phoniebox_rpc_server
from PhonieboxNvManager import nv_manager
from rfid_reader.PhonieboxRfidReader import RFID_Reader
#from gpio_control import gpio_control

g_nvm = None

def signal_handler(signal, frame):
    """ catches signal and triggers the graceful exit """
    print("Caught signal {}, exiting...".format(signal))
    exit_gracefully(signal, frame)

def exit_gracefully(esignal, frame):
    print ("\nGot Signal {} ({}) \n {}".format(signal.Signals(esignal).name, esignal, frame))
    
    #stop all threads
    
    #save all nv
    g_nvm.save_all()
    #play stop (maybe)
    #shutdown ()
    
    print ("Exiting")
    sys.exit(0)

if __name__ == "__main__":

    # get absolute path of this script
    dir_path = os.path.dirname(os.path.realpath(__file__))
    defaultconfigFilePath = os.path.join(dir_path, 'phoniebox.conf')
    # if called directly, launch Phoniebox.py as rfid-reader daemon
    # treat the first argument as defaultconfigFilePath if given
    if len(sys.argv) <= 1:
        configFilePath = defaultconfigFilePath
    else:
        configFilePath = sys.argv[1]

    #parse config
    #gpio_config = configparser.ConfigParser(inline_comment_prefixes=";")
    #gpio_config_path = os.path.expanduser('/home/pi/RPi-Jukebox-RFID/settings/gpio_settings.ini')
    #gpio_config.read(config_path)

    #read config to dictionary?
    phoniebox_config = {}
    phoniebox_config['audiofolders_path'] = "../shared/"

    # Play Startup Sound
    volume_control_alsa = PhonieboxVolume.volume_control_alsa()
    startsound_thread = threading.Thread(target=volume_control_alsa.play_wave_file, args=["../shared/startupsound.wav"])
    startsound_thread.start()

    #Debug: List ALSA cards and mixers
    #PhonieboxVolume.list_cards()
    #PhonieboxVolume.list_mixers({ 'cardindex': 0 })

    g_nvm = nv_manager()
    

    #phoniebox music player status
    music_player_status = g_nvm.load("../shared/music_player_status.json")
    
    #card id database
    cardid_database = g_nvm.load("../settings/phoniebox_cardid_database.json")

    #initialize Phonibox objcts
    objects = {'volume':volume_control_alsa,
               'player':PhonieboxPlayerMPD.player_control(music_player_status,volume_control_alsa)}

    print ("Init Phonibox RPC Server ")
    rpcs = phoniebox_rpc_server(objects)
    if rpcs != None:
        rpcs.connect()

    #rfid_reader = RFID_Reader("RDM6300",{'numberformat':'card_id_float'})
    rfid_reader = RFID_Reader("Fake")
    #rfid_reader = None
    if rfid_reader is not None:
        print ("set db")
        rfid_reader.set_cardid_db(cardid_database)
        rfid_reader.reader.set_card_ids(list(cardid_database))     #just for Fake Reader
        print ("set thread")
        rfid_thread = threading.Thread(target=rfid_reader.run)
        #rfid_t.start()
    else:
        rfid_thread = None
    
    ##initialize gpio
    #gpio_config = configparser.ConfigParser(inline_comment_prefixes=";")
    gpio_config = None
    if gpio_config is not None:
        gpio_config_path = os.path.expanduser('/home/pi/RPi-Jukebox-RFID/settings/gpio_settings.ini')
        gpio_config.read(config_path)
    
        phoniebox_function_calls = function_calls.phoniebox_function_calls()
        gpio_controler = gpio_control(phoniebox_function_calls)

        devices = gpio_controler.get_all_devices(config)
        gpio_controler.print_all_devices()
        gpio_thread = threading.Thread(target=gpio_controler.gpio_loop)
    else:
        gpio_thread = None
    
    # signal.raise_signal(signum)
    # setup the signal listeners
    signal.signal(signal.SIGINT, exit_gracefully)
    signal.signal(signal.SIGTERM, exit_gracefully)
    
    #Start threads and RPC Server
    if rpcs is not None:
        if gpio_thread is not None:
            print ("Starting GPIO Thread")
            gpio_thread.start()
        if rfid_thread is not None:
            print ("Starting RFID Thread")
            rfid_thread.start()
        print ("Starting RPC Server")
        rpcs.server()