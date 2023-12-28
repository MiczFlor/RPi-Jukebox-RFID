"""
This module handles global and local configuration data

The concept is that config handler is created and initialized once in the main thread::

    cfg = get_handler('global')
    load_yaml(cfg, 'filename.yaml')

In all other modules (in potentially different threads) the same handler is obtained and used by::

    cfg = get_handler('global')

This eliminates the need to pass an effectively global configuration handler by parameters across the entire design.
Handlers are identified by their name (in the above example *global*)

The function :func:`get_handler` is the main entry point to obtain a new or existing handler.
"""
import copy
import sys
import threading
import logging
from ruamel.yaml import YAML
import hashlib
from typing import (Dict, Optional, Any)

logger = logging.getLogger('jb.cfghandler')

# ---------------------------------------------------------------------------
# Global thread-related stuff
# ---------------------------------------------------------------------------
# _lock_module is used to serialize access to shared data structures in this module
# (currently only during creation of a new config_handler)
# Each config handler has its own lock for protecting access to the underlying shared data
# this cannot be acquired automatically, as the shared data is typically a mutable. It is in the users
# responsibility to do that. See documentation below for more info

_lock_module = threading.RLock()


def _acquire_lock() -> None:
    """
    Acquire the module-level lock for serializing access to shared data.

    This should be released with _releaseLock().
    """
    if _lock_module:
        _lock_module.acquire()


def _release_lock() -> None:
    """
    Release the module-level lock acquired by calling _acquireLock().
    """
    if _lock_module:
        _lock_module.release()


class ConfigHandler:
    """
    The configuration handler class

    Don't instantiate directly. Always use :func:`get_handler`!

    **Threads:**

    All threads can read and write to the configuration data.
    **Proper thread-safeness must be ensured** by the the thread modifying the data by acquiring the lock
    Easiest and best way is to use the context handler::

        with cfg:
           cfg['key'] = 66
           cfg.setndefault('hello', value='world')

    For a single function call, this is done implicitly. In this case, there is no need
    to explicitly acquire the lock.

    Alternatively, you can lock and release manually by using :func:`acquire` and :func:`release`
    But be very sure to release the lock even in cases of errors an exceptions!
    Else we have a deadlock.

    Reading may be done without acquiring a lock. But be aware that when reading multiple values without locking, another
    thread may intervene and modify some values in between! So, locking is still recommended.
    """

    def __init__(self, name):
        self.name: str = name
        self._loaded_from: Optional[str] = None
        # Initialize this as empty standard dict. Type may be overwritten by config_dict
        self._data = {}
        # self._hash = hashlib.md5(self._data.__str__().encode('utf8')).digest()
        # Pre-computed MD5 hash of an empty dictionary
        self._hash = b'\x99\x91K\x93+\xd3zP\xb9\x83\xc5\xe7\xc9\n\xe9;'
        # Using a RLock to prevent deadlocks
        # This allows to have an always-on safety lock around the config_dict function and still work with outer locked context
        # Writing is a rare event, so performance is not an issue
        self._lock = threading.RLock()

    def acquire(self) -> bool:
        return self._lock.acquire()

    def release(self) -> None:
        return self._lock.release()

    @property
    def loaded_from(self) -> Optional[str]:
        """Property to store filename from which the config was loaded"""
        return self._loaded_from

    @loaded_from.setter
    def loaded_from(self, filename: str) -> None:
        self._loaded_from = filename

    def __enter__(self) -> 'ConfigHandler':
        self.acquire()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb) -> None:
        self.release()

    def __getitem__(self, key) -> Any:
        return self._data[key]

    def __setitem__(self, key, value):
        # We rely on calling function to properly lock before writing
        # Locking here will only help in the rarest of cases (because of mutable objects) and suggests false safety
        self._data[key] = value

    def __delitem__(self, *args, **kwargs):
        # We rely on calling function to properly lock before writing
        # Locking here will only help in the rarest of cases (because of mutable objects) and suggests false safety
        self._data.__delitem__(*args, **kwargs)

    def get(self, key, *, default=None):
        """
        Enforce keyword on default to avoid accidental misuse when actually getn is wanted
        """
        with self._lock:
            return self._data.get(key, default)

    def setdefault(self, key, *, value):
        """
        Enforce keyword on default to avoid accidental misuse when actually setndefault is wanted
        """
        with self._lock:
            return self._data.setdefault(key, value)

    def getn(self, *keys, default=None):
        """
        Get the value at arbitrary hierarchy depth. Return ``default`` if key not present

        The *default* value is returned no matter at which hierarchy level the path aborts.
        A hierarchy is considered as any type with a :func:`get` method.
        """
        with self._lock:
            sub = self._data
            for idx in range(0, len(keys)):
                try:
                    sub = sub.get(keys[idx], default)
                except AttributeError:
                    break
        return sub

    def setn(self, *keys, value, hierarchy_type=None) -> None:
        """
        Set the ``key: value`` pair at arbitrary hierarchy depth

        All non-existing hierarchy levels are created.

        :param keys: Key hierarchy path through the nested levels
        :param value: The value to set
        :param hierarchy_type: The type for new hierarchy levels. If *None*, the top-level type
            is used
        """
        with self._lock:
            if hierarchy_type is None:
                hierarchy_type = type(self._data)
            sub = self._data
            for idx in range(0, len(keys) - 1):
                sub = sub.setdefault(keys[idx], hierarchy_type())
            sub[keys[-1]] = value

    def setndefault(self, *keys, value, hierarchy_type=None):
        """
        Set the ``key: value`` pair at arbitrary hierarchy depth unless the key already exists

        All non-existing hierarchy levels are created.

        :param keys: Key hierarchy path through the nested levels
        :param value: The default value to set
        :param hierarchy_type: The type for new hierarchy levels. If *None*, the top-level type
            is used
        :return: The actual value or or the default value if key does not exit
        """
        with self._lock:
            if hierarchy_type is None:
                hierarchy_type = type(self._data)
            sub = self._data
            for idx in range(0, len(keys) - 1):
                sub = sub.setdefault(keys[idx], hierarchy_type())
            value = sub.setdefault(keys[-1], value)
        return value

    def __str__(self):
        return f'ConfigHandler({self.name}):: ' + self._data.__str__()

    def __contains__(self, item):
        return self._data.__contains__(item)

    def __iter__(self):
        return self._data.__iter__()

    def __len__(self) -> int:
        return self._data.__len__()

    def items(self):
        return self._data.items()

    def keys(self):
        return self._data.keys()

    def values(self):
        return self._data.values()

    def config_dict(self, data):
        """
        Initialize configuration data from dict-like data structure

        :param data: configuration data
        """
        logger.debug(f"({self.name}) Replacing current config data")
        with self._lock:
            self._data = copy.deepcopy(data)
            self._hash = hashlib.md5(self._data.__str__().encode('utf8')).digest()

    def is_modified(self) -> bool:
        """
        Check if the data has changed since the last load/store

        > [!NOTE]
        > This relies on the *__str__* representation of the underlying data structure
        > In case of ruamel, this ignores comments and only looks at the data
        """
        with self._lock:
            is_modified_value = self._hash != hashlib.md5(self._data.__str__().encode('utf8')).digest()
        return is_modified_value

    def clear_modified(self) -> None:
        """
        Sets the current state as new baseline, clearing the is_modified state
        """
        with self._lock:
            self._hash = hashlib.md5(self._data.__str__().encode('utf8')).digest()

    def save(self, only_if_changed: bool = False) -> None:
        """Save config back to the file it was loaded from

        If you want to save to a different file, use :func:`write_yaml`.
        """
        # Developers note: Only YAML supported for now.
        # If so inclined somebody may implement a FactoryPattern
        with self._lock:
            write_yaml(self, self._loaded_from, only_if_changed=only_if_changed)
            self.clear_modified()

    def load(self, filename: str) -> None:
        """Load YAML config file into memory"""
        # Developers note: Only YAML supported for now.
        # If so inclined somebody may implement a FactoryPattern
        load_yaml(self, filename)


