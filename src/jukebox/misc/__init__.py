import os
from typing import (Any)


def recursive_chmod(path, mode_files, mode_dirs):
    """Recursively change folder and file permissions

    mode_files/mode dirs can be given in octal notation e.g. 0o777
    flags from the stats module.

    Reference: https://docs.python.org/3/library/os.html#os.chmod"""
    # os.walk will loop through all dirs in dirpath (including top-level dir)
    # filenames are just that: list of filenames for each dir
    for dirpath, _, filenames in os.walk(path):
        os.chmod(dirpath, mode_dirs)
        for filename in filenames:
            os.chmod(os.path.join(dirpath, filename), mode_files)


def flatten(iterable):
    """Flatten all levels of hierarchy in nested iterables"""
    res = []
    try:
        iterator = iter(iterable)
    except TypeError:
        res.append(iterable)
    else:
        for it in iterator:
            res = [*res, *flatten(it)]
    return res


def getattr_hierarchical(obj: Any, name: str) -> Any:
    """Like the builtin getattr, but descends though the hierarchy levels"""
    for sub_name in name.split("."):
        obj = getattr(obj, sub_name)
    return obj
