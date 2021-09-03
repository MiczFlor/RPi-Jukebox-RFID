import logging
import threading
import time
import importlib
import jukebox.plugs as plugs
import jukebox.cfghandler

log = logging.getLogger('jb.rfid')

_READERS = {}
cfg_rfid = jukebox.cfghandler.get_handler('rfid')
cfg_main = jukebox.cfghandler.get_handler('jukebox')
cfg_cards = jukebox.cfghandler.get_handler('cards')


class ReaderRunner(threading.Thread):
    def __init__(self, reader_cfg_key: str,
                 action_thread=None,
                 logger: logging.Logger = None):
        super().__init__(name=f"{reader_cfg_key}Thread", daemon=True)
        self._logger = logger
        if logger is None:
            self._logger = logging.getLogger(f'jb.rfid({reader_cfg_key})')
        self._action_thread = action_thread
        # TODO
        self._timer_thread = None  # timer_thread
        self._reader_cfg_key = reader_cfg_key
        reader_type = cfg_rfid['rfid']['readers'][reader_cfg_key]['module'].lower()
        # Load the corresponding module
        self._logger.info(f"For reader config key '{reader_cfg_key}': loading module '{reader_type}'")
        self._reader_module = importlib.import_module('components.rfid.' + reader_type + '.' + reader_type, 'pkg.subpkg')
        self._reader = None
        # Get additional configuration
        self._cfg_same_id_delay = cfg_rfid.setndefault('rfid', 'same_id_delay', value=1.0)
        self._cfg_place_not_swipe = cfg_rfid.setndefault('rfid', 'place_not_swipe', value=False)
        self._cfg_log_ignored_cards = cfg_rfid.setndefault('rfid', 'log_ignored_cards', value=False)
        # Ready to go
        self._cancel = threading.Event()

    def stop(self):
        self._cancel.set()
        self._reader.stop()

    def run(self):
        self._logger.debug("Start listening!")
        # Init the reader class
        # Do it here, such that the reader class is initialized and destroyed in the
        # actual reader thread
        self._reader = self._reader_module.ReaderClass(self._reader_cfg_key)
        # Previous ID is only stored to prevent repetitive triggers of the same card in case of place-not-swipe scenarios
        # For command card there is an exception (see below)
        previous_id = ''
        previous_time = time.time()

        if self._timer_thread is not None:
            self._logger.debug(f"card_removal_timer_thread.native_id = {self._timer_thread.ident}")
            self._timer_thread.trigger.clear()

        if self._action_thread is not None:
            self._logger.debug(f"pin_action_thread.native_id = {self._action_thread.ident}")
            self._action_thread.trigger.clear()

        with self._reader as reader:
            # Raises a StopIteration (if blocking) or simply returns '' (if non-blocking)
            for card_id in reader:
                if self._cancel.is_set():
                    break
                if card_id:
                    if card_id != previous_id or (time.time() - previous_time) >= self._cfg_same_id_delay:
                        # Do this first to provide fast audible/visual feed-back
                        if self._action_thread:
                            self._action_thread.trigger.set()
                        previous_id = card_id
                        self._logger.info(f"Received card id = '{card_id}'")
                        # (1) Look-up card
                        card_action = cfg_cards.get(card_id, default=None)
                        # (2) Send status update to PubSub
                        # TODO
                        # (3) Trigger action
                        #     Option A) plugs.call_ignore_errors() --> it is thread safe! But it blocks - there is no Queue!
                        #     Option B) Through the RPC client. A little overhead but uses the same communication channel
                        #               as external IFs
                        if card_action is not None:
                            # Retrieve card_action parameters always with default to be error-safe in case of
                            # dodgy cards database entry
                            # TODO: This call happens from the reader thread, which is not necessarily what we want ...
                            # TODO: Change to RPC call to transfer execution into main thread
                            plugs.call_ignore_errors(card_action.get('package', 'package_not_specified'),
                                                     card_action.get('plugin', 'plugin_not_specified'),
                                                     card_action.get('method', None),
                                                     args=card_action.get('args', ()),
                                                     kwargs=card_action.get('kwargs', {}))
                            if card_action.get('command_card', False):
                                # If this is a command card, clear the previous ID:
                                # This very neatly allows (without overhead) that the card can trigger the command again
                                # without waiting for same_id_delay
                                previous_id = ''
                        else:
                            self._logger.info(f"Unknown card: '{card_id}'.")
                    elif self._cfg_log_ignored_cards:
                        self._logger.debug(f"'Ignoring card id {card_id} due to same-card-delay ({self._cfg_same_id_delay}s)")
                    previous_time = time.time()
                else:
                    # Time-out for reader internal error resulting in empty string: to be ignored
                    pass
                # Slow down the card reading while loop in case card is placed permanently on reader
                self._cancel.wait(timeout=0.2)

        self._logger.debug("Stop listening!")


@plugs.finalize
def finalize():
    jukebox.cfghandler.load_yaml(cfg_rfid, cfg_main.getn('rfid', 'reader_config'))
    try:
        jukebox.cfghandler.load_yaml(cfg_cards, cfg_main.getn('rfid', 'card_database'))
    except FileNotFoundError:
        cfg_cards.config_dict({})
        log.error(f"Empty card database: Could not open file: {cfg_main.getn('rfid', 'card_database')}")

    # TODO: externalize card_database checker
    # Check type of keys (all of them)
    illegal_cards = [x for x in cfg_cards.keys() if not isinstance(x, str)]
    if len(illegal_cards) > 0:
        log.error(f"Found non-string card ID entries! Ignoring the following cards IDs: {illegal_cards}")

    # Timer Thread: TODO

    # Pin Action Thread
    buzzer_thread = None
    if plugs.exists('rfidpinaction'):
        buzzer_module = plugs.get('rfidpinaction')
        buzzer_thread = buzzer_module.get_handler()

    # Load all the required modules
    # Start a ReaderRunner-Thread for each Reader
    for reader_cfg_key in cfg_rfid['rfid']['readers'].keys():
        _READERS[reader_cfg_key] = ReaderRunner(reader_cfg_key, buzzer_thread)
    for reader_cfg_key in cfg_rfid['rfid']['readers'].keys():
        _READERS[reader_cfg_key].start()


@plugs.atexit
def atexit(**ignored_kwargs):
    # For all parallel readers, call the stop function
    for reader in _READERS.values():
        reader.stop()
    # Do I need to write the config?
    # Probably yes, in case Readers add default values?
    # Changed values of buzzer etc through a later user if?
    jukebox.cfghandler.write_yaml(cfg_rfid, cfg_main.getn('rfid', 'reader_config'), only_if_changed=True)
    # jukebox.cfghandler.write_yaml(cfg_cards, cfg_main.getn('rfid', 'card_database'), only_if_changed=False)
    return _READERS.values()