# ---------------------------------------------------------------------------
# The main entry point
# ---------------------------------------------------------------------------

# Collects all created config handlers
# Using a simple dict as this is sufficient if nobody accesses that directly unless he knows exactly what he is doing
# and it saves a lot of code
handlers: Dict[str, ConfigHandler] = {}


def get_handler(name: str) -> ConfigHandler:
    """
    Get a configuration data handler with the specified name, creating it
    if it doesn't yet exit. If created, it is always created empty.

    This is the main entry point for obtaining an configuration handler

    :param name: Name of the config handler
    :return: The configuration data handler for *name*
    :rtype: ConfigHandler
    """
    _acquire_lock()
    try:
        if name in handlers:
            cfg_handler = handlers[name]
        else:
            cfg_handler = handlers[name] = ConfigHandler(name)
    finally:
        _release_lock()
    return cfg_handler


# ---------------------------------------------------------------------------
# Pre-defined file I/O for yaml
# ---------------------------------------------------------------------------


def load_yaml(cfg: ConfigHandler, filename: str) -> None:
    """
    Load a yaml file into a ConfigHandler

    :param cfg: ConfigHandler instance
    :param filename: filename to yaml file
    :return: None
    """
    yaml = YAML(typ='rt')
    logger.info(f"({cfg.name}) Loading yaml file '{filename}'")
    with cfg:
        cfg.loaded_from = filename
        with open(filename) as stream:
            cfg.config_dict(yaml.load(stream))


def write_yaml(cfg: ConfigHandler, filename: str, only_if_changed: bool = False, *args, **kwargs) -> None:
    """
    Writes ConfigHandler data to yaml file / sys.stdout

    :param cfg: ConfigHandler instance
    :param filename: filename to output file. If *sys.stdout*, output is written to console
    :param only_if_changed: Write file only, if ConfigHandler.is_modified()
    :param args: passed on to yaml.dump(...)
    :param kwargs: passed on to yaml.dump(...)
    :return: None
    """
    # Lock cfg first thing, to prevent any changes between write call and actual write-out
    with cfg:
        if cfg.is_modified() or not only_if_changed:
            logger.info(f"({cfg.name}) Writing yaml file '{filename}'")
            yaml = YAML(typ='rt')
            # The access to "private" _data here is ok, because the lock is acquired
            if filename is sys.stdout:
                yaml.dump(cfg._data, sys.stdout, *args, **kwargs)
            else:
                with open(filename, 'wt') as stream:
                    yaml.dump(cfg._data, stream, *args, **kwargs)
        else:
            logger.info(f"({cfg.name}) "
                        f"Not writing to file as data has unchanged status set (use only_if_changed=False to override)")
