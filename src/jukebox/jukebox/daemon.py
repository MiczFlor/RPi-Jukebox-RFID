#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import threading
import sys
import signal
import logging
import time


import jukebox.plugs as plugin
from jukebox.rpc.server import RpcServer
from jukebox.NvManager import nv_manager
from components.rfid_reader.PhonieboxRfidReader import RFID_Reader
# from gpio_control import gpio_control

import jukebox.cfghandler

logger = logging.getLogger('jb.daemon')
cfg = jukebox.cfghandler.get_handler('jukebox')


class JukeBox:
    def __init__(self, configuration_file):
        self.nvm = nv_manager()
        self.configuration_file = configuration_file
        self._signal_cnt = 0
        self.rpcserver = None

        jukebox.cfghandler.load_yaml(cfg, self.configuration_file)

        logger.info("Starting the " + cfg.getn('system', 'box_name', default='Jukebox2') + " Daemon")
        logger.info("Starting the " + cfg['system'].get('box_name', default='Jukebox2') + " Daemon")

        # setup the signal listeners
        signal.signal(signal.SIGINT, self.signal_handler)
        signal.signal(signal.SIGTERM, self.signal_handler)

    def signal_handler(self, esignal, frame):
        """Signal handler for orderly shutdown

        On first Ctrl-C (or SIGTERM) orderly shutdown procedure is embarked upon. It get allocated a time-out!
        On third Ctrl-C (or SIGTERM), this is interrupted and there will be a hard exit!
        """
        # systemd: By default, a SIGTERM is sent, followed by 90 seconds of waiting followed by a SIGKILL.
        # Pressing Ctrl-C gives SIGINT
        self._signal_cnt += 1
        timeout: float = 10.0
        time_start = time.time_ns()
        msg = f"Received signal '{signal.Signals(esignal).name}'. Count = {self._signal_cnt}"
        print(msg)
        logger.debug(msg)
        if self._signal_cnt == 1:
            # Put the shutdown procedure into a thread, so we can make a time-out on it
            # Cannot use threading.Timer for the timeout, as sys.exit() must be called from main thread
            t = threading.Thread(target=self.exit_gracefully, args=[esignal], daemon=True, name="ShutdownThread")
            t.start()
            t.join(timeout)
            if t.is_alive():
                msg = f"Shutdown handler timed out after {timeout} s "
                print(f"Shutdown incomplete. {msg}. Terminating now forcefully!")
                print(f"Active Threads = {threading.enumerate()}")
                logger.error(msg)
                # Let's see which threads did not exit properly in time
                logger.error(f"Active Threads = {threading.enumerate()}")
                sys.exit(1)
            logger.debug(f"Active Threads = {threading.enumerate()}")
            logger.info(f"Shutdown time: {((time.time_ns() - time_start) / 1000000.0):.3f} ms")
            sys.exit(0)
        elif self._signal_cnt == 2:
            print("Waiting for closing down procedure to complete. Pressing Ctrl-C again will close Jukebox down immediately.")
        if self._signal_cnt == 3:
            sys.exit(1)

    def exit_gracefully(self, esignal):
        msg = f"Closing down JukeBox {cfg.getn('system', 'box_name', default='Unnamed')}"
        print(msg)
        logger.info(msg)
        # (1) Stop taking commands from RPC
        if self.rpcserver is not None:
            self.rpcserver.terminate()
        # (2) Stop the music
        plugin.call_ignore_errors('player', 'ctrl', 'stop')
        # (3) Call exit functions of all plugins
        plugin.close_down(esignal)
        # (4) Save all nonvolatile data
        self.nvm.save_all()
        jukebox.cfghandler.write_yaml(cfg, self.configuration_file, only_if_changed=True)
        # (5) Say goodbye
        msg = "All done. Hear you soon!"
        print(msg)
        logger.info(msg)

    def run(self):
        time_start = time.time_ns()
        # Load the plugins
        plugins_named = cfg.getn('modules', 'named', default={})
        plugins_other = cfg.getn('modules', 'others', default=[])
        plugin.load_all_named(plugins_named, prefix='components')
        plugin.load_all_unnamed(plugins_other, prefix='components')
        plugin.load_all_finalize()

        # Initial testing code:
        # print(f"Callables = {plugin._PLUGINS}")
        # print(f"{plugin.modules['volume'].factory.list()}")
        # print(f"Volume factory = {plugin.get('volume', 'factory').list()}")

        # Testcode for switching to another volume control service ...
        # plugin.modules['volume'].factory.set_active("alsa2")
        # print(f"Callables = {plugin.callables}")

        # load card id database
        cardid_database = self.nvm.load(cfg.getn('rfid', 'cardid_database'))

        logger.info("Init Jukebox RPC Server")
        self.rpcserver = RpcServer()

        rfid_reader = None
        # rfid_reader = RFID_Reader("RDM6300",{'numberformat':'card_id_float'})
        # rfid_reader = RFID_Reader("Fake", zmq_address='inproc://JukeBoxRpcServer', zmq_context=zmq.Context.instance())
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
            pass
            # gpio_config = configparser.ConfigParser(inline_comment_prefixes=";")
            # gpio_config.read(self.config.get('GPIO', 'GPIO_CONFIG'))

            # phoniebox_function_calls = function_calls.phoniebox_function_calls()
            # gpio_controler = gpio_control(phoniebox_function_calls)

            # devices = gpio_controler.get_all_devices(config)
            # gpio_controler.print_all_devices()
            # gpio_thread = threading.Thread(target=gpio_controler.gpio_loop)
        else:
            gpio_thread = None

        logger.info(f"Start-up time: {((time.time_ns() - time_start) / 1000000.0):.3f} ms")

        if 'reference_out' in cfg['modules']:
            with open(cfg.getn('modules', 'reference_out'), 'w') as stream:
                plugin.dump_plugins(stream)

        # Start the RPC Server
        self.rpcserver.run()
