import logging
import os.path

import yaml

import jukebox.plugs as plugin
import jukebox.cfghandler

logger = logging.getLogger('jb.player_content')
cfg = jukebox.cfghandler.get_handler('jukebox')


class PlayerData:

    def __init__(self):
        self.audiofile = cfg.setndefault('players', 'content', 'audiofile', value='../../shared/audiofolders/audiofiles.yaml')
        self._database = {'music': [{}],
                          'podcasts': [{}],
                          'livestreams': [{}]}
        self._fill_database(self.audiofile)

    def _fill_database(self, yaml_file):
        with open(yaml_file, 'r') as stream:
            try:
                self._database = yaml.safe_load(stream)
                logger.debug("audiofiles database read")
            except yaml.YAMLError as err:
                logger.error(f"Error occured while reading {yaml_file}: {err}")

    @plugin.tag
    def read_player_content(self, content_type):
        return self._database.get(content_type, "empty")

    @plugin.tag
    def get_location(self, titlename):
        for key, value in self._database.items():
            for elem in value:
                return f"mpd:{key}:{elem['location']}" if elem['name'] == titlename else None

    @plugin.tag
    def list_content(self):
        return self._database
