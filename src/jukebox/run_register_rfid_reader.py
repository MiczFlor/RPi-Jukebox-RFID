#!/usr/bin/env python3

import os
import logging
import argparse
import subprocess

import components.rfid.configure as rfid_configure

# Create logger
logger = logging.getLogger()
logger.setLevel(logging.DEBUG)
# Create console handler and set default level
logconsole = logging.StreamHandler()
logconsole.setFormatter(logging.Formatter('%(asctime)s - %(name)s - %(levelname)-8s: %(message)s',
                                          datefmt='%d.%m.%Y %H:%M:%S'))
logconsole.setLevel(logging.INFO)
logger.addHandler(logconsole)


if __name__ == '__main__':
    # The default config file relative to this files location and independent of working directory
    cfg_file_default = os.path.abspath(os.path.dirname(os.path.realpath(__file__)) + '/../../shared/settings/rfid.yaml')
    service_name = "jukebox-daemon.service"

    parser = argparse.ArgumentParser()
    parser.add_argument("-f", "--force",
                        help="Force overwriting of existing configuration",
                        action="store_true", default=False)
    parser.add_argument("-d", "--deps",
                        help="Install dependencies: (a)uto, (n)o, (q)uery [default]",
                        metavar="CHAR", choices=['a', 'q', 'n', 'auto', 'query', 'no'], default='q')
    parser.add_argument("-c", "--conffile",
                        help=f"Output configuration file [default: '{cfg_file_default}']",
                        metavar="FILE", default=cfg_file_default)
    parser.add_argument("-sr", "--service_restart",
                        help="Restart the jukebox daemon reader service after configuration update",
                        action="store_true", default=False)
    parser.add_argument("-v", "--verbosity",
                        help="Increase verbosity to 'DEBUG'",
                        action="store_true", default=False)
    args = parser.parse_args()

    if args.verbosity is True:
        print("Setting logging level to DEBUG.")
        logconsole.setLevel(logging.DEBUG)

    dinstall_lookup = {'a': 'auto', 'q': 'query', 'n': 'no', 'auto': 'auto', 'query': 'query', 'no': 'no'}
    rfid_configure.write_config(args.conffile,
                                rfid_configure.query_user_for_reader(dependency_install=dinstall_lookup[args.deps]),
                                force_overwrite=args.force)

    if args.service_restart:
        print(f"Restarting {service_name} ...")
        subprocess.run(f"sudo systemctl restart {service_name}",
                       shell=True, check=False)
