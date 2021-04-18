#!/usr/bin/env python3
"""
This script kicks off the daemon rfid reader
"""
import os
import argparse
import logging

from base import readerdaemon


if __name__ == '__main__':
    # Parse the arguments and get the script started :-)

    # Get absolute path of this script
    script_path = os.path.abspath(os.path.dirname(os.path.realpath(__file__)))
    # The default config file relative to this files location and independent of working directory
    default_reader_cfg_file = os.path.abspath(script_path + '/../../settings') + '/rfid_reader.ini'

    parser = argparse.ArgumentParser()
    parser.add_argument("-v", "--verbosity",
                        help="Increase verbosity to 'DEBUG'",
                        action="store_const", const=logging.DEBUG, default=None)
    parser.add_argument("-c", "--conffile",
                        help=f"Reader configuration file [default: '{default_reader_cfg_file}']",
                        metavar="FILE", default=default_reader_cfg_file)
    args = parser.parse_args()

    readerdaemon.create_read_card_workers(args.conffile, args.verbosity)
