def play_folder_recursive_args(payload: str):
    return {"folder": payload, "recursive": True}


def parse_repeat_mode(payload: str):
    if payload == "single":
        return "toggle_repeat_single"
    elif payload == "playlist":
        return "toggle_repeat"
    elif payload == "disable" or payload == "off":
        return None
    return "toggle"
