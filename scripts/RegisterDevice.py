#!/usr/bin/env python2

import os.path
from Reader import get_devices

devices = get_devices()
path = os.path.dirname(os.path.realpath(__file__))
i = 0
print "Choose the reader from list"
for dev in devices:
	print i, dev.name
	i += 1

dev_id = int(raw_input('Device Number: '))

with open(path + '/deviceName.txt','w') as f:
	f.write(devices[dev_id].name)
	f.close()
