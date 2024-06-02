# -*- coding: utf-8 -*-
import threading
import os
import sys
import signal
import logging
import time
import atexit
from typing import (Optional)

from misc import flatten
import jukebox.plugs as plugin
import jukebox.utils
import jukebox.publishing as publishing
from jukebox.rpc.server import RpcServer
from jukebox.NvManager import nv_manager

import jukebox
import jukebox.cfghandler

logger = logging.getLogger('jb.daemon')
cfg = jukebox.cfghandler.get_handler('jukebox')


@atexit.register
def log_active_threads():
    """This functions is registered with atexit very early, meaning it will be run very late. It is the best guess to
    evaluate which Threads are still running (and probably shouldn't be)

    This function is registered before all the plugins and their dependencies are loaded"""
    logger.debug(f"Active Threads = {threading.enumerate()}")


class JukeBox:
    def __init__(self, configuration_file: str, write_artifacts: bool):
        # Set up the signal listeners
        signal.signal(signal.SIGINT, self.signal_handler)
        signal.signal(signal.SIGTERM, self.signal_handler)

        self._start_time = time.time()
        logger.info(f"Starting Jukebox Daemon (Version {jukebox.version()})")

        self._git_state = jukebox.utils.get_git_state()
        logger.info(f"Git state: {self._git_state}")

        self.nvm = nv_manager()
        self._signal_cnt = 0
        self.rpc_server = None
        jukebox.cfghandler.load_yaml(cfg, configuration_file)

        self.write_artifacts = write_artifacts

        logger.info("Welcome to " + cfg.getn('system', 'box_name', default='Jukebox Version 3'))
        logger.info(f"Time of start: {time.ctime(self._start_time)}")

    @property
    def start_time(self):
        return self._start_time

    @property
    def git_state(self):
        return self._git_state

    def signal_handler(self, esignal, frame):
        """Signal handler for orderly shutdown

        On first Ctrl-C (or SIGTERM) orderly shutdown procedure is embarked upon. It gets allocated a time-out!
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
            t = threading.Thread(target=self.exit_gracefully, args=[esignal, timeout], daemon=True, name="ShutdownThread")
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
            logger.info(f"Shutdown time: {((time.time_ns() - time_start) / 1000000.0):.3f} ms")
            sys.exit(0)
        elif self._signal_cnt == 2:
            print("Waiting for closing down procedure to complete. Pressing Ctrl-C again will close Jukebox down immediately.")
        if self._signal_cnt == 3:
            sys.exit(1)

    def exit_gracefully(self, esignal, timeout):
        msg = f"Closing down JukeBox {cfg.getn('system', 'box_name', default='Unnamed')}"
        print(msg)
        logger.info(msg)
        # (1) Stop taking commands from RPC
        if self.rpc_server is not None:
            self.rpc_server.terminate()
        # (2) Stop the music
        plugin.call_ignore_errors('player', 'ctrl', 'stop')
        # (3) Call exit functions of all plugins -> return list of threads we should to wait for before shutting down
        # Note about the data format:
        # Potentially nested list since each function may return a list of threads -> flatten
        # Some functions may return None: filter those
        # thread_list = [t for t in flatten(plugin.close_down(signal_id=esignal)) if t is not None]
        thread_list = list(filter(lambda x: x is not None, flatten(plugin.close_down(signal_id=esignal))))
        # (4) Save all nonvolatile data
        self.nvm.save_all()
        cfg.save(only_if_changed=True)
        # (5) Wait for open threads to close
        # Note: Not waiting for ALL open threads, but only for those threads that are returned by the
        # @plugin.atexit-registered functions of the plugin modules
        logger.debug(f"Waiting {timeout}s for @plugin.atexit-threads to complete: {thread_list}")
        for t in thread_list:
            t.join()

        logger.debug("All @plugin.atexit threads closed")
        # (6) Say goodbye
        msg = "All done. Hear you soon!"
        print(msg)
        logger.info(msg)

    def run(self):
        time_start = time.time_ns()

        # Load the plugins
        # Ignore all errors during plugin loading to provide functionality
        # even if a plugin throws errors or has bad error handling
        plugins_named = cfg.getn('modules', 'named', default={})
        plugins_other = cfg.getn('modules', 'others', default=[])
        plugin.load_all_named(plugins_named, prefix='components', ignore_errors=True)
        plugin.load_all_unnamed(plugins_other, prefix='components', ignore_errors=True)
        plugin.load_all_finalize(ignore_errors=True)

        pack_ok = plugin.call_ignore_errors('misc', 'get_all_loaded_packages')
        pack_error = plugin.call_ignore_errors('misc', 'get_all_failed_packages')
        logger.info(f"Loaded plugins: {', '.join(pack_ok)}")
        if len(pack_error) > 0:
            logger.error(f"Plugins with errors during load: {', '.join(pack_error)}")
        publishing.get_publisher().send('core.plugins.loaded', pack_ok)
        publishing.get_publisher().send('core.plugins.error', pack_error)
        publishing.get_publisher().send('core.started_at', time.ctime(self._start_time))
        publishing.get_publisher().send('core.git_state', self._git_state)

        # ps = plugin.summarize()
        # for k, v in ps.items():
        #     print(f"{k}: {v}")

        # Initial testing code:
        # print(f"Callables = {plugin._PLUGINS}")
        # print(f"{plugin.modules['volume'].factory.list()}")
        # print(f"Volume factory = {plugin.get('volume', 'factory').list()}")

        # Testcode for switching to another volume control service ...
        # plugin.modules['volume'].factory.set_active("alsa2")
        # print(f"Callables = {plugin.callables}")

        # cfg_cards = jukebox.cfghandler.get_handler('cards')
        #
        # from components.rfid.cardutils import (card_to_str)
        # logger.debug(f"Selected card command: {' / '.join(card_to_str('V', long=True))}")
        # logger.debug(f"Selected card command: {' / '.join(card_to_str('new', long=True))}")
        #
        # print(f"\n\n{cfg_cards._data}")
        # cl = plugin.call_ignore_errors('cards', 'list_cards')
        # print(f"\n\n{cfg_cards._data}")
        #
        # logger.debug(f"Selected card command: {' / '.join(card_to_str('V', long=True))}")
        # logger.debug(f"Selected card command: {' / '.join(card_to_str('new', long=True))}")

        # for k, v in cl.items():
        #     print(f"{k}: {v}")
        # time.sleep(1)
        # plugin.call_ignore_errors('cards', 'register_card', args=['new', 'inc_volume'], kwargs={'args': [15],
        #                                                                                         'ignore_same_id_delay': True,
        #                                                                                         'overwrite': True})
        #
        # time.sleep(1)
        # plugin.call_ignore_errors('cards', 'delete_card', args=['1', False])
        # cl = plugin.call_ignore_errors('cards', 'list_cards', )
        # for k, v in cl.items():
        #     print(f"{k}: {v}")

        # Testcode for timers
        # plugin.call_ignore_errors('timers', 'timer_shutdown', 'start', args=[10])
        # time.sleep(2)
        # plugin.call_ignore_errors('timers', 'timer_shutdown', 'trigger')
        # plugin.call_ignore_errors('timers', 'timer_shutdown', 'cancel')
        # plugin.call_ignore_errors('timers', 'timer_fade_volume', 'start', args=[4, 2])

        # plugin.call_ignore_errors('host', 'timer_temperature', 'trigger')
        # time.sleep(1)
        # plugin.call_ignore_errors('host', 'timer_temperature', 'trigger')
        # time.sleep(1)
        # plugin.call_ignore_errors('host', 'timer_temperature', 'trigger')
        # time.sleep(1)
        # plugin.call_ignore_errors('host', 'timer_temperature', 'cancel')

        # plugin.call_ignore_errors('publishing', 'republish')

        # plugin.call_ignore_errors('host', 'reboot')

        # # initialize gpio
        # # TODO: GPIO not yet integrated
        # gpio_config = None
        # if gpio_config is not None:
        #     pass
        #     # gpio_config = configparser.ConfigParser(inline_comment_prefixes=";")
        #     # gpio_config.read(self.config.get('GPIO', 'GPIO_CONFIG'))
        #
        #     # phoniebox_function_calls = function_calls.phoniebox_function_calls()
        #     # gpio_controler = gpio_control(phoniebox_function_calls)
        #
        #     # devices = gpio_controler.get_all_devices(config)
        #     # gpio_controler.print_all_devices()
        #     # gpio_thread = threading.Thread(target=gpio_controler.gpio_loop)
        # else:
        #     gpio_thread = None

        self.rpc_server = RpcServer()

        logger.info(f"Start-up time: {((time.time_ns() - time_start) / 1000000.0):.3f} ms")

        if self.write_artifacts:
            # This writes out
            # rpc_command_reference.txt
            # rpc_command_alias_reference.txt

            artifacts_dir = '../../shared/artifacts/'

            try:
                os.mkdir(artifacts_dir)
            except FileExistsError:
                pass

            with open(os.path.join(artifacts_dir, 'rpc_command_reference.txt'), 'w') as stream:
                plugin.dump_plugins(stream)

            # Write reference of command shortcuts
            with open(os.path.join(artifacts_dir, 'rpc_command_alias_reference.txt'), 'w') as stream:
                jukebox.utils.generate_cmd_alias_reference(stream)

        # Start the RPC Server
        self.rpc_server.run()


class JukeBoxBuilder:
    def __init__(self):
        self._instance = None

    def __call__(self, *args, **kwargs):
        if not self._instance:
            self._instance = JukeBox(*args, **kwargs)
        return self._instance


_JUKEBOX_BUILDER: Optional[JukeBoxBuilder] = None


def get_jukebox_daemon(*args, **kwargs):
    global _JUKEBOX_BUILDER
    if _JUKEBOX_BUILDER is None:
        _JUKEBOX_BUILDER = JukeBoxBuilder()
    return _JUKEBOX_BUILDER(*args, **kwargs)
