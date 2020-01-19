#!/usr/bin/env python3
# -*- coding: utf-8 -*-

__name__ = "Phoniebox"

import configparser # needed only for the exception types ?!
from ConfigParserExtended import ConfigParserExtended
import codecs
import subprocess # needed for aplay call
import os,sys
from time import sleep
from mpd import MPDClient

# get absolute path of this script
dir_path = os.path.dirname(os.path.realpath(__file__))
defaultconfigFilePath = os.path.join(dir_path,'./phoniebox.conf')

# TODO: externalize helper functions for the package. How?
def is_int(s):
    """ return True if string is an int """
    try:
        int(s)
        return True
    except ValueError:
        return False

def str2bool(s):
    """ convert string to a python boolean """
    return s.lower() in ("yes", "true", "t", "1")

def str2num(s):
    """ convert string to an int or a float """
    try:
        return int(s)
    except ValueError:
        return float(s)

def find_modified_files(path,since):
    modified_files = []
    for root, dirs, files in os.walk(path):
        for basename in files:
            filename = os.path.join(path, basename)
            status = os.stat(filename)
            if status.st_mtime > since:
               modified_files.append(filename)
    return  modified_files

def file_modified(filename,since):
    if os.stat(filename).st_mtime > since:
        return True
    else:
        return False


