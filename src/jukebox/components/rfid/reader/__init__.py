import logging
import threading
import time
import importlib
from typing import Callable
from enum import Enum

import jukebox.plugs as plugs
import jukebox.cfghandler
import jukebox.utils as utils
import jukebox.publishing as publishing
from components.rfid.cardutils import (decode_card_command)

from jukebox.callingback import CallbackHandler

log = logging.getLogger('jb.rfid')

_READERS = {}
cfg_rfid = jukebox.cfghandler.get_handler('rfid')
cfg_main = jukebox.cfghandler.get_handler('jukebox')
cfg_cards = jukebox.cfghandler.get_handler('cards')


class RfidCardDetectState(Enum):
    received = 0,
    isRegistered = 1
    isUnkown = 2


class RfidCardDetectCallbacks(CallbackHandler):
    """
    Callbacks are executed if rfid card is detected
    """

    def register(self, func: Callable[[str, RfidCardDetectState], None]):
        """
        Add a new callback function :attr:`func`.

        Callback signature is

        .. py:function:: func(card_id: str, state: int)
            :noindex:

        :param card_id: Card ID
        :param state: See #RfidCardDetectState
        """
        super().register(func)

    def run_callbacks(self, card_id: str, state: RfidCardDetectState):
        """:meta private:"""
        super().run_callbacks(card_id, state)


#: Callback handler instance for rfid_card_detect_callbacks events.
#: See #RfidCardDetectCallbacks
rfid_card_detect_callbacks: RfidCardDetectCallbacks = RfidCardDetectCallbacks('rfid_card_detect_callbacks', log)


class CardRemovalTimerClass(threading.Thread):
    """
    A timer watchdog thread that calls timeout_action on time-out

    """
    def __init__(self, on_timeout_callback, logger: logging.Logger = None):
        """
        :param on_timeout_callback: The function to execute on time-out
        """
        threading.Thread.__init__(self)
        self._logger = logger if logger is not None else logging.getLogger('jb.rfid.cardremove')
        self.trigger = threading.Event()
        self.timeout_action = on_timeout_callback

    def run(self):
        self._logger.debug("CardRemovalTimerClass watchdog started")
        has_timed_out = True
        while True:
            # Prevent max CPU by forced loop slow down when self.trigger.is_set() is permanently high
            time.sleep(0.2)
            # This is the actual timer:
            # self.trigger.wait() aborts immediately when trigger.is_set becomes True
            self.trigger.wait(1)
            if self.trigger.is_set():
                has_timed_out = False
            else:
                if not has_timed_out:
                    self.timeout_action()
                # Save that we have timed out before, so time-out event handler is run only on the first time out
                has_timed_out = True


