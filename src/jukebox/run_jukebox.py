#!/usr/bin/env python3
"""
Top-level entry point for the JukeBox Core demon

##############
Configuration
##############
TBD

##############
Logger
##############
We use a hierarchical Logger structure based on pythons logging module. It can be finely configured with a yaml file.

The top-level logger is called 'jb' (to make it short). In any module you may simple create a child-logger at any hierarchy
level below 'jb'. It will inherit settings from it's parent logger unless otherwise configured in the yaml file.
Hierarchy separator is the '.'. If the logger already exits, getLogger will return a reference to the same, else it will be
created on the spot.

:Example::
    >>> import logging
    >>> logger = logging.getLogger('jb.awesome_module')
    >>> logger.info('Started general awesomeness aura')

Example: YAML snippet, setting WARNING as default level everywhere and DEBUG for jb.awesome_module::
``
loggers:
  jb:
    level: WARNING
    handlers: [console, debug_file_handler, error_file_handler]
    propagate: no
  jb.awesome_module:
    level: DEBUG
``

.. note::
The name (and hierarchy path) of the logger can be arbitrary and must not necessarily match the module name (still makes sense)
There can be multiple loggers per module, e.g. for special classes, to further control the amount of log output
"""

import os.path
import sys
import argparse
import logging
import logging.config
from ruamel.yaml import YAML
import jukebox.daemon
import misc.loggingext


def logger_default(level=logging.DEBUG):
    logger = logging.getLogger('jb')
    logger.setLevel(level)
    console = logging.StreamHandler(sys.stdout)
    console.setLevel(level)
    formatter = logging.Formatter(
        fmt='{asctime} - {lineno:4}:{filename:20} - {name} - {threadName:10} - {levelnameColored:8} - '
            '{lightcyan}{message}{reset}',
        datefmt='%d.%m.%Y %H:%M:%S',
        style='{')
    console.addFilter(misc.loggingext.ColorFilter())
    console.setFormatter(formatter)
    logger.addHandler(console)
    logger.info(f"Enabling default logger with level = {level}")
    return logger


def logger_configure(filename=None):
    if filename is None:
        return logger_default()
    yaml = YAML(typ='safe')
    try:
        with open(filename) as stream:
            cfg = yaml.load(stream)
        logging.config.dictConfig(cfg)
        logger = logging.getLogger('jb')
    except Exception as e:
        logger = logger_default()
        logger.error(f"Using default fallback logger. Reason: while opening '{filename}' for logger configuration")
        logger.error(f"{e}")
    # This enforces a fresh file for all RotatingFileHandlers at start of application
    for h in logger.handlers:
        if type(h) == logging.handlers.RotatingFileHandler:
            h.doRollover()
    return logger


def main():
    # Get absolute path of this script
    script_path = os.path.abspath(os.path.dirname(os.path.realpath(__file__)))
    default_cfg_jukebox = os.path.abspath(os.path.join(script_path, '../../settings/jukebox.conf'))
    default_cfg_logger = os.path.abspath(os.path.join(script_path, '../../settings/logger.yaml'))

    argparser = argparse.ArgumentParser(description='The JukeboxDaemon')
    argparser.add_argument('-conf', '-c', type=argparse.FileType('r'), default=default_cfg_jukebox,
                           help=f"jukebox configuration file [default: '{default_cfg_jukebox}'",
                           metavar="FILE")
    verbose_group = argparser.add_mutually_exclusive_group()
    verbose_group.add_argument("-l", "--logger",
                               help=f"logger configuration file [default: '{default_cfg_logger}']",
                               metavar="FILE", default=default_cfg_logger)
    verbose_group.add_argument('-v', '--verbose', action='count', default=None,
                               help="increase logger verbosity level from warning to info (-v) to debug (-vv)")
    verbose_group.add_argument('-q', '--quiet', action='count', default=None,
                               help="decrease logger verbosity level from warning to error (-q) to critical (-qq)")
    args = argparser.parse_args()

    if args.verbose is not None:
        logger = logger_default({1: logging.INFO, 2: logging.DEBUG}[min(args.verbose, 2)])
    elif args.quiet is not None:
        logger = logger_default({1: logging.ERROR, 2: logging.CRITICAL}[min(args.quiet, 2)])
    else:
        logger = logger_configure(args.logger)

    jukebox.daemon.jukebox_daemon(args.conf.name)


if __name__ == "__main__":
    main()
