import logging
from jukebox import publishing

logger = logging.getLogger('jb.player')


class PlayerStatus:
    STATUS = {
        'album': '',
        'albumartist': '',
        'artist': '',
        'coverArt': '',
        'duration': 0,
        'elapsed': 0,
        'file': '',  # required for MPD // check if really is required
        'player': '',
        'playing': False,
        'shuffle': False,
        'repeat': 0,
        'title': '',
        'trackid': '',
    }

    def __init__(self):
        self._player_status = self.STATUS

    def update(self, **kwargs):
        for key, value in kwargs.items():
            if key in self.STATUS:
                self._player_status[key] = value

        self.publish()

    def publish(self):
        logger.debug(f'Published: {self._player_status}')
        return publishing.get_publisher().send(
            'player_status',
            self._player_status
        )
