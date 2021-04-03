#!/usr/bin/env python3

import sys
import os
import argparse
import readersupport as rs


if __name__ == '__main__':
    cfg_file = '../../settings/rfid_reader.ini'
    parser = argparse.ArgumentParser()
    parser.add_argument("-nw", "--nowarn",
                        help="Do not warn before overwriting old configuration",
                        action="store_true", default=False)
    parser.add_argument("-ni", "--noinstall",
                        help="Do not install dependencies (e.g. because they are already installed).",
                        action="store_true", default=False)
    parser.add_argument("-v", "--verbosity",
                        help="Increase verbosity to 'DEBUG'",
                        action="store_true", default=False)
    args = parser.parse_args()

    rs.logconsole.setLevel(rs.logging.INFO)
    if args.verbosity is True:
        print("Setting logging level to DEBUG.")
        rs.logconsole.setLevel(rs.logging.DEBUG)

    rs.write_config(cfg_file, rs.query_user_for_reader(no_dep_install=args.noinstall), nowarn=args.nowarn)
