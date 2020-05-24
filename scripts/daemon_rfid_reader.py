#!/usr/bin/env python3

import logging
import os
import subprocess
import time

from Reader import Reader

logger = logging.getLogger()
logger.setLevel(logging.DEBUG)
ch = logging.StreamHandler()
ch.setLevel(logging.INFO)
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
ch.setFormatter(formatter)
logger.addHandler(ch)

reader = Reader()

# get absolute path of this script
dir_path = os.path.dirname(os.path.realpath(__file__))
logger.info('Dir_PATH: {dir_path}'.format(dir_path=dir_path))

# vars for ensuring delay between same-card-swipes
same_id_delay = 0
previous_id = ""
previous_time = time.time()

while True:
    # reading the card id
    # NOTE: it's been reported that KKMOON Reader might need the following line altered.
    # Instead of:
    # cardid = reader.reader.readCard()
    # change the line to:
    # cardid = reader.readCard()
    # See here for (German ;) details:
    # https://github.com/MiczFlor/RPi-Jukebox-RFID/issues/551
    cardid = reader.reader.readCard()
    try:
        # start the player script and pass on the cardid (but only if new card or otherwise
        # "same_id_delay" seconds have passed)
        if cardid is not None:
            if cardid != previous_id or (time.time() - previous_time) >= same_id_delay:
                logger.info('Trigger Play Cardid={cardid}'.format(cardid=cardid))
                subprocess.call([dir_path + '/rfid_trigger_play.sh --cardid=' + cardid], shell=True)
                previous_id = cardid
                previous_time = time.time()
            else:
                logger.debug('Ignoring Card id {cardid} due to same-card-delay, delay: {same_id_delay}'.format(
                    cardid=cardid,
                    same_id_delay=same_id_delay
                ))

    except OSError as e:
        logger.error('Execution failed: {e}'.format(e=e))
