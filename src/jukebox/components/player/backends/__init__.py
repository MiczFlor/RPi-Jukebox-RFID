import jukebox.plugs as plugin


class BackendPlayer:
    """
    Class to inherit, so that you can build a proper new Player
    """
    def __init__(self):
        raise NotImplementedError

    @plugin.tag
    def next(self):
        raise NotImplementedError

    @plugin.tag
    def prev(self):
        raise NotImplementedError

    @plugin.tag
    def play(self, idx=None):
        raise NotImplementedError

    @plugin.tag
    def toggle(self):
        raise NotImplementedError

    @plugin.tag
    def pause(self):
        raise NotImplementedError

    @plugin.tag
    def stop(self):
        raise NotImplementedError

    @plugin.tag
    def get_queue(self):
        raise NotImplementedError

    @plugin.tag
    def play_uri(self, uri):
        raise NotImplementedError

    @plugin.tag
    def repeatmode(self):
        raise NotImplementedError

    @plugin.tag
    def seek(self):
        raise NotImplementedError

    @plugin.tag
    def get_albums(self):
        raise NotImplementedError
