import sys, os.path
import argparse
import jukebox.daemon


if __name__ == "__main__":

    print ("hallo")

    # get absolute path of this script
    dir_path = os.path.dirname(os.path.realpath(__file__))
    defaultconfigFilePath = os.path.join(dir_path, '../../settings/phoniebox.conf')

    argparser = argparse.ArgumentParser(description='The JukeboxDaemon')
    argparser.add_argument('configuration_file', type=argparse.FileType('r'),nargs='?',default=defaultconfigFilePath)
    ##help=f"Reader configuration file [default: '{default_reader_cfg_file}']",
    argparser.add_argument('--verbose', '-v', action='count', default=0)

    args = argparser.parse_args()

    jukebox.daemon.jukebox_daemon(args.configuration_file.name)