class ReaderRunner(threading.Thread):
    def __init__(self, reader_cfg_key: str,
                 logger: logging.Logger = None):
        super().__init__(name=f"{reader_cfg_key}Thread", daemon=True)
        self._logger = logger
        if logger is None:
            self._logger = logging.getLogger(f'jb.rfid({reader_cfg_key})')
        self._reader_cfg_key = reader_cfg_key
        reader_type = cfg_rfid['rfid']['readers'][reader_cfg_key]['module'].lower()
        # Load the corresponding module
        self._logger.info(f"For reader config key '{reader_cfg_key}': loading module '{reader_type}'")
        self._reader_module = importlib.import_module('components.rfid.hardware.' + reader_type + '.' + reader_type,
                                                      'pkg.subpkg')
        self._reader = None
        # Get additional configuration
        self._cfg_same_id_delay = cfg_rfid.setndefault('rfid', 'readers', reader_cfg_key,
                                                       'same_id_delay', value=1.0)
        self._cfg_place_not_swipe = cfg_rfid.setndefault('rfid', 'readers', reader_cfg_key,
                                                         'place_not_swipe', 'enabled', value=False)
        self._cfg_log_ignored_cards = cfg_rfid.setndefault('rfid', 'readers', reader_cfg_key,
                                                           'log_ignored_cards', value=False)
        # Get removal actions:
        cfg_removal_action = cfg_rfid.getn('rfid', 'readers', reader_cfg_key,
                                           'place_not_swipe', 'card_removal_action', default=None)
        self._default_removal_action = utils.decode_rpc_command(cfg_removal_action, self._logger)
        self._logger.debug(f"Decoded removal action: {utils.rpc_call_to_str(self._default_removal_action)}")

        if self._cfg_place_not_swipe is True and self._default_removal_action is None:
            self._logger.warning('Option place_not_swipe activated, but no card removal action specified. '
                                 'Ignoring place_place_not_swipe')
            self._cfg_place_not_swipe = False
        self._timer_thread = None
        if self._cfg_place_not_swipe:
            self._timer_thread = CardRemovalTimerClass(utils.bind_rpc_command(self._default_removal_action, dereference=False,
                                                                              logger=self._logger))
            self._timer_thread.daemon = True
            self._timer_thread.name = f"{reader_cfg_key}CRemover"
            self._timer_thread.start()
        self.publisher = None
        self.topic = f"{plugs.loaded_as(__name__)}.card_id"
        # Ready to go
        self._cancel = threading.Event()

    def stop(self):
        self._cancel.set()
        self._reader.stop()

    def run(self):  # noqa: C901
        self._logger.debug("Start listening!")
        # Init the reader class
        # Do it here, such that the reader class is initialized and destroyed in the
        # actual reader thread
        self._reader = self._reader_module.ReaderClass(self._reader_cfg_key)
        self.publisher = publishing.get_publisher()
        # Previous ID is only stored to prevent repetitive triggers of the same card in case of place-not-swipe scenarios
        # For command card there is an exception (see below)
        previous_id = ''
        previous_time = time.time()
        # This parameter is only relevant for the place-not-swipe case:
        # We need to store if the last action was a valid action, which triggers the timer for the remove action
        # So we can decide when a card id comes in, if the timer has to be reset or not without decoding the cards action
        valid_for_removal_action = False

        if self._timer_thread is not None:
            self._logger.debug(f"card_removal_timer_thread.native_id = {self._timer_thread.ident}")
            self._timer_thread.trigger.clear()

        with self._reader as reader:
            # Raises a StopIteration (if blocking) or simply returns '' (if non-blocking)
            for card_id in reader:
                if self._cancel.is_set():
                    break
                if card_id:
                    # (1) Re-Trigger the timer, to detect card removal
                    # But: don't trigger the timer just yet if it is a new card id
                    # First, need to figure out if this card really has is a removal-action card
                    # Cards w/o removal action are e.g. command card, ignore_removal, unknown cards
                    # These non-removal actions card can also be placed on the reader. Meaning that only
                    # on first read-out card_id != previous_id. For further iterations, the
                    # validity state needs to be saved in valid_for_removal_action
                    if valid_for_removal_action and self._timer_thread is not None and card_id == previous_id:
                        self._timer_thread.trigger.set()
                    if card_id != previous_id or (time.time() - previous_time) >= self._cfg_same_id_delay:
                        # (2) Log this: do this first to provide log entry in case something does not run through
                        self._logger.info(f"Received card id = '{card_id}'")

                        previous_id = card_id
                        valid_for_removal_action = False

                        # (3) Check if this card is in the card database
                        # TODO: This card config read is not thread safe

                        # run callbacks on successfull read before card_entry is processed
                        rfid_card_detect_callbacks.run_callbacks(card_id, RfidCardDetectState.received)

                        card_entry = cfg_cards.get(card_id, default=None)
                        if card_entry is not None:

                            # (4) Decode card action
                            card_action = decode_card_command(card_entry, self._logger)

                            # (5) Send status update to PubSub
                            self.publisher.send(self.topic, card_id)

                            if card_action is not None:
                                # (6) Override card individual parameters
                                if card_action.get('ignore_same_id_delay', False):
                                    # If this is a 'ignore_same_id_delay' card, clear the previous ID:
                                    # This very neatly allows (without overhead) that the card can trigger the command again
                                    # without waiting for same_id_delay
                                    previous_id = ''
                                elif self._timer_thread is not None:
                                    # Only activate removal action if ignore_same_id_delay is False
                                    # Reason: There is no use case for a card with fast-repeat action (e.g. volume incr)
                                    # and common card removal action. Disallow that to card config a little easier
                                    valid_for_removal_action = not card_entry.get('ignore_card_removal_action', False)
                                    if valid_for_removal_action:
                                        self._timer_thread.trigger.set()

                                # (7) Finally trigger action
                                #     Option A) plugs.call_ignore_errors(): it is thread safe but blocks, there is no Queue!
                                #     Option B) Through the RPC client. A little overhead but uses the same
                                #               communication channel as external IFs
                                # Retrieve card_action parameters always with default to be error-safe in case of
                                # dodgy cards database entry
                                # TODO: This call happens from the reader thread, which is not necessarily what we want ...
                                # TODO: Change to RPC call to transfer execution into main thread
                                rfid_card_detect_callbacks.run_callbacks(card_id, RfidCardDetectState.isRegistered)
                                plugs.call_ignore_errors(card_action['package'], card_action['plugin'], card_action['method'],
                                                         args=card_action['args'], kwargs=card_action['kwargs'])

                        else:
                            rfid_card_detect_callbacks.run_callbacks(card_id, RfidCardDetectState.isUnkown)
                            self._logger.info(f"Unknown card: '{card_id}'")
                            self.publisher.send(self.topic, card_id)
                    elif self._cfg_log_ignored_cards is True:
                        self._logger.debug(f"'Ignoring card id {card_id} due to same-card-delay ({self._cfg_same_id_delay}s)")
                    previous_time = time.time()
                else:
                    # Time-out for reader internal error resulting in empty string: to be ignored
                    pass
                # Slow down the card reading while loop in case card is placed permanently on reader
                self._cancel.wait(timeout=0.2)
                if self._timer_thread is not None:
                    self._timer_thread.trigger.clear()

        self._logger.debug("Stop listening!")


@plugs.finalize
def finalize():
    try:
        reader_config_file = cfg_main.getn('rfid', 'reader_config')
        jukebox.cfghandler.load_yaml(cfg_rfid, reader_config_file)
    except FileNotFoundError:
        cfg_rfid.config_dict({'rfid': {'readers': {}}})
        log.warning(f"rfid reader database file not found. Creating empty database: '{reader_config_file}'")
        # Save the empty rfid reader database, to make sure we can create the file and have access to it
        cfg_rfid.save(only_if_changed=False)

    if 'rfid' in cfg_rfid and 'readers' in cfg_rfid['rfid']:
        # Load all the required modules
        # Start a ReaderRunner-Thread for each Reader
        for reader_cfg_key in cfg_rfid['rfid']['readers'].keys():
            _READERS[reader_cfg_key] = ReaderRunner(reader_cfg_key)
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
    return _READERS.values()
