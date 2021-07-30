#!/usr/bin/env python3
"""
Top-level entry point for the JukeBox Core demon

"""
import os.path
import argparse
import logging
import logging.config
import jukebox.daemon
import misc.loggingext


def main():
    # Get absolute path of this script
    script_path = os.path.abspath(os.path.dirname(os.path.realpath(__file__)))
    working_path = os.path.abspath(os.getcwd())
    default_cfg_jukebox = os.path.abspath(os.path.join(script_path, '../../shared/settings/jukebox.yaml'))
    default_cfg_logger = os.path.abspath(os.path.join(script_path, '../../shared/settings/logger.yaml'))

    argparser = argparse.ArgumentParser(description='The JukeboxDaemon')
    argparser.add_argument('-conf', '-c', type=argparse.FileType('r'), default=default_cfg_jukebox,
                           help=f"jukebox configuration file [default: '{default_cfg_jukebox}'",
                           metavar="FILE")
    verbose_group = argparser.add_mutually_exclusive_group()
    verbose_group.add_argument("-l", "--logger",
                               help=f"logger configuration file [default: '{default_cfg_logger}']",
                               metavar="FILE", default=default_cfg_logger)
    verbose_group.add_argument('-v', '--verbose', action='count', default=None,
                               help="increase logger verbosity level from warning to info (-v) to debug (-vv) "
                                    "to see all plugin calls and not only errors (-vvv)")
    verbose_group.add_argument('-q', '--quiet', action='count', default=None,
                               help="decrease logger verbosity level from warning to error (-q) to critical (-qq)")
    args = argparser.parse_args()

    if args.verbose is not None:
        logger = misc.loggingext.configure_default({1: logging.INFO, 2: logging.DEBUG}[min(args.verbose, 2)])
        if args.verbose < 3:
            misc.loggingext.configure_default(logging.ERROR, name='jb.plugin.call')
    elif args.quiet is not None:
        logger = misc.loggingext.configure_default({1: logging.ERROR, 2: logging.CRITICAL}[min(args.quiet, 2)])
    else:
        logger = misc.loggingext.configure_from_file(args.logger)

    logger.info("Starting Jukebox Daemon")
    if working_path != script_path:
        logger.warning("It is working_path != script_path."
                       "If you have relative filenames in your config, they may not be found!")
        logger.warning(f"working_path: '{working_path}'")
        logger.warning(f"script_path : '{script_path}'")
    myjukebox = jukebox.daemon.JukeBox(args.conf.name)
    myjukebox.run()


if __name__ == "__main__":
    main()
