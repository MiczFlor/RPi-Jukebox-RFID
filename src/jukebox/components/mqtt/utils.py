import time
from typing import Callable, Optional

from components.rpc_command_alias import cmd_alias_definitions

from .mqtt_const import REPEAT_MODE_OFF, REPEAT_MODE_PLAYLIST, REPEAT_MODE_SINGLE


def play_folder_recursive_args(payload: str) -> dict:
    """Create arguments for playing a folder recursively."""
    return {"folder": payload, "recursive": True}


def parse_repeat_mode(payload: str) -> Optional[str]:
    """Parse a repeat mode command based on the given payload."""
    if payload == "single":
        return "toggle_repeat_single"
    elif payload == "playlist":
        return "toggle_repeat"
    elif payload in ["disable", "off"]:
        return None
    return "toggle"


def get_args(config: dict, payload: dict) -> Optional[dict]:
    """Retrieve arguments based on the configuration and payload."""
    if "args" not in config:
        return None
    elif isinstance(config["args"], Callable):
        return config["args"](payload)
    return config["args"]


def get_rpc_command(config: dict) -> Optional[dict]:
    """Retrieve the RPC command based on the configuration."""
    rpc_key = config.get("rpc")
    if rpc_key is None:
        return None
    elif isinstance(config["rpc"], str):
        return cmd_alias_definitions[rpc_key]
    return config["rpc"]


def get_kwargs(config: dict, payload: dict) -> Optional[dict]:
    """Retrieve keyword arguments based on the configuration and payload."""
    if "kwargs" not in config:
        return None
    elif isinstance(config["kwargs"], Callable):
        return config["kwargs"](payload)
    return config["kwargs"]


def get_current_time_milli() -> int:
    """Get the current time in milliseconds."""
    return round(time.time() * 1000)


def split_topic(topic: str) -> str:
    """Split an MQTT topic and return a part of it."""
    parts = topic.split("/")
    return parts[2] if len(parts) == 3 else parts[1]


def map_repeat_mode(repeat_active: bool, single_active: bool) -> str:
    """Map boolean flags to repeat mode constants."""
    if not repeat_active:
        return REPEAT_MODE_OFF
    if single_active:
        return REPEAT_MODE_SINGLE
    return REPEAT_MODE_PLAYLIST
