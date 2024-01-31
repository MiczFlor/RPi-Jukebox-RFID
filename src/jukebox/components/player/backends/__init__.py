from abc import ABC, abstractmethod


class BackendPlayer(ABC):
    """
    Abstract Class to inherit, so that you can build a proper new Player
    """

    @abstractmethod
    def next(self):
        pass

    @abstractmethod
    def prev(self):
        pass

    @abstractmethod
    def play(self):
        pass

    @abstractmethod
    def play_single(self, uri):
        pass

    @abstractmethod
    def play_album(self, albumartist, album):
        pass

    @abstractmethod
    def play_folder(self, folder: str, recursive: bool):
        """
        Playback a music folder.

        :param folder: Folder path relative to music library path
        :param recursive: Add folder recursively
        """
        pass

    @abstractmethod
    def toggle(self):
        pass

    @abstractmethod
    def shuffle(self):
        pass

    @abstractmethod
    def pause(self):
        pass

    @abstractmethod
    def stop(self):
        pass

    @abstractmethod
    def get_queue(self):
        pass

    @abstractmethod
    def repeat(self):
        pass

    @abstractmethod
    def seek(self):
        pass

    @abstractmethod
    def get_albums(self):
        pass

    @abstractmethod
    def get_single_coverart(self, song_url):
        pass

    @abstractmethod
    def get_album_coverart(self):
        pass

    @abstractmethod
    def list_dirs(self):
        pass

    @abstractmethod
    def get_song_by_url(self, song_url):
        pass

    @abstractmethod
    def get_folder_content(self, folder):
        """
        Get the folder content as content list with meta-information. Depth is always 1.

        Call repeatedly to descend in hierarchy

        :param folder: Folder path relative to music library path
        """
        pass
