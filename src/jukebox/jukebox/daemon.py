#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import threading
import sys
import signal
import configparser
import logging
import importlib

import jukebox.Volume
import jukebox.System
from player import PlayerMPD
from jukebox.rpc.Server import RpcServer
from jukebox.NvManager import nv_manager
from components.rfid_reader.PhonieboxRfidReader import RFID_Reader
# from gpio_control import gpio_control

import jukebox.cfghandler

logger = logging.getLogger('jb.daemon')
cfg = jukebox.cfghandler.get_handler('jukebox')


class JukeBox:
    def __init__(self, configuration_file):
        self.nvm = nv_manager()
        self.zmq_context = None

        self.config = configparser.ConfigParser(inline_comment_prefixes=";")
        self.config.read(configuration_file)

        jukebox.cfghandler.load_yaml(cfg, '../../settings/jukebox.yaml')

        logger.info("Starting the " + cfg.getn('system', 'box_name', default='Jukebox2') + " Daemon")
        logger.info("Starting the " + cfg['system'].get('box_name', default='Jukebox2') + " Daemon")

        # if logger.isEnabledFor(logging.DEBUG):
        #     self.dump_config_options(self.config, configuration_file)

        # setup the signal listeners
        signal.signal(signal.SIGINT, self.signal_handler)
        signal.signal(signal.SIGTERM, self.signal_handler)

    def dump_config_options(self, config, filename):
        print("\nDumping configig option from File:" + filename)
        for section in config.sections():
            print("[" + section + "]")
            options = config.options(section)
            for option in options:
                print(option + " = " + config.get(section, option))
            print("\n")

    def signal_handler(self, esignal, frame):
        # catches signal and triggers the graceful exit
        logger.info("Caught signal {} ({}) \n {}".format(signal.Signals(esignal).name, esignal, frame))
        self.exit_gracefully()

    def exit_gracefully(self):
        # TODO: play stop
        # TODO: Iterate over objects and tell them to exit
        # TODO: stop all threads
        logger.info("Exiting")

        # save all nonvolatile data
        self.nvm.save_all()

        # TODO: implement shutdown ()

        logger.info("Exiting")
        sys.exit(0)

    def run(self):
        objects = {}
        if 'volume' in cfg['modules']:
            try:
                m_volume = importlib.import_module(cfg['modules']['volume'], 'pkg.subpkg')
            except Exception as e:
                logger.error(f"Failed to load volume module: {cfg['modules']['volume']}. Trying without...")
                logger.error(f"Reason: {e}")
            else:
                objects['volume'] = m_volume.init()
                if 'startup_sound' in cfg['system']:
                    startsound_thread = threading.Thread(target=m_volume.play_wave,
                                                         args=[cfg['system']['startup_sound']],
                                                         name='StartSound')
                    startsound_thread.daemon = True
                    startsound_thread.start()
                else:
                    logger.debug("No startup sound in config file")

        # Play Startup Sound
        # volume_control = jukebox.Volume.volume_control_alsa(listcards=False)
        #
        # startsound_thread = threading.Thread(target=volume_control.play_wave_file,
        #                                      args=[self.config.get('SYSTEM', 'STARTUP_SOUND')])
        # startsound_thread.start()

        # load music player status
        # music_player_status = self.nvm.load(self.config.get('PLAYER', 'MUSIC_PLAYER_STATUS'))
        #
        # # load card id database
        cardid_database = self.nvm.load(self.config.get('RFID', 'CARDID_DATABASE'))
        #
        # # MPD Configs
        # mpd_host = self.config.get('SYSTEM', 'MPD_HOST')

        # initialize Jukebox objcts
        # objects = {'player': PlayerMPD.player_control(mpd_host, music_player_status, None),
        #            'system': jukebox.System.system_control}

        logger.info("Init Jukebox RPC Server")
        rpcserver = RpcServer(objects)
        if rpcserver is not None:
            self.zmq_context = rpcserver.connect()

        # rfid_reader = RFID_Reader("RDM6300",{'numberformat':'card_id_float'})
        rfid_reader = RFID_Reader("Fake", zmq_context=self.zmq_context)
        if rfid_reader is not None:
            rfid_reader.set_cardid_db(cardid_database)
            rfid_reader.reader.set_card_ids(list(cardid_database))     # just for Fake Reader to be aware of card ids
            rfid_thread = threading.Thread(target=rfid_reader.run)
        else:
            rfid_thread = None

        # initialize gpio
        # TODO: GPIO not yet integrated
        gpio_config = None
        if gpio_config is not None:
            gpio_config = configparser.ConfigParser(inline_comment_prefixes=";")
            gpio_config.read(self.config.get('GPIO', 'GPIO_CONFIG'))

            # phoniebox_function_calls = function_calls.phoniebox_function_calls()
            # gpio_controler = gpio_control(phoniebox_function_calls)

            # devices = gpio_controler.get_all_devices(config)
            # gpio_controler.print_all_devices()
            # gpio_thread = threading.Thread(target=gpio_controler.gpio_loop)
        else:
            gpio_thread = None

        # Start threads and RPC Server
        if rpcserver is not None:
            if gpio_thread is not None:
                logger.debug("Starting GPIO Thread")
                gpio_thread.start()
            if rfid_thread is not None:
                logger.debug("Starting RFID Thread")
                rfid_thread.start()
            logger.debug("Starting RPC Server")
            rpcserver.run()
