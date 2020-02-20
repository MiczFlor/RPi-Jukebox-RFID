#!/usr/bin/env python3

import subprocess
import os 
from Reader import Reader

reader = Reader()

# get absolute path of this script
dir_path = os.path.dirname(os.path.realpath(__file__))

print(dir_path)

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
            # start the player script and pass on the cardid
            if cardid != None:
                subprocess.call([dir_path + '/rfid_trigger_play.sh --cardid=' + cardid], shell=True)
        except OSError as e:
            print("Execution failed:")
