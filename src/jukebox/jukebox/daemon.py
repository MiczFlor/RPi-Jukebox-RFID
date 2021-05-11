#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import threading
import sys
import signal
import configparser

import jukebox.Volume
import jukebox.System
from player import PlayerMPD
from jukebox.rpc.Server import PhonieboxRpcServer
from jukebox.NvManager import nv_manager
from components.rfid_reader.PhonieboxRfidReader import RFID_Reader
# from gpio_control import gpio_control

g_nvm = None


def signal_handler(signal, frame):
    """ catches signal and triggers the graceful exit """
    print("Caught signal {}, exiting...".format(signal))
    exit_gracefully(signal, frame)


def exit_gracefully(esignal, frame):
    print("\nGot Signal {} ({}) \n {}".format(signal.Signals(esignal).name, esignal, frame))

    global g_nvm
    # TODO: stop all threads

    # save all nonvolatile data
    g_nvm.save_all()
    # TODO: play stop (maybe)
    # TODO: implement shutdown ()

    print("Exiting")
    sys.exit(0)


def dump_config_options(phoniebox_config, filename):
    print("\nDumping configig option from File:" + filename)
    for section in phoniebox_config.sections():
        print("[" + section + "]")
        options = phoniebox_config.options(section)
        for option in options:
            print(option + " = " + phoniebox_config.get(section, option))
    print("\n")


def jukebox_daemon(configuration_file, verbose=0):

    global g_nvm
    zmq_context = None

    phoniebox_config = configparser.ConfigParser(inline_comment_prefixes=";")
    phoniebox_config.read(configuration_file)

    print("Starting the " + phoniebox_config.get('SYSTEM', 'BOX_NAME') + " Daemon")

    if verbose:
        dump_config_options(phoniebox_config, configuration_file)

    # Play Startup Sound
    volume_control = jukebox.Volume.volume_control_alsa(listcards=False)

    startsound_thread = threading.Thread(target=volume_control.play_wave_file,
                                         args=[phoniebox_config.get('SYSTEM', 'STARTUP_SOUND')])
    startsound_thread.start()

    g_nvm = nv_manager()

    # load music player status
    music_player_status = g_nvm.load(phoniebox_config.get('PLAYER', 'MUSIC_PLAYER_STATUS'))

    # load card id database
    cardid_database = g_nvm.load(phoniebox_config.get('RFID', 'CARDID_DATABASE'))

    # MPD Configs
    mpd_host = phoniebox_config.get('SYSTEM', 'MPD_HOST')

    # initialize Jukebox objcts
    objects = {'volume': volume_control,
               'player': PlayerMPD.player_control(mpd_host, music_player_status, volume_control),
               'system': jukebox.System.system_control}

    print("Init Jukebox RPC Server ")
    rpcs = PhonieboxRpcServer(objects)
    if rpcs is not None:
        zmq_context = rpcs.connect()

    # rfid_reader = RFID_Reader("RDM6300",{'numberformat':'card_id_float'})
    rfid_reader = RFID_Reader("Fake", zmq_context=zmq_context)
    if rfid_reader is not None:
        rfid_reader.set_cardid_db(cardid_database)
        rfid_reader.reader.set_card_ids(list(cardid_database))     # just for Fake Reader to be aware of card numbers
        rfid_thread = threading.Thread(target=rfid_reader.run)
    else:
        rfid_thread = None

    # initialize gpio
    # TODO: GPIO not yet integreted
    gpio_config = None
    if gpio_config is not None:
        gpio_config = configparser.ConfigParser(inline_comment_prefixes=";")
        gpio_config.read(phoniebox_config.get('GPIO', 'GPIO_CONFIG'))

        # phoniebox_function_calls = function_calls.phoniebox_function_calls()
        # gpio_controler = gpio_control(phoniebox_function_calls)

        # devices = gpio_controler.get_all_devices(config)
        # gpio_controler.print_all_devices()
        # gpio_thread = threading.Thread(target=gpio_controler.gpio_loop)
    else:
        gpio_thread = None

    # setup the signal listeners
    signal.signal(signal.SIGINT, exit_gracefully)
    signal.signal(signal.SIGTERM, exit_gracefully)

    # Start threads and RPC Server
    if rpcs is not None:
        if gpio_thread is not None:
            print("Starting GPIO Thread")
            gpio_thread.start()
        if rfid_thread is not None:
            print("Starting RFID Thread")
            rfid_thread.start()
        print("Starting RPC Server")
        rpcs.server()
