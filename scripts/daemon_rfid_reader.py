#!/usr/bin/env python2

import subprocess
import os 
from Reader import Reader

reader = Reader()

# get absolute path of this script
dir_path = os.path.dirname(os.path.realpath(__file__))

print dir_path

while True:
        # reading the card id
        cardid = reader.reader.readCard()
        try:
            # start the player script and pass on the cardid
            if cardid != None:
                subprocess.call([dir_path + '/rfid_trigger_play.sh --cardid=' + cardid], shell=True)
        except OSError as e:
            print "Execution failed:" 