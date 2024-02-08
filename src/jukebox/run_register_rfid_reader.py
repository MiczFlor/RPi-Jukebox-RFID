#!/usr/bin/env python
"""
Setup tool to configure the RFID Readers.

Run this once to register and configure the RFID readers with the Jukebox. Can be re-run at any time to change
the settings. For more information see [RFID Readers](../rfid/README.md).

> [!NOTE]
> This tool will always write a new configurations file. Thus, overwrite the old one (after checking with the user).
> Any manual modifications to the settings will have to be re-applied

"""
import os
import logging
import argparse

import misc.inputminus as pyil
import components.rfid.configure as rfid_configure
import jukebox.plugs
jukebox.plugs.ALLOW_DIRECT_IMPORTS = True
import components.hostif.linux as host  # noqa: E402

# Create logger
logger = logging.getLogger()
logger.setLevel(logging.DEBUG)
# Create console handler and set default level
logconsole = logging.StreamHandler()
logconsole.setFormatter(logging.Formatter('%(asctime)s - %(name)s - %(levelname)-8s: %(message)s',
                                          datefmt='%d.%m.%Y %H:%M:%S'))
logconsole.setLevel(logging.INFO)
logger.addHandler(logconsole)


def main():
    # The default config file relative to this files location and independent of working directory
    script_path = os.path.abspath(os.path.dirname(os.path.realpath(__file__)))
    cfg_file_default = os.path.abspath(os.path.join(script_path, '../../shared/settings/rfid.yaml'))

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
    parser.add_argument("-v", "--verbosity",
                        help="Increase verbosity to 'DEBUG'",
                        action="store_true", default=False)
    args = parser.parse_args()

    if args.verbosity is True:
        print("Setting logging level to DEBUG.")
        logconsole.setLevel(logging.DEBUG)

    if host.is_any_jukebox_service_active():
        pyil.msg_highlight('Jukebox service is running!')
        print("\nPlease stop jukebox-daemon service and restart tool")
        print("$ systemctl --user stop jukebox-daemon\n\n")
        print("Don't forget to start the service again :-)")
        return

    dinstall_lookup = {'a': 'auto', 'q': 'query', 'n': 'no', 'auto': 'auto', 'query': 'query', 'no': 'no'}
    rfid_configure.write_config(args.conffile,
                                rfid_configure.query_user_for_reader(dependency_install=dinstall_lookup[args.deps]),
                                force_overwrite=args.force)


if __name__ == '__main__':
    main()
