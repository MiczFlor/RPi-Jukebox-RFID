#!/usr/bin/env python
"""
This is the main app and starts the Jukebox Core.

Usually this runs as a service, which is started automatically after boot-up. At times, it may be necessary to restart
the service.
For example after a configuration change. Not all configuration changes can be applied on-the-fly.
See [Jukebox Configuration](../../builders/configuration.md#jukebox-configuration).

For debugging, it is usually desirable to run the Jukebox directly from the console rather than
as service. This gives direct logging info in the console and allows changing command line parameters.
See [Troubleshooting](../../builders/troubleshooting.md).
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
    argparser.add_argument('-c', '--conf', type=argparse.FileType('r'), default=default_cfg_jukebox,
                           help=f"jukebox configuration file [default: '{default_cfg_jukebox}'",
                           metavar="FILE")
    argparser.add_argument('-a', '--artifacts', action="store_true",
                           help="Write out all artifacts and auto-generated help files")
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
        logger = misc.loggingext.configure_default({1: logging.INFO, 2: logging.DEBUG}[min(args.verbose, 2)],
                                                   with_publisher=True)
        if args.verbose < 3:
            misc.loggingext.configure_default(logging.ERROR, name='jb.plugin.call', with_publisher=True)
    elif args.quiet is not None:
        logger = misc.loggingext.configure_default({1: logging.ERROR, 2: logging.CRITICAL}[min(args.quiet, 2)],
                                                   with_publisher=True)
    else:
        logger = misc.loggingext.configure_from_file(args.logger)

    if working_path != script_path:
        logger.warning("It is working_path != script_path."
                       "If you have relative filenames in your config, they may not be found!")
        logger.warning(f"working_path: '{working_path}'")
        logger.warning(f"script_path : '{script_path}'")
    myjukebox = jukebox.daemon.get_jukebox_daemon(args.conf.name, args.artifacts)
    myjukebox.run()


if __name__ == "__main__":
    main()
