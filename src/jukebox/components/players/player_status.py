import logging
import jukebox.cfghandler
from jukebox import publishing

logger = logging.getLogger('jb.players.player_status')
cfg = jukebox.cfghandler.get_handler('jukebox')

class PlayerStatus:
    ATTRS = [
        'player',
        'playing', # bool
        'shuffle',
        'repeat',
        'trackid', # was `songid` before
        'title',
        'artist',
        'albumartist',
        'album',
        'timeTotal', # was `elapsed` before
        'timeElapsed', # was `duration` before
        'file', # required for MPD // check if really is required
    ]

    def __init__(self):
        self._player_status = dict.fromkeys(self.ATTRS)


    def update(self, **kwargs):
        for key, value in kwargs.items():
            if key in self.ATTRS:
                self._player_status[key] = value

        self.publish()


    def publish(self):
        logger.debug(f'Published: {self._player_status}')
        return publishing.get_publisher().send(
            'player_status',
            self._player_status
        )
