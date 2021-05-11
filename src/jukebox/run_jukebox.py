import os.path
import argparse
import jukebox.daemon


if __name__ == "__main__":

    # get absolute path of this script
    dir_path = os.path.dirname(os.path.realpath(__file__))
    defaultconfigFilePath = os.path.join(dir_path, '../../settings/jukebox.conf')

    argparser = argparse.ArgumentParser(description='The JukeboxDaemon')
    argparser.add_argument('configuration_file', type=argparse.FileType('r'), nargs='?', default=defaultconfigFilePath)
    argparser.add_argument('--verbose', '-v', action='count', default=0)

    args = argparser.parse_args()

    jukebox = jukebox.daemon.JukeBox(args.configuration_file.name, args.verbose)
    jukebox.run()
