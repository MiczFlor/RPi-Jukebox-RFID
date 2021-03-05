#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import threading
import sys, os.path
import signal
from time import sleep, time

#import gpio_control

import PhonieboxVolume
import PhonieboxPlayer
from PhonieboxRpcServer import phoniebox_rpc_server

# get absolute path of this script
dir_path = os.path.dirname(os.path.realpath(__file__))
defaultconfigFilePath = os.path.join(dir_path, 'phoniebox.conf')

def signal_handler(signal, frame):
    """ catches signal and triggers the graceful exit """
    print("Caught signal {}, exiting...".format(signal))
    exit_gracefully(signal, frame)

def exit_gracefully(esignal, frame):
    print ("\nGot Signal {} ({}) \n {}".format(signal.Signals(esignal).name, esignal, frame))
    
    #stop all threads
    
    #save all nv
    #play stop (maybe)
    #shutdown ()
    
    print ("Exiting")
    sys.exit(0)


def playstartsound():
    # import required libraries 
    from pydub import AudioSegment  
    from pydub.playback import play  
  
    # Import an audio file  
    wav_file = AudioSegment.from_file(file = "../../shared/startupsound.wav", format = "wav")  
    play(wav_file)


if __name__ == "__main__":

    # if called directly, launch Phoniebox.py as rfid-reader daemon
    # treat the first argument as defaultconfigFilePath if given
    if len(sys.argv) <= 1:
        configFilePath = defaultconfigFilePath
    else:
        configFilePath = sys.argv[1]

    #sys.path.append(parentdir+"/scripts")
    sys.path.insert(0,'../../gpio_control')
    print(sys.path)

    #parse config
    #gpio_config = configparser.ConfigParser(inline_comment_prefixes=";")
    #gpio_config_path = os.path.expanduser('/home/pi/RPi-Jukebox-RFID/settings/gpio_settings.ini')
    #gpio_config.read(config_path)

    # Play Startup Sound
    startsound_thread = threading.Thread(target=playstartsound)
    startsound_thread.start()


    PhonieboxVolume.list_cards()
    PhonieboxVolume.list_mixers({ 'cardindex': 0 })

    #initialize Phonibox objcts
    objects = {'volume':PhonieboxVolume.volume_control_alsa(),
               'player':PhonieboxPlayer.player_control()}

    print ("Init Phonibox ZMQ Server ")
    rpcs = phoniebox_rpc_server(objects)
    if rpcs != None:
        rpcs.connect()
        #pc_t = threading.Thread(target=pc.process_queue)
        #pc_t.start()


    ##rfid
    #card id will be linked directly with object call which are feeded into the mq
    cardid_db = {'104,49914':{'object':'','method':'','params':{}},
                 '103,12632':{'object':'','method':'','params':{}},
                 '104,29698':{'object':'','method':'','params':{}},
                 '108,07437':{'object':'','method':'','params':{}},
                 '107,60360':{'object':'','method':'','params':{}},
                 '106,64513':{'object':'','method':'','params':{}},
                 '104,14891':{'object':'','method':'','params':{}},
                 '103,24033':{'object':'','method':'','params':{}},
                 '104,32860':{'object':'','method':'','params':{}}   }

    #rfid_reader = RFID_Reader("RDM6300",{'numberformat':'card_id_float'})
    rfid_reader = None
    if rfid_reader is not None:
        rfid_reader.set_cardid_db()
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
        print ("Starting ZMQ Server")
        rpcs.server()