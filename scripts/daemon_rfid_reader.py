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
import signal
from functools import partial

import RPi.GPIO as gpio


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


class PinActionClass(threading.Thread):
    """
    A thread to control a GPIO output pin to sound a buzzer or light an LED

    An extra thread for a GPIO pin? Why so complicated?
    Reason 1: This is a single thread for all RFID reader threads (if there is more than one), because we only
    have a single GPIO pin and access must be properly sequenced to ensure it is reset after sounding the buzzer
    Reason 2: The time the buzzer is sounded should be run in background to avoid extra delay between card placement and
    card action however small the buzzer duration

    Note: You can connect a LED or a Piezzo Buzzer. Only for reasons of simplicity, parameters are named 'buzzer'

    The GPIO level is active high, after a card has been detected for the length of buzz_duration
    """
    def __init__(self, buzz_pin, buzz_duration, buzz_retrigger=True):
        """

        :param buzz_pin: The GPIO pin of the buzzer of LED
        :param buzz_duration: The duration in sec the GPIO pin is high after a card has been detected (e.g. 0.2)
        :param buzz_retrigger: If True, multiple cards within the buzz_duration start the buzzer time anew
        """
        threading.Thread.__init__(self)
        logger.debug(f"PinActionClass started with buzz_pin={buzz_pin}, buzz_duration={buzz_duration}, buzz_retrigger={buzz_retrigger}")
        self.trigger = threading.Event()
        self.buzz_pin = buzz_pin
        self.buzz_delay = buzz_duration
        if buzz_retrigger:
            self.run_action = self.run_retrigger
        else:
            self.run_action = self.run_single_trigger

        # Initialize RPi.GPIO here, as this is only required when a buzzer is configured
        gpio.setmode(gpio.BCM)
        gpio.setup(self.buzz_pin, gpio.OUT, initial=gpio.LOW)
        gpio.output(self.buzz_pin, gpio.LOW)

    def run_retrigger(self) -> None:
        """
        The wait-for-trigger-and-do-it endless loop for the re-triggerable case
        """
        while True:
            self.trigger.wait()
            # Clear the trigger, so we can detect a new event while doing the pin high wait
            self.trigger.clear()
            gpio.output(self.buzz_pin, gpio.HIGH)
            # Wait for duration unless, another trigger event already comes in
            self.trigger.wait(self.buzz_delay)
            # Set the pin low for a very small length of time, to provide a feedback that card re-trigger has happend
            gpio.output(self.buzz_pin, gpio.LOW)
            time.sleep(0.1)

    def run_single_trigger(self) -> None:
        """
        The wait-for-trigger-and-do-it endless loop for the non re-triggerable case
        """
        while True:
            self.trigger.wait()
            gpio.output(self.buzz_pin, gpio.HIGH)
            # A blocking wait to ignore changes on trigger
            time.sleep(self.buzz_delay)
            gpio.output(self.buzz_pin, gpio.LOW)
            # Only clear the trigger after full delay time, to also clear any trigger that came in during the wait
            self.trigger.clear()

    def run(self):
        self.run_action()

    def cleanup(self):
        """
        The abort handler to ensure pin is low active on exit

        Note: This does not get called automatically. It needs to be taken care of on program exit!
        """
        gpio.output(self.buzz_pin, gpio.LOW)
        gpio.cleanup()


def termination_handler(func, signal_number, frame) -> None:
    """
    Handler for termination signal

    This is only be needed when GPIO pins are used, to ensure these are reset to low before exiting

    :param func: The function to execute for cleanup before exiting the program. In the typical setup, this is PinActionClass.cleanup
    :param signal_number: signal number
    :param frame: stack frame index
    """
    logger.info(f"Termination handler: caught signal {signal_number}")
    func()
    if signal_number == signal.SIGINT:
        raise KeyboardInterrupt
    else:
        sys.exit()


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
        self.trigger = threading.Event()
        self.timeout_action = timeout_action

    def run(self):
        logger.debug("CardRemovalTimerClass watchdog started")
        has_timed_out = True
        while True:
            # Prevent max CPU by forced loop slow down when self.trigger.is_set() is permanently high
            time.sleep(0.2)
            # This is the actual timer:
            # self.trigger.wait() aborts immediately when trigger.is_set becomes True
            self.trigger.wait(2)
            if self.trigger.is_set():
                has_timed_out = False
            else:
                if not has_timed_out:
                    self.timeout_action()
                # Save that we have timed out before, so time-out event handler is run only on the first time out
                has_timed_out = True


