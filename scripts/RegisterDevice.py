#!/usr/bin/env python2
# Forked from Francisco Sahli's https://github.com/fsahli/music-cards/blob/master/config.py
import os.path
from Reader import get_devices

devices = get_devices()

print "Choose the reader from list:"
for i in range(len(devices)):
    print i, devices[i].name

dev_id = int(raw_input('Device Number: '))

path = os.path.dirname(os.path.realpath(__file__))
with open(path + '/deviceName.txt', 'w') as f:
    f.write(devices[dev_id].name)
    f.close()
