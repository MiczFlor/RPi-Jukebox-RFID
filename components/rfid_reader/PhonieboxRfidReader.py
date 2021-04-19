#!/usr/bin/env python3
# This alternative Reader.py script was meant to cover not only USB readers but more.
# It can be used to replace Reader.py if you have readers such as
# MFRC522, RDM6300 or PN532.
# Please use the github issue threads to share bugs and improvements
# or create pull requests.

import os.path
import sys

import logging

from rpc.PhonieboxRpcClient import PhonieboxRpcClient

#from evdev import InputDevice, categorize, ecodes, list_devices

logger = logging.getLogger(__name__)

def get_devices():
    devices = [InputDevice(fn) for fn in list_devices()]
    devices.append(NonUsbDevice('MFRC522'))
    devices.append(NonUsbDevice('RDM6300'))
    devices.append(NonUsbDevice('PN532'))
    return devices


class NonUsbDevice(object):
    name = None

    def __init__(self, name):
        self.name = name


class UsbReader(object):
    def __init__(self, device):
        self.keys = "X^1234567890XXXXqwertzuiopXXXXasdfghjklXXXXXyxcvbnmXXXXXXXXXXXXXXXXXXXXXXX"
        self.dev = device

    def readCard(self):
        from select import select
        stri = ''
        key = ''
        while key != 'KEY_ENTER':
            select([self.dev], [], [])
            for event in self.dev.read():
                if event.type == 1 and event.value == 1:
                    stri += self.keys[event.code]
                    key = ecodes.KEY[event.code]
        return stri[:-1]


class RFID_Reader(object):
    def __init__(self,device_name,param=None):

        if device_name == 'MFRC522':
            from . import RfidReader_RC522
            self.reader = Mfrc522Reader()
        elif device_name == 'RDM6300':
            from . import RfidReader_RDM6300
            self.reader = Rdm6300Reader(param)
        elif device_name == 'PN532':
            from . import RfidReader_PN532
            self.reader = Pn532Reader()
        elif device_name == 'Fake':
            from .FakeRfidReader import FakeReader
            self.reader = FakeReader()
        else:
            try:
                device = [device for device in get_devices() if device.name == device_name][0]
                self.reader = UsbReader(device)
            except IndexError:
                sys.exit('Could not find the device %s.\n Make sure it is connected' % device_name)

        self.PhonieboxRpc = PhonieboxRpcClient()
        self.PhonieboxRpc.connect()
        self._keep_running = True
        self.cardnotification = None
        self.valid_cardnotification = None
        self.invalid_cardnotification = None

    def set_cardid_db(self,cardid_db):
        ##potentially dangerous for runtime updates, needs look?
        if cardid_db != None:
            self.cardid_db = cardid_db

    def get_card_assignment(self,cardid):
        ##potentially dangerous for runtime updates, needs look?
        return self.cardid_db.get(cardid)

    def get_last_card_id(self):
        return self.last_card_id

    def set_cardnotification(self, callback):
        if callable(callback):
            self.cardnotification = callback

    def set_valid_cardnotification(self, callback):
        if callable(callback):
            self.valid_cardnotification = callback
    
    
    def set_invalid_cardnotification(self, callback):
        if callable(callback):
            self.invalid_cardnotification = callback

    
    def terminate(self):
        self._keep_running = False
    
    def run(self):

        self._keep_running = True
        ##card_detection_sound = self.get_setting("phoniebox", "card_detection_sound")  <-- this module should not deciede about sound
        #debounce_time = self.get_setting("phoniebox", "debounce_time")
        #if debounce_time == -1:
        #    debounce_time = 0.5
        #second_swipe_delay = self.get_setting("phoniebox", "second_swipe_delay")
        #if second_swipe_delay == -1:
        #    second_swipe_delay = 0
        #store_card_assignments = self.get_setting("phoniebox", "store_card_assignments")
        #if store_card_assignments == -1:
        #    store_card_assignments = 30
        #last_swipe = 0
        #last_write_card_assignments = 0

        ## who does know about card ids?
        ##the reader?
        ##    -> reader would know about titles? how much can this be? none will deal with more then100 cards? 
        ##    -> would be ok or? How das webui trigger this? how is mpd triggered, lets look up
        ##core?
        ##    -> core would need to ditribute functions -> bad
        ##      -> Reader knows about IDs eecuitng a command, everything else is treted -> maybe

        while self._keep_running:               #since readCard is a blocking call, this will not work
            cardid = self.reader.readCard()  
            self.last_card_id = cardid

            if self.cardnotification is not None:
                self.cardnotification(cardid)

            card_assignment = self.get_card_assignment(cardid)

            if card_assignment is not None:    
                
                #probably deal with 2nd swipe here
                
                if self.valid_cardnotification is not None:
                    self.valid_cardnotification()
                #queue = phoniebox_object_access_queue()
                #queue.connect()
                resp = self.PhonieboxRpc.enqueue(card_assignment)

                
                #hm, what to do with response here?

            else:
                if self.invalid_cardnotification is not None:
                    self.invalid_cardnotification()

                
                #ok, card not in database,
                
                
                
                #try:
                    # start the player script and pass on the cardid
                #    if cardid is not None:
                #        print("Card ID: {}".format(int(cardid)))
                #        filename = self.get_setting("phoniebox", "Latest_RFID_file")
                #        if filename != -1:
                #            self.print_to_file(filename, "\'{}\' was used at {}".format(cardid, time()))
                #        if card_detection_sound != -1:
                #            self.play_alsa(card_detection_sound)
                #        if cardid in self.cardAssignments.sections():
                #            # second swipe detection
                #            if int(cardid) == int(self.lastplayedID) and time()-last_swipe > second_swipe_delay:
                #                self.log("Second swipe for {}".format(cardid), 3)
                #                self.do_second_swipe()
                #            # if first swipe, just play
                #            else:
                #                last_swipe = time()
                #                self.do_start_playlist(cardid)
                #            # do not react for debounce_time
                #            sleep(debounce_time)
                #        else:
                #            self.log("Card with ID {} not mapped yet.".format(cardid), 1)
#
                #except OSError as e:
                #    print("Execution failed:", e)
#
            # check if it is time for the next update of the cardAssignments and do it                  
            # Note: this is purely time-based and not clever at all. Find a
            # TODO: find a better way to check for changes in the files on disk to trigger the update
            ## <- this module should not deceide about card_id updates
            #if time()-last_write_card_assignments > store_card_assignments and store_card_assignments != False:
            #    # store card assignments
            #    if self.get_setting("phoniebox", "translate_legacy_cardassignments", "bool") == True:
            #        legacy_cardAssignments = self.translate_legacy_cardAssignments(last_write_card_assignments)
            #        self.update_cardAssignments(legacy_cardAssignments)
            #    else:
            #        self.update_cardAssignments(self.read_cardAssignments)

            #    self.write_new_cardAssignments()
            #    last_write_card_assignments = time()
        return 1

