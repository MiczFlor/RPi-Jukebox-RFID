class BackendPlayer:
    """
    Class to inherit, so that you can build a proper new Player
    """
    def __init__(self):
        raise NotImplementedError

    def next(self):
        raise NotImplementedError

    def prev(self):
        raise NotImplementedError

    def play(self, idx=None):
        raise NotImplementedError

    def toggle(self):
        raise NotImplementedError

    def pause(self):
        raise NotImplementedError

    def stop(self):
        raise NotImplementedError

    def get_queue(self):
        raise NotImplementedError

    def play_uri(self, uri):
        raise NotImplementedError

    def repeatmode(self):
        raise NotImplementedError

    def seek(self):
        raise NotImplementedError
