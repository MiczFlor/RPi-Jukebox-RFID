#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import threading
import sys, os.path
import signal
from Phoniebox import Phoniebox
from time import sleep, time

#import gpio_control

import PhonieboxVolume
import PhonieboxPlayer
from PhonieboxRpcServer import phoniebox_rpc_server

# get absolute path of this script
dir_path = os.path.dirname(os.path.realpath(__file__))
defaultconfigFilePath = os.path.join(dir_path, 'phoniebox.conf')

# watchdog blocks the script, so it cannot be used in the same file as the PhonieboxDaemon
# from watchdog.observers import Observer
# from watchdog.events import FileSystemEventHandler
# from os.path import dirname

# class FileModifiedHandler(FileSystemEventHandler):

#    """ watch the given file for changes and execute callback function on modification """
#    def __init__(self, file_path, callback):
#        self.file_path = file_path
#        self.callback = callback

#        # set observer to watch for changes in the directory
#        self.observer = Observer()
#        self.observer.schedule(self, dirname(file_path), recursive=False)
#        self.observer.start()
#        try:
#            while True:
#                sleep(1)
#        except KeyboardInterrupt:
#            self.observer.stop()
#        self.observer.join()
#
#    def on_modified(self, event):
#        # only act on the change that we're looking for
#        if not event.is_directory and event.src_path.endswith(self.file_path):
#            daemon.log("cardAssignmentsFile modified!",3)
#            self.callback() # call callback


class PhonieboxDaemon(Phoniebox):
    """ This subclass of Phoniebox is to be called directly, running as RFID reader daemon """

    def __init__(self, configFilePath=defaultconfigFilePath):
        Phoniebox.__init__(self, configFilePath)
        self.lastplayedID = 0

    def run(self):
        # do things if killed
        signal.signal(signal.SIGINT, self.signal_handler)
        signal.signal(signal.SIGTERM, self.signal_handler)

        # establish mpd connection
        self.mpd_init_connection()
        self.mpd_init_settings()
        state = self.client.status()["state"]

        daemon.play_alsa(daemon.get_setting("phoniebox", 'startup_sound'))
        if state == "play":
            self.client.play()

        # launch watcher for config files, blocks the script
        # TODO: it would be better to watch the changes with a second process that
        # tells the PhonieboxDaemon to reload the config whenever needed.

        # card_assignments_file = daemon.get_setting("phoniebox","card_assignments_file")
        # cardAssignmentsWatchdog = FileModifiedH check for process existandler(card_assignments_file, self.update_cardAssignments)
        # ConfigWatchdog = FileModifiedHandler(configFilePath, self.read_config)

#        # start_reader runs an endless loop, nothing will be executed afterwards
        daemon.start_reader()


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
    
    
    #""" stop mpd and write cardAssignments to disk if daemon is stopped """
    #self.mpd_connect_timeout()
    #self.client.stop()
    #self.client.disconnect()
    # write config to update playstate
    #self.write_new_cardAssignments()
     # exit script

    print ("Exiting")
    
    sys.exit(0)
    #trigger halt of system?


def startsound():
    print ("Play Start Sound")
    ##play start sound
    ##use dub to play sound? -> benchmark could be used to play 440 hz or other music things

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
    startsound_thread = threading.Thread(target=startsound)
    startsound_thread.start()


    PhonieboxVolume.list_cards()
    PhonieboxVolume.list_mixers({ 'cardindex': 0 })

    ##run zeromq_server as thread
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