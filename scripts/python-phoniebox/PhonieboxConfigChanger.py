#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# import json
import os, sys, signal
# from mpd import MPDClient
import configparser
# from RawConfigParserExtended import RawConfigParserExtended
from Phoniebox import Phoniebox

# get absolute path of this script
dir_path = os.path.dirname(os.path.realpath(__file__))
defaultconfigFilePath = os.path.join(dir_path, './phoniebox.conf')


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


class PhonieboxConfigChanger(Phoniebox):

    def __init__(self, configFilePath=defaultconfigFilePath):
        Phoniebox.__init__(self, configFilePath)

    def assigncard(self, cardid, uri):
        section = cardid
        # set uri and cardid for card (section = cardid)
        if not section in self.cardAssignments.sections():
            self.cardAssignments.add_section(section)
        self.cardAssignments.set(section, "cardid", cardid)
        self.cardAssignments.set(section, "uri", uri)
        # write updated assignments to file
        with open(self.config['card_assignments_file'], 'w') as cardAssignmentsFile:
            self.cardAssignments.write(cardAssignmentsFile)

    def removecard(self, cardid):
        section = cardid
        if section in self.cardAssignments.sections():
            self.cardAssignments.remove_section(section)
        # write updated assignments to file
        with open(self.config['card_assignments_file'], 'w') as f:
            self.cardAssignments.write(f)

    def set(self, section, key, value):
        try:
            num = int(section)
            parser = self.cardAssignments
            config_file = self.config.get("phoniebox", "card_assignments_file")
        except ValueError:
            parser = self.config
            config_file = self.configFilePath
        # update value
        try:
            parser.set(section, key, value)
            self.debug("Set {} = {} in section {}".format(key, value, section))
        except configparser.NoSectionError as e:
            raise(configparser.NoSectionError, e)
        # write to file
        # with open(config_file, 'w') as f:
        #     parser.write(f)

    def get(self, section, t="ini"):
        try:
            num = int(section)
            parser = self.cardAssignments
        except ValueError:
            parser = self.config

        if t == "json":
            print(parser.as_json(section))
        elif t == "dict":
            print(parser.as_dict(section))
        else:
            print(parser.print_ini(section))

    def print_usage(self):
        print("Usage: {} set ".format(sys.argv[0]))


def main(self):

    cmdlist = ["assigncard", "removecard", "set", "get"]

    if len(sys.argv) < 1:
        sys.exit()
    else:
        if sys.argv[1] in cmdlist:
            configFilePath = defaultconfigFilePath
            cmd = sys.argv[1]
            shift = 0
        else:
            configFilePath = sys.argv[1]
            cmd = sys.argv[2]
            shift = 1

        ConfigChanger = PhonieboxConfigChanger(configFilePath)
        try:
            if cmd == "assigncard":
                cardid = sys.argv[2+shift]
                uri = sys.argv[3+shift]
                ConfigChanger.assigncard(cardid, uri)
            elif cmd == "removecard":
                cardid = sys.argv[2+shift]
                ConfigChanger.removecard(cardid)
            elif cmd == "set":
                section = sys.argv[2+shift]
                key = sys.argv[3+shift]
                value = sys.argv[4+shift]
                ConfigChanger.set(section, key, value)
            elif cmd == "get":
                section = sys.argv[2+shift]
                try:
                    t = sys.argv[3+shift]
                except:
                    t = "ini"
                ConfigChanger.get(section, t)
            else:
                # will never be reached
                print("supported commands are {} and {}".format(", ".join(cmdlist[:-1]), cmdlist[-1]))
        except:
            self.print_usage()


if __name__ == "__main__":
    main()
