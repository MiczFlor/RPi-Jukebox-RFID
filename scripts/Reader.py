import string
import csv
import os.path
import sys

from evdev import InputDevice, categorize, ecodes, list_devices
from select import select
class Reader:
	def __init__(self):
		path = os.path.dirname(os.path.realpath(__file__))
		self.keys = "X^1234567890XXXXqwertzuiopXXXXasdfghjklXXXXXyxcvbnmXXXXXXXXXXXXXXXXXXXXXXX"
		if not os.path.isfile(path + '/deviceName.txt'):
			sys.exit('Please run config.py first')
		else: 
			with open(path + '/deviceName.txt','r') as f:
				deviceName = f.read()
			devices = [InputDevice(fn) for fn in list_devices()]
			for device in devices:
				if device.name == deviceName:
					self.dev = device
					break 		
			try:
				self.dev
			except:
				sys.exit('Could not find the device %s\n. Make sure is connected' % deviceName)
		
	def readCard(self):
		stri=''
		key = ''
		while key != 'KEY_ENTER':
		   r,w,x = select([self.dev], [], [])
		   for event in self.dev.read():
			if event.type==1 and event.value==1:
				stri+=self.keys[ event.code ]
				#print( keys[ event.code ] )
				key = ecodes.KEY[ event.code ]
		return stri[:-1]

