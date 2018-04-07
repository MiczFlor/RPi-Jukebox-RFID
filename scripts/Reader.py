# Forked from Francisco Sahli's https://github.com/fsahli/music-cards/blob/master/Reader.py

import string
import csv
import os.path
import sys

from evdev import InputDevice, categorize, ecodes, list_devices
from select import select


class Reader:

	self.deviceName = None
	self.dev = None
	
	# Mapping table for Even.Code from reader
	self.keys = "X^1234567890XXXXqwertzuiopXXXXasdfghjklXXXXXyxcvbnmXXXXXXXXXXXXXXXXXXXXXXX"
	
	def __init__(self):
		path = os.path.dirname(os.path.realpath(__file__))
		
		# check if device has been selected
		# file is created by using script RegisterDevice.py
		if os.path.isfile(os.path.join(path, '/deviceName.txt'):
			
			with open(path + '/deviceName.txt','r') as f:
				self.deviceName = f.read()
			
			# select device by name
			devices = [InputDevice(fn) for fn in list_devices()]
			for device in devices:
				if device.name == self.deviceName:
					self.dev = device
					break
			#end for
		
	def readCard(self):
		stri = ''
		key  = ''
		while key != 'KEY_ENTER':
		   r,w,x = select([self.dev], [], [])
		   for event in self.dev.read():
			if event.type==1 and event.value==1:
				stri+=self.keys[ event.code ]
				key = ecodes.KEY[ event.code ]
		return stri[:-1]

