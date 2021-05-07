#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import threading
import sys, os.path
import signal
import argparse
import configparser
from time import sleep, time

import PhonieboxVolume
import PhonieboxSystem
from player import PhonieboxPlayerMPD
from rpc.PhonieboxRpcServer import PhonieboxRpcServer
from PhonieboxNvManager import nv_manager
from rfid_reader.PhonieboxRfidReader import RFID_Reader
#from gpio_control import gpio_control

g_nvm = None
g_zmq_context = None

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

def dump_config_options(phoniebox_config,filename):
    print ("\nDumping configig option from File:"+ filename)
    for section in phoniebox_config.sections():
        print ("["+section+"]")
        options = phoniebox_config.options(section)
        for option in options:
            print(option+" = "+phoniebox_config.get(section, option)) 
    print ("\n")

if __name__ == "__main__":

    home = '/home/pi/RPi-Jukebox-RFID'

    # get absolute path of this script
    dir_path = os.path.dirname(os.path.realpath(__file__))
    defaultconfigFilePath = os.path.join(dir_path, '../settings/phoniebox.conf')

    argparser = argparse.ArgumentParser(description='The PhonieboxDaemon')
    argparser.add_argument('configuration_file', type=argparse.FileType('r'),nargs='?',default=defaultconfigFilePath)
    argparser.add_argument('--verbose', '-v', action='count', default=0)
    args = argparser.parse_args()

    phoniebox_config = configparser.ConfigParser(inline_comment_prefixes=";")
    phoniebox_config.read(args.configuration_file.name)

    print ("Starting the "+ phoniebox_config.get('SYSTEM', 'BOX_NAME') +" Daemon")
    
    if args.verbose:
        dump_config_options(phoniebox_config,args.configuration_file.name)

    # Play Startup Sound
    volume_control = PhonieboxVolume.volume_control_alsa(listcards=False)
    startsound_thread = threading.Thread(target=volume_control.play_wave_file, args=[home + "/shared/startupsound.wav"])
    startsound_thread.start()

    g_nvm = nv_manager()

    #phoniebox music player status
    music_player_status = g_nvm.load(phoniebox_config.get('PLAYER', 'MUSIC_PLAYER_STATUS'))
    
    #card id database
    cardid_database = g_nvm.load(phoniebox_config.get('RFID', 'CARDID_DATABASE'))

    #initialize Phonibox objcts
    objects = {'volume':volume_control,
               'player':PhonieboxPlayerMPD.player_control(music_player_status,volume_control),
               'system':PhonieboxSystem.system_control}

    print ("Init Phonibox RPC Server ")
    rpcs = PhonieboxRpcServer(objects)
    if rpcs != None:
        g_zmq_context = rpcs.connect()

    #rfid_reader = RFID_Reader("RDM6300",{'numberformat':'card_id_float'})
    rfid_reader = RFID_Reader("Fake",zmq_context=g_zmq_context)
    if rfid_reader is not None:
        rfid_reader.set_cardid_db(cardid_database)
        rfid_reader.reader.set_card_ids(list(cardid_database))     #just for Fake Reader to be aware of card numbers
        rfid_thread = threading.Thread(target=rfid_reader.run)
    else:
        rfid_thread = None
    
    ##initialize gpio
    gpio_config = None
    if gpio_config is not None:
        gpio_config = configparser.ConfigParser(inline_comment_prefixes=";")
        gpio_config.read(phoniebox_config.get('GPIO', 'GPIO_CONFIG'))
    
        phoniebox_function_calls = function_calls.phoniebox_function_calls()
        gpio_controler = gpio_control(phoniebox_function_calls)

        devices = gpio_controler.get_all_devices(config)
        gpio_controler.print_all_devices()
        gpio_thread = threading.Thread(target=gpio_controler.gpio_loop)
    else:
        gpio_thread = None
    
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