#!/usr/bin/env python3

import logging
import os
import subprocess
import time
import re
import sys
import configparser
import argparse
import threading


logger = logging.getLogger(os.path.basename(__file__).ljust(25))
logger.setLevel(logging.DEBUG)
logconsole = logging.StreamHandler()
logconsole.setLevel(logging.INFO)
logconsole.setFormatter(logging.Formatter('%(asctime)s - %(name)s - %(levelname)-8s: %(message)s', datefmt='%d.%m.%Y %H:%M:%S'))
logger.addHandler(logconsole)

# Get absolute path of this script
script_path = os.path.abspath(os.path.dirname(os.path.realpath(__file__)))
logger.info(f"Script path: '{script_path}'")

# Add the path for the reader modules to Python's search path
# such the reader directory is searched after local dir, but before all others
reader_path = script_path + '/../components/rfid-reader'
sys.path.insert(1, reader_path)
import readersupport


def get_global_params() -> dict:
    """
    Read all the configuration from the global configuration files

    i.e. everything that is not in the rfid_reader.ini
    This is separated from the rfid_reader configuration read-in as preparation for configuration file unification
    """
    # Minimum delay between cards with same ID to be accepted as valid input
    try:
        with open(script_path + '/../settings/Second_Swipe_Pause', 'r') as f:
            try:
                same_id_delay = float(f.read().strip())
            except ValueError:
                same_id_delay = 1.0
    except FileNotFoundError:
        same_id_delay = 1.0
    logger.info(f"Global config: same_id_delay = {same_id_delay}s")

    # Swipe or place RFID cards
    with open(script_path + '/../settings/Swipe_or_Place', 'r') as f:
        place_not_swipe = True if f.read().strip().lower() == "placenotswipe" else False
    logger.info(f"Global config: place_not_swipe = {place_not_swipe}")

    # Weather control cards are except from same card delay
    with open(script_path + '/../settings/Second_Swipe_Pause_Controls', 'r') as f:
        cmd_cards_no_delay = True if f.read().strip().lower() == "on" else False
    logger.info(f"Global config: cmd_cards_no_delay = {cmd_cards_no_delay}")

    # Gather all control card IDs if necessary
    # Expects all 'CMD = 1224' entries in separate lines
    cmd_cards = None
    if cmd_cards_no_delay:
        cmd_cards = []
        # Get the card ID: Match everything between '="' and '"' ( ="cardId" ) ignoring whitespaces
        # i.e. put no restrictions on the number format.
        # New readers could introduce hexadecimal or float numbers (as in now an option in RDM6300)
        re_expr = re.compile(r'(?:\s*=\s*"\s*)(.+)(?:\s*")', re.IGNORECASE)
        print(f"{re_expr.groups}")
        with open(script_path + '/../settings/global.conf', 'r') as f:
            for line in f.readlines():
                if line.strip().lower().startswith("cmd"):
                    re_result = re_expr.search(line)
                    if re_result:
                        cmd_cards.append(re_result.group(1))
        # Check if there are no command cards configured even if cmd_cards_no_delay is enabled
        if not len(cmd_cards):
            cmd_cards = None
    logger.info(f"Global config: cmd_cards = '{cmd_cards}'")

    return {'same_id_delay': same_id_delay,
            'place_not_swipe': place_not_swipe,
            'cmd_cards': cmd_cards}


