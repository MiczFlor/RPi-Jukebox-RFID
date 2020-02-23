#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# import threading
import sys, os.path
import signal
from Phoniebox import Phoniebox
from time import sleep, time

# get absolute path of this script
dir_path = os.path.dirname(os.path.realpath(__file__))
defaultconfigFilePath = os.path.join(dir_path, 'phoniebox.conf')

# watchdog blocks the script, so it cannot be used in the same file as the PhonieboxDaemon
# from watchdog.observers import Observer
# from watchdog.events import FileSystemEventHandler
# from os.path import dirname

# class FileModifiedHandler(FileSystemEventHandler):

#    """ watch the given file for changes and execute callback function on modification """
#    def __init__(self, file_path, callback):
#        self.file_path = file_path
#        self.callback = callback

#        # set observer to watch for changes in the directory
#        self.observer = Observer()
#        self.observer.schedule(self, dirname(file_path), recursive=False)
#        self.observer.start()
#        try:
#            while True:
#                sleep(1)
#        except KeyboardInterrupt:
#            self.observer.stop()
#        self.observer.join()
#
#    def on_modified(self, event):
#        # only act on the change that we're looking for
#        if not event.is_directory and event.src_path.endswith(self.file_path):
#            daemon.log("cardAssignmentsFile modified!",3)
#            self.callback() # call callback


class PhonieboxDaemon(Phoniebox):
    """ This subclass of Phoniebox is to be called directly, running as RFID reader daemon """

    def __init__(self, configFilePath=defaultconfigFilePath):
        Phoniebox.__init__(self, configFilePath)
        self.lastplayedID = 0

    def run(self):
        # do things if killed
        signal.signal(signal.SIGINT, self.signal_handler)
        signal.signal(signal.SIGTERM, self.signal_handler)

        # establish mpd connection
        self.mpd_init_connection()
        self.mpd_init_settings()
        state = self.client.status()["state"]

        daemon.play_alsa(daemon.get_setting("phoniebox", 'startup_sound'))
        if state == "play":
            self.client.play()

        # launch watcher for config files, blocks the script
        # TODO: it would be better to watch the changes with a second process that
        # tells the PhonieboxDaemon to reload the config whenever needed.

        # card_assignments_file = daemon.get_setting("phoniebox","card_assignments_file")
        # cardAssignmentsWatchdog = FileModifiedHandler(card_assignments_file, self.update_cardAssignments)
        # ConfigWatchdog = FileModifiedHandler(configFilePath, self.read_config)

#        # start_reader runs an endless loop, nothing will be executed afterwards
        daemon.start_reader()

    def start_reader(self):
        from Reader import Reader
        reader = Reader()

        card_detection_sound = self.get_setting("phoniebox", "card_detection_sound")
        debounce_time = self.get_setting("phoniebox", "debounce_time")
        if debounce_time == -1:
            debounce_time = 0.5
        second_swipe_delay = self.get_setting("phoniebox", "second_swipe_delay")
        if second_swipe_delay == -1:
            second_swipe_delay = 0
        store_card_assignments = self.get_setting("phoniebox", "store_card_assignments")
        if store_card_assignments == -1:
            store_card_assignments = 30
        last_swipe = 0
        last_write_card_assignments = 0

        while True:
            # reading the card id
            cardid = reader.reader.readCard()
#            cardid = None
#            sleep(debounce_time)
            try:
                # start the player script and pass on the cardid
                if cardid is not None:
                    print("Card ID: {}".format(int(cardid)))
                    filename = self.get_setting("phoniebox", "Latest_RFID_file")
                    if filename != -1:
                        self.print_to_file(filename, "\'{}\' was used at {}".format(cardid, time()))
                    if card_detection_sound != -1:
                        self.play_alsa(card_detection_sound)
                    if cardid in self.cardAssignments.sections():
                        # second swipe detection
                        if int(cardid) == int(self.lastplayedID) and time()-last_swipe > second_swipe_delay:
                            self.log("Second swipe for {}".format(cardid), 3)
                            self.do_second_swipe()
                        # if first swipe, just play
                        else:
                            last_swipe = time()
                            self.do_start_playlist(cardid)
                        # do not react for debounce_time
                        sleep(debounce_time)
                    else:
                        self.log("Card with ID {} not mapped yet.".format(cardid), 1)

            except OSError as e:
                print("Execution failed:", e)

            # check if it is time for the next update of the cardAssignments and do it
            # Note: this is purely time-based and not clever at all. Find a
            # TODO: find a better way to check for changes in the files on disk to trigger the update
            if time()-last_write_card_assignments > store_card_assignments and store_card_assignments != False:
                # store card assignments
                if self.get_setting("phoniebox", "translate_legacy_cardassignments", "bool") == True:
                    legacy_cardAssignments = self.translate_legacy_cardAssignments(last_write_card_assignments)
                    self.update_cardAssignments(legacy_cardAssignments)
                else:
                    self.update_cardAssignments(self.read_cardAssignments)

                self.write_new_cardAssignments()
                last_write_card_assignments = time()

    def signal_handler(self, signal, frame):
        """ catches signal and triggers the graceful exit """
        print("Caught signal {}, exiting...".format(signal))
        self.exit_gracefully()

    def exit_gracefully(self):
        """ stop mpd and write cardAssignments to disk if daemon is stopped """
        self.mpd_connect_timeout()
        self.client.stop()
        self.client.disconnect()
        # write config to update playstate
        self.write_new_cardAssignments()

        # exit script
        sys.exit(0)


if __name__ == "__main__":

    # if called directly, launch Phoniebox.py as rfid-reader daemon
    # treat the first argument as defaultconfigFilePath if given
    if len(sys.argv) <= 1:
        configFilePath = defaultconfigFilePath
    else:
        configFilePath = sys.argv[1]

    daemon = PhonieboxDaemon(configFilePath)

    # setup the signal listeners
    signal.signal(signal.SIGINT, daemon.exit_gracefully)
    signal.signal(signal.SIGTERM, daemon.exit_gracefully)

    # start the daemon (blocking)
    daemon.run()
