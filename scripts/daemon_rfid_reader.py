#!/usr/bin/env python3

import logging
import os
import subprocess
import time
import re
import signal
import sys

# Add the path for the reader modules to Python's search path
# such the reader directory is searched after local dir, but before all others
reader_path = os.path.realpath(os.path.realpath(os.path.dirname(__file__)) + '/../components/rfid-reader')
sys.path.insert(1, reader_path)
import readersupport

logger = logging.getLogger(os.path.basename(__file__).ljust(25))
logger.setLevel(logging.DEBUG)
ch = logging.StreamHandler()
ch.setLevel(logging.INFO)
ch.setFormatter(logging.Formatter('%(asctime)s - %(name)s - %(levelname)-8s: %(message)s', datefmt='%d.%m.%Y %H:%M:%S'))
logger.addHandler(ch)

# Load the rfid reader module and reader configuration
readersupport.logconsole.setLevel(logging.DEBUG)
reader_cfg_file = os.path.abspath(os.path.dirname(os.path.realpath(__file__)) + '/../settings/rfid_reader.ini')
reader_module, reader_params = readersupport.load_reader(readersupport.read_config(reader_cfg_file))

# get absolute path of this script
dir_path = os.path.dirname(os.path.realpath(__file__))
logger.info('Dir_PATH: {dir_path}'.format(dir_path=dir_path))

# get control card ids
file_path = os.path.dirname(__file__)
if file_path != "":
    os.chdir(file_path)

# vars for ensuring delay between same-card-swipes
ssp = open('../settings/Second_Swipe_Pause', 'r')
same_id_delay = ssp.read().strip()
sspc = open('../settings/Second_Swipe_Pause_Controls', 'r')
sspc_nodelay = sspc.readline().strip()
previous_id = ""
previous_time = time.time()

# get swipe or place configuration value
sop = open('../settings/Swipe_or_Place', 'r')
swipe_or_place = sop.read().strip()

# create array for control card ids
cards = []

# open file and read the content in a list
with open('../settings/global.conf', 'r') as filehandle:
    filecontents = filehandle.readlines()

    for line in filecontents:
        cids = line[:-1]
        cards.append(cids)


extract = [s for s in cards if s.startswith('CMD')]
string = ''.join(extract)

# if controlcards delay is deactivated, let the cards pass, otherwise, they have to wait...
if sspc_nodelay == "ON":
    ids = re.findall("(\d+)", string)
else:
    ids = ""


# handler for RFID reading no cardid
def handler(signum, frame):
    logger.info('No RFID Signal detected.')
    try:
        # force pause the player script
        logger.info('Trigger Pause Force')
        subprocess.call([dir_path + '/playout_controls.sh -c=playerpauseforce -v=0.1'], shell=True)
    except OSError as e:
        logger.info('Execution of Pause failed.')


# associate the handler to signal alarm
signal.signal(signal.SIGALRM, handler)

with reader_module.Reader(reader_params) as reader:

    while True:
        # slow down the card reading while loop
        # in case card is placed permanently on reader
        time.sleep(0.2)

        if swipe_or_place == "PLACENOTSWIPE":
            # enable the signal alarm (if no card is present for 1 second)
            signal.alarm(1)

        # reading the card id
        # NOTE: it's been reported that KKMOON Reader might need the following line altered.
        # Instead of:
        # cardid = reader.reader.readCard()
        # change the line to:
        # cardid = reader.readCard()
        # See here for (German ;) details:
        # https://github.com/MiczFlor/RPi-Jukebox-RFID/issues/551
        cardid = reader.read_card()

        # disable the alarm after a successful read
        signal.alarm(0)

        try:
            # start the player script and pass on the cardid (but only if new card or otherwise
            # "same_id_delay" seconds have passed)
            # Test for empty strings or NoneType. Both are accepted for indicating that no card was found.
            if cardid:
                if cardid != previous_id or (time.time() - previous_time) >= float(same_id_delay) or cardid in str(ids):
                    logger.info('Trigger Play Cardid={cardid}'.format(cardid=cardid))
                    subprocess.call([dir_path + '/rfid_trigger_play.sh --cardid=' + cardid], shell=True)
                    previous_id = cardid

                else:
                    logger.debug('Ignoring Card id {cardid} due to same-card-delay, delay: {same_id_delay}'.format(
                        cardid=cardid,
                        same_id_delay=same_id_delay
                    ))

                previous_time = time.time()

        except OSError as e:
            logger.error('Execution failed: {e}'.format(e=e))