class CardRemovalTimerClass(threading.Thread):
    """
    A timer watchdog thread that calls timeout_action on time-out

    This is a single thread for all rfid reader threads (if there is more than one), such that on parallel readers
     one can be used for playback with the place-not-swipe option, and the other can be used for command cards
     without interrupting playback. I.e. as long as one reader has a card placed on it, no card removal is detected
    """
    def __init__(self, timeout_action):
        """
        :param timeout_action: The function to execute on time-out
        """
        threading.Thread.__init__(self)
        self.event = threading.Event()
        self.timeout_action = timeout_action

    def run(self):
        logger.debug("CardRemovalTimerClass watchdog started")
        has_timed_out = False
        while True:
            # Prevent max CPU by forced loop slow down when self.event.is_set() is permanently high
            time.sleep(0.2)
            # This is the actual timer:
            # self.event.wait() aborts immediately when event.is_set becomes True
            self.event.wait(2)
            if self.event.is_set():
                has_timed_out = False
            else:
                if not has_timed_out:
                    self.timeout_action()
                # Save that we have timed out before, so time-out event handler is run only on the first time out
                has_timed_out = True


def card_timeout_handler() -> None:
    """
    The function defining the action on card removal in place-not-swipe mode

    :return: None
    """
    logger.info("Time-out handler: card removal detected. Pausing playback due to 'place not swipe' option")
    try:
        subprocess.run(f"{script_path}/playout_controls.sh -c=playerpauseforce -v=0.1", shell=True, check=False)
        pass
    except OSError as e:
        logger.info(f"Execution of Pause failed with {e}")


def read_card_worker(reader_module, reader_params, global_params, timer_thread) -> None:
    """
    The actual wait-for-card-and-do-something endless loop routine

    This routine is started once for each rfid reader instance in a dedicated thread. If there is only one rfid reader,
    this gets started in the main thread. The timer_thread is 'shared' across all  worker threads.

    :param reader_module: Reader module reference
    :param reader_params: Parameters to be passed to the rfid reader
    :param global_params: Parameters controlling this function
    :param timer_thread: Optional timer for card removal detection in place-not-swipe mode
    :return: None
    """
    # Decode global configuration parameters
    cfg_log_ignored_cards = global_params['log_ignored_cards']
    cfg_same_id_delay = global_params['same_id_delay']
    cfg_cmd_cards = global_params['cmd_cards']
    if cfg_cmd_cards is None:
        cfg_cmd_cards = []

    # Initialization
    previous_id = ''
    previous_time = time.time()

    if timer_thread is not None:
        logger.debug(f"card_removal_timer_thread.native_id = {timer_thread.ident}")
        timer_thread.event.clear()

    with reader_module.ReaderClass(reader_params) as reader:
        for card_id in reader:
            if timer_thread is not None:
                timer_thread.event.set()
            # Test for empty strings or NoneType. Both are accepted for indicating that no card was found
            if card_id:
                if card_id != previous_id or (time.time() - previous_time) >= cfg_same_id_delay or card_id in cfg_cmd_cards:
                    previous_id = card_id
                    logger.info(f"Trigger play card id = '{card_id}'")
                    try:
                        subprocess.run(f"{script_path}/rfid_trigger_play.sh --cardid={card_id}", shell=True, check=False)
                        pass
                    except OSError as e:
                        logger.error(f"rfid_trigger_play.sh execution failed: {e}")
                elif cfg_log_ignored_cards:
                    logger.debug(f"'Ignoring card id {card_id} due to same-card-delay ({cfg_same_id_delay}s)")
                previous_time = time.time()

            # Slow down the card reading while loop in case card is placed permanently on reader
            time.sleep(0.2)
            if timer_thread is not None:
                timer_thread.event.clear()


