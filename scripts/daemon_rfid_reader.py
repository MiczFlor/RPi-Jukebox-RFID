#!/usr/bin/env python3

import subprocess
import os, time
from Reader import Reader
import logging
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
logger.info(f'Dir_PATH: {dir_path}')

print(dir_path)

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
            # start the player script and pass on the cardid (but only if new card or otherwise "same_id_delay" seconds have passed)
            if cardid != None:
                if (cardid != previous_id or (time.time()-previous_time) >= same_id_delay):
                    logger.info(f'Trigger Play Cardid={cardid}')
                    subprocess.call([dir_path + '/rfid_trigger_play.sh --cardid=' + cardid], shell=True)
                    previous_id = cardid
                    previous_time = time.time()
                else:
                    logger.debug(f'Ignoring Card id {cardid} due to same-card-delay, delay: {same_id_delay}')

        except OSError as e:
            logger.error(f"Execution failed: {e}" )
