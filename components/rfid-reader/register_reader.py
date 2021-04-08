#!/usr/bin/env python3

import os
import argparse
import subprocess

import readersupport as rs


if __name__ == '__main__':
    # The default config file relative to this files location and independent of working directory
    cfg_file_default = os.path.abspath(os.path.dirname(os.path.realpath(__file__)) + '/../../settings/rfid_reader.ini')
    service_name = "phoniebox-rfid-reader.service"

    parser = argparse.ArgumentParser()
    parser.add_argument("-f", "--force",
                        help="Force overwriting of existing configuration",
                        action="store_true", default=False)
    parser.add_argument("-d", "--deps",
                        help="Install dependencies: (a)uto, (n)o, (q)uery [default]",
                        metavar="CHAR", choices=['a', 'q', 'n', 'auto', 'query', 'no'], default='q')
    parser.add_argument("-o", "--outfile",
                        help=f"Output configuration file [default: '{cfg_file_default}']",
                        metavar="FILE", default=cfg_file_default)
    parser.add_argument("-se", "--service_enable",
                        help="Enable the rfid reader service during boot-up",
                        action="store_true", default=False)
    parser.add_argument("-sr", "--service_restart",
                        help="Restart the rfid reader service after configuration update",
                        action="store_true", default=False)
    parser.add_argument("-v", "--verbosity",
                        help="Increase verbosity to 'DEBUG'",
                        action="store_true", default=False)
    args = parser.parse_args()

    rs.logconsole.setLevel(rs.logging.INFO)
    if args.verbosity is True:
        print("Setting logging level to DEBUG.")
        rs.logconsole.setLevel(rs.logging.DEBUG)

    dinstall_lookup = {'a': 'auto', 'q': 'query', 'n': 'no', 'auto': 'auto', 'query': 'query', 'no': 'no'}
    rs.write_config(args.outfile,
                    rs.query_user_for_reader(dependency_install=dinstall_lookup[args.deps]),
                    force_overwrite=args.force)

    if args.service_enable:
        print(f"Enabling {service_name} ...")
        subprocess.run(f"sudo systemctl enable {service_name}",
                       shell=True, check=False)
    if args.service_restart:
        print(f"Restarting {service_name} ...")
        subprocess.run(f"sudo systemctl restart {service_name}",
                       shell=True, check=False)
