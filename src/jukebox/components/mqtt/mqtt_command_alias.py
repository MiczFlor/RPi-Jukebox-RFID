"""
This file provides definitions for MQTT to RPC command aliases

See [RPC Commands](../../builders/rpc-commands.md)
"""

import json

import jukebox.plugs as plugs

from .mqtt_const import Mqtt_Commands
from .utils import parse_repeat_mode, play_folder_recursive_args


def get_mute(payload) -> bool:
    """Helper to toggle mute in legacy support."""
    is_mute = plugs.call_ignore_errors(
        package="volume", plugin="ctrl", method="get_mute"
    )
    return not is_mute


legacy_mqtt_cmd = {
    "volumeup": {"rpc": "change_volume", "args": 1},
    "volumedown": {"rpc": "change_volume", "args": -1},
    "mute": {
        "rpc": {
            "package": "volume",
            "plugin": "ctrl",
            "method": "mute",
        },
        "args": get_mute,
    },
    "playerplay": {"rpc": "play"},
    "playerpause": {"rpc": "pause"},
    "playernext": {"rpc": "next_song"},
    "playerprev": {"rpc": "prev_song"},
    "playerstop": {
        "rpc": {
            "package": "player",
            "plugin": "ctrl",
            "method": "stop",
        }
    },
    "playerrewind": {
        "rpc": {
            "package": "player",
            "plugin": "ctrl",
            "method": "rewind",
        }
    },
    "playershuffle": {"rpc": "shuffle"},
    "playerreplay": {
        "rpc": {
            "package": "player",
            "plugin": "ctrl",
            "method": "replay",
        }
    },
    "setvolume": {
        "rpc": "set_volume",
        "args": int,
    },
    "setmaxvolume": {
        "rpc": "set_soft_max_volume",
        "args": int,
    },
    "shutdownafter": {
        "rpc": "timer_shutdown",
        "args": int,
    },
    "playerstopafter": {
        "rpc": "timer_stop_player",
        "args": int,
    },
    "playerrepeat": {
        "rpc": "repeat",
        "args": parse_repeat_mode,
    },
    "playfolder": {
        "rpc": "play_folder",
        "args": str,
    },
    "playfolderrecursive": {
        "rpc": "play_folder",
        "kwargs": play_folder_recursive_args,  # kwargs: folder, recursive
    },
    # "scan": {},
    # "shutdownsilent": {},
    # "disablewifi": {},
    # "setidletime": {},
    # "playerseek": {},
    # "setvolstep": {},
    # "rfid": {},
    # "gpio": {},
    # "swipecard": {},
}


_player_cmds = {
    Mqtt_Commands.PLAY.value: {"rpc": "play"},
    Mqtt_Commands.PLAY_FOLDER.value: {
        "rpc": "play_folder",
        "kwargs": json.loads,  # kwargs: folder, recursive
    },
    Mqtt_Commands.PLAY_ALBUM.value: {
        "rpc": "play_album",
        "kwargs": json.loads,  # kwargs: albumartist, album
    },
    Mqtt_Commands.PLAY_CARD.value: {
        "rpc": "play_card",
        "kwargs": json.loads,  # kwargs: folder, recursive
    },
    Mqtt_Commands.PLAY_SINGLE.value: {
        "rpc": "play_single",
        "kwargs": json.loads,  # kwargs: song_url
    },
    Mqtt_Commands.PAUSE.value: {"rpc": "pause"},
    Mqtt_Commands.NEXT_SONG.value: {"rpc": "next_song"},
    Mqtt_Commands.PREV_SONG.value: {"rpc": "prev_song"},
    Mqtt_Commands.STOP.value: {
        "rpc": {
            "package": "player",
            "plugin": "ctrl",
            "method": "stop",
        }
    },
    Mqtt_Commands.REWIND.value: {
        "rpc": {
            "package": "player",
            "plugin": "ctrl",
            "method": "rewind",
        }
    },
    Mqtt_Commands.SHUFFLE.value: {"rpc": "shuffle"},
    Mqtt_Commands.REPLAY.value: {
        "rpc": {
            "package": "player",
            "plugin": "ctrl",
            "method": "replay",
        }
    },
    Mqtt_Commands.REPEAT.value: {
        "rpc": "repeat",
        "kwargs": json.loads,  # kwargs: option
    },
}

_volume_cmds = {
    Mqtt_Commands.CHANGE_VOLUME.value: {
        "rpc": "change_volume",
        "kwargs": json.loads,  # kwargs: step
    },
    Mqtt_Commands.SET_VOLUME.value: {
        "rpc": "set_volume",
        "kwargs": json.loads,  # kwargs: volume
    },
    Mqtt_Commands.VOLUME_MUTE.value: {
        "rpc": {
            "package": "volume",
            "plugin": "ctrl",
            "method": "mute",
        },
        "kwargs": json.loads,  # kwargs: mute
    },
    Mqtt_Commands.SET_SOFT_MAX_VOLUME.value: {
        "rpc": "set_soft_max_volume",
        "kwargs": json.loads,  # kwargs: max_volume
    },
}

_system_cmd = {
    Mqtt_Commands.SAY_MY_IP.value: {
        "rpc": "say_my_ip",
        "kwargs": json.loads,  # kwargs: option
    },
    Mqtt_Commands.SHUTDOWN.value: {"rpc": "shutdown"},
    Mqtt_Commands.REBOOT.value: {"rpc": "reboot"},
    Mqtt_Commands.TIMER_SHUTDOWN.value: {
        "rpc": "timer_shutdown",
        "kwargs": json.loads,  # kwargs: value
    },
    Mqtt_Commands.TIMER_STOP_PLAYER.value: {
        "rpc": "timer_stop_player",
        "kwargs": json.loads,  # kwargs: value
    },
    Mqtt_Commands.TIMER_FADE_VOLUME.value: {
        "rpc": "timer_fade_volume",
        "kwargs": json.loads,  # kwargs: value
    },
}

mqtt_cmd = {
    **_volume_cmds,
    **_system_cmd,
    **_player_cmds,
}
