from enum import Enum


class Mqtt_Attributes(Enum):
    STATE = "attribute/state"
    TITLE = "attribute/title"
    ARTIST = "attribute/artist"
    ELAPSED = "attribute/elapsed"
    DURATION = "attribute/duration"
    TRACK = "attribute/track"
    FILE = "attribute/file"
    RANDOM = "attribute/random"
    REPEAT = "attribute/repeat"
    REPEAT_MODE = "attribute/repeat_mode"
    VOLUME = "attribute/volume"
    MUTE = "attribute/mute"


class Mqtt_Commands(Enum):
    PLAY = "play"
    PLAY_FOLDER = "play_folder"
    PLAY_ALBUM = "play_album"
    PLAY_CARD = "play_card"
    PLAY_SINGLE = "play_single"
    PAUSE = "pause"
    NEXT_SONG = "next_song"
    PREV_SONG = "prev_song"
    STOP = "stop"
    REWIND = "rewind"
    SHUFFLE = "shuffle"
    REPLAY = "replay"
    REPEAT = "repeat"
    CHANGE_VOLUME = "change_volume"
    SET_VOLUME = "set_volume"
    VOLUME_MUTE = "volume_mute"
    SET_SOFT_MAX_VOLUME = "set_soft_max_volume"
    SAY_MY_IP = "say_my_ip"
    SHUTDOWN = "shutdown"
    REBOOT = "reboot"
    TIMER_SHUTDOWN = "timer_shutdown"
    TIMER_STOP_PLAYER = "timer_stop_player"
    TIMER_FADE_VOLUME = "timer_fade_volume"


# List of topics to send
topics_to_send = ["volume.level", "playerstatus"]

# Constants for repeat modes
REPEAT_MODE_OFF = "off"
REPEAT_MODE_SINGLE = "single"
REPEAT_MODE_PLAYLIST = "playlist"