def card_timeout_action() -> None:
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


def read_card_worker(reader_module, reader_params, global_params,
                     timer_thread: CardRemovalTimerClass = None, action_thread: PinActionClass = None) -> None:
    """
    The actual wait-for-card-and-do-something endless loop routine

    This routine is started once for each rfid reader instance in a dedicated thread. If there is only one rfid reader,
    this gets started in the main thread. The timer_thread is 'shared' across all  worker threads.

    :param reader_module: Reader module reference
    :param reader_params: Parameters to be passed to the rfid reader
    :param global_params: Parameters controlling this function
    :param timer_thread: Optional timer for card removal detection in place-not-swipe mode
    :param action_thread: Optional GPIO pin action thread
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
        timer_thread.trigger.clear()

    if action_thread is not None:
        logger.debug(f"card_removal_action_thread.native_id = {action_thread.ident}")
        action_thread.trigger.clear()

    with reader_module.ReaderClass(reader_params) as reader:
        for card_id in reader:
            if timer_thread is not None:
                timer_thread.trigger.set()
            # Test for empty strings or NoneType. Both are accepted for indicating that no card was found
            if card_id:
                if card_id != previous_id or (time.time() - previous_time) >= cfg_same_id_delay or card_id in cfg_cmd_cards:
                    # Do this first to provide fast audible/visual feed-back
                    if action_thread:
                        action_thread.trigger.set()
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
                timer_thread.trigger.clear()


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
    # Add the buzzer parameters: If section is missing in file, add empty section here, so all default parameters are used
    if 'BuzzOnCard' not in config.sections():
        config.add_section('BuzzOnCard')
    global_params['buzzer_enabled'] = config['BuzzOnCard'].getboolean('buzzer_enabled', fallback=False)
    global_params['buzzer_pin'] = config['BuzzOnCard'].getint('buzzer_pin', fallback=0)
    global_params['buzzer_duration'] = config['BuzzOnCard'].getfloat('buzzer_duration', fallback=0.3)
    global_params['buzzer_retrigger'] = config['BuzzOnCard'].getboolean('buzzer_retrigger', fallback=True)

    card_removal_timer_thread = None
    # Only create the timer thread for card removal detection if we need it
    if global_params['place_not_swipe']:
        card_removal_timer_thread = CardRemovalTimerClass(card_timeout_action)
        card_removal_timer_thread.daemon = True
        card_removal_timer_thread.start()

    pin_action_action_thread = None
    # Only create the pin action thread if we need it
    if global_params['buzzer_enabled']:
        pin_action_action_thread = PinActionClass(global_params['buzzer_pin'], global_params['buzzer_duration'], global_params['buzzer_retrigger'])
        # Catching the termination signal is only necessary, if we need to clean up GPIO pins
        # If a gpio pin is used (e.g. a buzzer) we MUST ensure it is low before exiting the program no matter how (imagine the noise!)
        signal.signal(signal.SIGTERM, partial(termination_handler, pin_action_action_thread.cleanup))
        signal.signal(signal.SIGINT, partial(termination_handler, pin_action_action_thread.cleanup))
        pin_action_action_thread.daemon = True
        pin_action_action_thread.start()

    if len(reader_params) == 1:
        # The simple case: single rfid reader only
        logger.info(f"Single instance RFID reader")
        read_card_worker(reader_module[0], reader_params[0], global_params, card_removal_timer_thread, pin_action_action_thread)
    else:
        # The complicated case: multiple parallel rfid readers
        logger.info(f"Starting parallel threads for {len(reader_module)}  RFID readers")

        reader_threads = [threading.Thread(target=read_card_worker,
                                           args=(rm, rp, global_params, card_removal_timer_thread, pin_action_action_thread)) for rm, rp in zip(reader_module, reader_params)]
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