def create_read_card_workers(reader_cfg_file, logger_level=None) -> None:
    """
    Prepare everything to enter the card reading routine(s) for the single/multiple rfid readers

    :param reader_cfg_file: reader configuration file
    :param logger_level: override logger level to this value. If None read logger level from configuration file. If that is not present, use default
    :return: None
    """
    # Set the default logger (to make sure it is set consistently) for the next few commands
    logconsole.setLevel(logging.INFO)
    readersupport.logconsole.setLevel(logging.INFO)

    # Load the rfid reader module and reader configuration
    config_dict = readersupport.read_config(reader_cfg_file)
    config = configparser.ConfigParser()
    config.read_dict(config_dict)

    # Adjust the logger level based on command line override or config file
    if logger_level:
        # Command line logger level overrides default level and rfid_reader.ini level
        logconsole.setLevel(logging.DEBUG)
    else:
        # Check the config file for custom logger level
        logger_decode = {'debug': logging.DEBUG,
                         'info': logging.INFO,
                         'warning': logging.WARNING,
                         'error': logging.ERROR,
                         'critical': logging.CRITICAL}
        try:
            logger_level = logger_decode[config['ReaderType'].get('logger_level', fallback='info')]
        except KeyError:
            logger.warning(f"Unknown logger_level = '{logger_level}'. Using default: 'info'.")
    # Set the requested logger level
    logconsole.setLevel(logger_level)
    readersupport.logconsole.setLevel(logger_level)
    logger.info(f"Logger level is now {logger_level}")

    reader_module, reader_params = readersupport.load_reader(config_dict)
    logger.debug(f"reader_module = {reader_module}")
    logger.debug(f"reader_params = {reader_params}")

    if len(reader_params) != len(reader_module):
        raise ValueError("List length mismatch in reader modules and reader params")

    # Read in the parameters from the global configuration files
    global_params = get_global_params()
    # Add the global parameters from the rfid_reader.ini file to the params struct for global parameters
    global_params['log_ignored_cards'] = config['ReaderType'].getboolean('log_ignored_cards', fallback=False)

    card_removal_timer_thread = None
    # Only create the timer thread for card removal detection if we need it
    if global_params['place_not_swipe']:
        card_removal_timer_thread = CardRemovalTimerClass(card_timeout_handler)
        card_removal_timer_thread.daemon = True
        card_removal_timer_thread.start()

    if len(reader_params) == 1:
        # The simple case: single rfid reader only
        logger.info(f"Single instance RFID reader")
        read_card_worker(reader_module[0], reader_params[0], global_params, card_removal_timer_thread)
    else:
        # The complicated case: multiple parallel rfid readers
        logger.info(f"Starting parallel threads for {len(reader_module)}  RFID readers")

        reader_threads = [threading.Thread(target=read_card_worker,
                                           args=(rm, rp, global_params, card_removal_timer_thread)) for rm, rp in zip(reader_module, reader_params)]
        # Start all threads
        for t in reader_threads:
            t.daemon = True
            t.start()
        # Wait for all threads to finish (but get all started first!)
        # Will never happen as threads are endless loops waiting for RFID cards
        for t in reader_threads:
            t.join()
        # This code will never be reached
        print("All rfid reader threads finished")

        # Alternative using futures (how does that tie in with use of threading for the timer above?)
        # # Make sure there are enough workers: one per blocking card read i/o and one for this main thread one for the timer!
        # logger.info(f"To interrupt by keyboard, press Ctrl-C TWICE / THRICE")
        # import concurrent.futures
        # with concurrent.futures.ThreadPoolExecutor(max_workers=len(reader_params) + 2) as pool:
        #     workers = [pool.submit(action_handler, rm, rp, global_params, card_removal_timer_thread) for rm, rp in zip(reader_module, reader_params)]
        #     # Implicitly part of with ... as pool: done, pending = concurrent.futures.wait(workers)


if __name__ == '__main__':
    # Parse the arguments and get the script started :-)

    # The default config file relative to this files location and independent of working directory
    default_reader_cfg_file = script_path + '/../settings/rfid_reader.ini'

    parser = argparse.ArgumentParser()
    parser.add_argument("-v", "--verbosity",
                        help="Increase verbosity to 'DEBUG'",
                        action="store_const", const=logging.DEBUG, default=None)
    parser.add_argument("-c", "--conffile",
                        help=f"Reader configuration file [default: '{default_reader_cfg_file}']",
                        metavar="FILE", default=default_reader_cfg_file)
    args = parser.parse_args()

    create_read_card_workers(args.conffile, args.verbosity)