class Phoniebox(object):

    def __init__(self,configFilePath=defaultconfigFilePath):
        print("Using configuration file {}".format(configFilePath))
        self.read_config(configFilePath)
        # read cardAssignments from given card assignments file
        card_assignments_file = self.get_setting("phoniebox","card_assignments_file")
        self.cardAssignments = self.read_cardAssignments()
        if self.get_setting("phoniebox","translate_legacy_cardassignments","bool") == True:
            self.log("Translating legacy cardAssignment config from folder.conf files.",3)
            legacy_cardAssignments = self.translate_legacy_cardAssignments()
            self.update_cardAssignments(legacy_cardAssignments)


    def log(self,msg,level=3):
        """ level based logging to stdout """
        log_level_map = {0:None,1:"error",2:"warning",3:"info",4:"extended",5:"debug"}
        log_level = int(self.get_setting("phoniebox","log_level"))
        if log_level >= level and log_level != -1:
            print("{}: {}".format(log_level_map[level].upper(),msg))


    def mpd_init_connection(self):
        """ connect to mpd """
        host = self.get_setting("mpd","host")
        if host == -1:
            host = "localhost"
        port = self.get_setting("mpd","port")
        if port == -1:
            port = 6600
        timeout = self.get_setting("mpd","timeout")
        if timeout == -1:
            timeout = 3

        self.client = MPDClient()
        self.client.host = host
        self.client.port = port
        self.client.timeout = timeout

        #ret = self.mpd_connect_timeout()
        if self.mpd_connect_timeout() != 0:
            sys.exit()
        else:
            self.log("connected to MPD with settings host = {}, port = {}, timeout = {}".format(host,port,timeout),3)

    def mpd_connect_timeout(self):
        """ establishes the connection to MPD when disconnected """
        success = False
        runtime = 0
        try:
            self.client.disconnect()
        except:
            pass
        while success != True and runtime <= self.client.timeout:
            try:
                self.client.connect(self.client.host,self.client.port)
                success = True
                self.log("Connected to MPD at {} on port {}.".format(self.client.host,self.client.port),5)
                return 0
            except:
                self.log("Could not connect to MPD, retrying.",5)
            sleep(0.2)
            runtime += 0.2
            if runtime >= self.client.timeout:
                self.log("Could not connect to MPD for {}s, giving up.".format(self.client.timeout),2)
                return 1


    def do_second_swipe(self):
       """ react to the second swipe of the same card according to settings"""
       second_swipe_map = { 'default':     self.do_restart_playlist,
                            'restart':     self.do_restart_playlist,
                            'restart_track':self.do_restart_track,
                            'stop':        self.do_stop,
                            'pause':       self.do_toggle,
                            'noaudioplay': self.do_pass,
                            'skipnext':    self.do_next,
       }
       setting_key = "second_swipe"
       map_key = self.config.get("phoniebox",setting_key)
       try:
           second_swipe_map[map_key]()
       except KeyError as e:
           self.log("Unknown setting \"{} = {}\", using \"{} = default\".".format(setting_key,map_key,setting_key),5)
           second_swipe_map['default']()

    def do_restart_playlist(self):
        """ restart the same playlist from the beginning """
        # TODO: Any reason not to just start the first item in the current playlist?
        self.mpd_connect_timeout()
        self.set_mpd_playmode(self.lastplayedID)
        self.play_mpd(self.get_cardsetting(self.lastplayedID,"uri"))

    def do_restart_track(self):
        """ restart currently playing track """
        self.mpd_connect_timeout()
        mpd_status = self.client.status()
        self.set_mpd_playmode(self.lastplayedID)
        # restart current track
        self.client.play(mpd_status['song'])

    def do_start_playlist(self,cardid):
        """ restart the same playlist, eventually resume """
        if self.get_cardsetting(self.lastplayedID,"resume"):
            self.resume(self.lastplayedID,"save")
        self.mpd_connect_timeout()
        self.set_mpd_playmode(cardid)
        self.play_mpd(self.get_cardsetting(cardid,"uri"))
        if self.get_cardsetting(cardid,"resume"):
            self.resume(cardid,"resume")
        self.lastplayedID = cardid

    def do_toggle(self):
        """ toggle play/pause """
        self.mpd_connect_timeout()
        status = self.client.status()
        if status['state'] == "play":
            self.client.pause()
        else:
            self.client.play()

    def do_pass(self):
        """ do nothing (on second swipe with noaudioplay) """
        pass

    def do_next(self):
        """ skip to next track or restart playlist if stopped (on second swipe with noaudioplay) """
        self.mpd_connect_timeout()
        status = self.client.status()
        # start playlist if in stop state or there is only one song in the playlist (virtually loop)
        if (status["state"] ==  "stop") or (status["playlistlength"] == "1"):
            self.do_restart_playlist()
        else:
            self.client.next()

    def do_stop(self):
        """ do nothing (on second swipe with noaudioplay) """
        self.mpd_connect_timeout()
        self.client.stop()

    def play_alsa(self,audiofile):
        """ pause mpd and play file on alsa player """
        self.mpd_connect_timeout()
        self.client.pause()
        # TODO: use the standard audio device or set them via phoniebox.conf
        subprocess.call(["aplay -q -Dsysdefault:CARD=sndrpijustboomd " + audiofile], shell=True)
        subprocess.call(["aplay -q -Dsysdefault " + audiofile], shell=True)

    def play_mpd(self,uri):
        """ play uri in mpd """
        self.mpd_connect_timeout()
        self.client.clear()
        self.client.add(uri)
        self.client.play()
        self.log("phoniebox: playing {}".format(uri.encode('utf-8')),3)


    # TODO: is there a better way to check for "value not present" than to return -1?
    def get_setting(self,section,key,opt_type="string"):
        """ get a setting from configFile file or cardAssignmentsFile
            if not present, return -1
        """
        try:
            num = str2num(section)
            parser = self.cardAssignments
        except ValueError:
            parser = self.config
        
        try:
            opt = parser.get(section,key)
        except configparser.NoOptionError:
            print("No option {} in section {}".format(key,section))
            return -1
        except configparser.NoSectionError:
            print("No section {}".format(section))
            return -1
        if "bool" in opt_type.lower():
            return str2bool(opt)
        else:
            try:
                return str2num(opt)
            except ValueError:
                return opt

    def get_cardsetting(self,cardid,key,opt_type="string"):
        """ catches Errors """
        return self.get_setting(cardid,key,opt_type)

    def mpd_init_settings(self):
        """ set initial mpd state:
            max_volume
            initial_volume """
        mpd_status = self.client.status()
        max_volume = self.get_setting("phoniebox","max_volume")
        init_volume = self.get_setting("phoniebox","init_volume")
        if max_volume == -1:
            max_volume = 100 # the absolute max_volume is 100%
        if init_volume == -1:
            init_volume = 0 # to be able to compare
        if max_volume < init_volume:
            self.log("init_volume cannot exceed max_volume.",2)
            init_volume = max_volume # do not exceed max_volume
        if mpd_status["volume"] > max_volume:
            self.client.setvol(init_volume)
            
    def set_mpd_playmode(self,cardid):
        """ set playmode in mpd according to card settings """
        playmode_defaults_map = {"repeat":0,"random":0,"single":0,"consume":0}
        set_playmode_map = { "repeat":self.client.repeat,
                             "random":self.client.random,
                             "single":self.client.single,
                             "consume":self.client.consume }
        for key in set_playmode_map.keys():
            # option is set if config file contains "option = 1" or just "option" without value.
            playmode_setting = self.get_cardsetting(cardid,key)
            if playmode_setting == -1 or playmode_setting == 1:
                playmode_setting = 1
            else:
                playmode_setting = playmode_defaults_map[key]
            # set value
            set_playmode_map[key](playmode_setting)
            self.log("setting mpd {} = {}".format(key,playmode_setting),5)

    def resume(self,cardid,action="resume"):
        """ seek to saved position if resume is activated """ 
        self.mpd_connect_timeout()
        mpd_status = self.client.status()
        print(mpd_status)
        if action in ["resume","restore"]:
            opt_resume = self.get_cardsetting(cardid,"resume")
            if opt_resume == -1 or opt_resume == 1:
                resume_elapsed = self.get_cardsetting(cardid,"resume_elapsed")
                resume_song = self.get_cardsetting(cardid,"resume_song")
                if resume_song == -1:
                    resume_song = 0
                if resume_elapsed != -1 and resume_elapsed != 0:
                    self.log("{}: resume song {} at time {}s".format(cardid,
                            self.get_cardsetting(cardid,"resume_song"),
                            self.get_cardsetting(cardid,"resume_elapsed")),5)
                    self.client.seek(resume_song,resume_elapsed)
        elif action in ["save","store"]:
            try:
                self.log("{}: save state, song {} at time {}s".format(cardid,
                            mpd_status["song"],mpd_status["elapsed"]),5)
                self.cardAssignments.set(cardid,"resume_elapsed",
                                            mpd_status["elapsed"])
                self.cardAssignments.set(cardid,"resume_song",
                                            mpd_status["song"])
            except KeyError as e:
                print("KeyError: {}".format(e))
            except ValueError as e:
                print("ValueError: {}".format(e))

    def read_cardAssignments(self):
        card_assignments_file = self.config.get("phoniebox","card_assignments_file")
        parser = ConfigParserExtended(allow_no_value=True)
        dataset = parser.read(card_assignments_file)
        if len(dataset) != 1:
            raise ValueError("Config file {} not found!".format(card_assignments_file))
        return parser

    def update_cardAssignments(self,static_cardAssignments):
        """card_assignments_file = self.config.get("phoniebox","card_assignments_file")
        parser = ConfigParserExtended(allow_no_value=True)
        dataset = parser.read(card_assignments_file)
        if len(dataset) != 1:
            raise ValueError("Config file {} not found!".format(card_assignments_file))
        # if cardAssignments is still empty, store new cardAssignments directly
        # otherwise compare new values with old values and update only certain values
        if hasattr(self, 'cardAssignments'):
            self.debug("cardAssignments already set, updating data in memory with new data from file {}".format(card_assignments_file))
            static_cardAssignments = parser"""
        self.log("Updating changes in cardAssignments from disk.",3)
        keep_cardsettings = ["resume_song","resume_elapsed"]
        common_sections = list(set(static_cardAssignments.sections()).intersection(self.cardAssignments.sections()))
        for section in common_sections:
            for option in keep_cardsettings:
                if self.cardAssignments.has_option(section,option):
                    value = self.cardAssignments.get(section,option)
                    static_cardAssignments.set(section,option,value)
                    self.log("Updating cardid {} with \"{} = {}\".".format(section,option,value),5)
        # finally assign new values
        self.cardAssignments = static_cardAssignments

 
    def read_config(self,configFilePath=defaultconfigFilePath):
        """ read config variables from file """
        configParser = ConfigParserExtended(allow_no_value=True,interpolation=configparser.BasicInterpolation()) 
        dataset = configParser.read(configFilePath)
        if len(dataset) != 1:
            raise ValueError("Config file {} not found!".format(configFilePath))
        self.config = configParser

    def translate_legacy_cardAssignments(self,last_translate_legacy_cardAssignments=0):
        """ reads the card settings data from the old scheme an translates them """
        shortcuts_path = self.get_setting("phoniebox","shortcuts_path")
        audiofolders_path = self.get_setting("phoniebox","audiofolders_path")
        if shortcuts_path != -1:
            configParser = ConfigParserExtended()
            shortcut_files = [f for f in os.listdir(shortcuts_path) if os.path.isfile(os.path.join(shortcuts_path,f)) and is_int(f)]

            # filename is the cardid
            for filename in shortcut_files:
                with open(os.path.join(shortcuts_path,filename)) as f:
                    uri = f.readline().strip().decode('utf-8')
                
                # add default settings
                if not filename in configParser.sections():
                    self.log("Adding section {} to cardAssignments".format(filename),5)
                    configParser.add_section(filename)
                configParser[filename] = self.config["default_cardsettings"]
                configParser.set(filename,"cardid",filename)
                configParser.set(filename,"uri",uri)
                # translate and add folder.conf settings if they contradict default_cardsettings
                cardsettings_map = {"CURRENTFILENAME":None,
                                    "ELAPSED":"resume_elapsed",
                                    "PLAYSTATUS":None,
                                    "RESUME":"resume",
                                    "SHUFFLE":"random",
                                    "LOOP":"repeat"}
                folderconf = os.path.join(audiofolders_path,uri,"folder.conf")
                if os.path.isfile(folderconf) and file_modified(folderconf,last_translate_legacy_cardAssignments):
                    with open(folderconf) as f:
                        lines = f.readlines()
                    cardsettings_old = dict([l.strip().replace('"','').split("=") for l in lines])
                    for key in cardsettings_old.keys():
                        if cardsettings_map[key] != None:
                        # ignore 0 and OFF values, drop settings that have None in cardsettings_map
                            if key != "ELAPSED":
                                if cardsettings_old[key] != "0" and cardsettings_old[key] != "OFF":
                                    configParser.set(filename,cardsettings_map[key],"1")
                                else:
                                    configParser.set(filename,cardsettings_map[key],"0")
                            else:
                                try:
                                    elapsed_val = float(cardsettings_old[key])
                                except ValueError:
                                    elaped_val = 0
                                configParser.set(filename,cardsettings_map[key],str(elapsed_val))
        return configParser

    def write_new_cardAssignments(self):
        """ updates the cardsettings with according to playstate """
        card_assignments_file = self.config.get("phoniebox","card_assignments_file")
        self.log("Write new card assignments to file {}.".format(card_assignments_file),3)
        with codecs.open(card_assignments_file,'w','utf-8') as f:
            self.cardAssignments.write(f)

    def print_to_file(self,filename,string):
        """ simple function to write a string to a file """
        with codecs.open(filename,'w','utf-8') as f:
            f.write(string)
        


if __name__ == "__main__":
    print("This module is not to be run! Use \"from Phoniebox import Phoniebox\" instead!")
else:
    print("Phoniebox imported. Use \"box = Phoniebox(configFile)\" to get it working.")
