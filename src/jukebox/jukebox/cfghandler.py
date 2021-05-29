import sys
import threading
import logging
from ruamel.yaml import YAML
import hashlib

logger = logging.getLogger('jb.cfghandler')

# Collects all created config handlers
# Using a simple dict as this is sufficient if nobody accesses that directly unless he knows exactly what he is doing
# and it saves a lot of code
handlers = {}

# ---------------------------------------------------------------------------
# Global thread-related stuff
# ---------------------------------------------------------------------------
# _lock_module is used to serialize access to shared data structures in this module
# (currently only during creation of a new config_handler)
# Each config handler has its own lock for protecting access to the underlying shared data
# this cannot be acquired automatically, as the shared data is typically a mutable. It is in the users
# responsibility to do that. See documentation below for more info

_lock_module = threading.RLock()


def _acquire_lock():
    """
    Acquire the module-level lock for serializing access to shared data.

    This should be released with _releaseLock().
    """
    if _lock_module:
        _lock_module.acquire()


def _release_lock():
    """
    Release the module-level lock acquired by calling _acquireLock().
    """
    if _lock_module:
        _lock_module.release()


# ---------------------------------------------------------------------------
# The main entry point
# ---------------------------------------------------------------------------

def get_handler(name):
    """
    Get a configuration data handler with the specified name, creating it
    if it doesn't yet exit. If created, it is always created empty.

    This is the main entry point for obtaining an configuration handler

    :param name: Name of the config handler for reference
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


class ConfigHandler:
    """
    The actual configuration handler.

    Don't instantiate directly. Always use get_handler()!

    The concept is that config handler is created once in the main thread with
    >>> cfg = get_handler('global')
    and loaded
    >>> load_yaml(cfg, 'filename.yaml')
    and in all other modules (in potentially different threads) the same handler is obtained and used by
    >>> cfg = get_handler('global')

    This eliminates the need to pass an effectively global configuration handler by paramters across the entire design

    All threads can read and write to the configuration data.
    Proper thread-safeness must be ensured by the the thread modifying the data by acquiring the lock
    Easiest and best way is to use the context handler:
    with cfg:
       cfg['key'] = 66
       cfg.setdefault['hello'] = 'world'

    Alternatively, you can lock and release manually by using acquire() and release()
    But be very sure to release the lock even in cases of errors an exceptions!
    Else we have a deadlock!

    Reading can be done without acquiring a lock. But be aware that when reading multiple values without locking, another
    thread may intervene and modify some values in between

    """
    def __init__(self, name):
        self.name = name
        # Initialize this as empty standard dict. Type may be overwritten by config_dict
        self._data = {}
        # self._hash = hashlib.md5(self._data.__str__().encode('utf8')).digest()
        # Pre-computed MD5 hash of an empty dictionary
        self._hash = b'\x99\x91K\x93+\xd3zP\xb9\x83\xc5\xe7\xc9\n\xe9;'
        # Using a RLock to prevent deadlocks
        # This allows to have an always-on safety lock around the config_dict function and still work with outer locked context
        # Writing is a rare event, so performance is not an issue
        self._lock = threading.RLock()

    def acquire(self):
        return self._lock.acquire()

    def release(self):
        return self._lock.release()

    def __enter__(self):
        self.acquire()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.release()

    def __getitem__(self, key):
        return self._data[key]

    def __setitem__(self, key, value):
        # We rely on calling function to properly lock before writing
        # Locking here will only help in the rarest of cases (because of mutable objects) and suggests false safety
        self._data[key] = value

    def get(self, key, *, default=None):
        """
        Enforce keyword on default to avoid accidental misuse when actually getn is wanted
        """
        return self._data.get(key, default)

    def setdefault(self, key, *, value):
        """
        Enforce keyword on default to avoid accidental misuse when actually setndefault is wanted
        """
        return self._data.setdefault(key, value)

    def getn(self, *keys, default=None):
        """
        Get the value at arbitrary hierarchy depth. Return default if key not present

        Note: that default value is returned no matter at which hierarchy level the path aborts
        """
        with self._lock:
            if len(keys) == 1:
                return self._data.get(keys[0], default)
            else:
                try:
                    tmp = self._data[keys[0]]
                    for nk in keys[1:-1]:
                        tmp = tmp[nk]
                except KeyError as e:
                    return default
                else:
                    return tmp.get(keys[-1], default)

    def setndefault(self, *keys, value, create=False):
        """
        Set the key = value pair at arbitrary hierarchy depth unless the key already exists

        Note: default only refers to the lowest hierarchy level. All upper levels MUST exist
        else a KeyError is raised. That is because we cannot know which types the levels should consist of
        """
        if len(keys) == 1:
            return self._data.setdefault(keys[0], value)
        else:
            tmp = self._data[keys[0]]
            for nk in keys[1:-1]:
                tmp = tmp[nk]
            return tmp.setdefault(keys[-1], value)

    def __str__(self):
        return f'ConfigHandler({self.name}):: ' + self._data.__str__()

    def __contains__(self, item):
        return self._data.__contains__(item)

    def __iter__(self):
        return self._data.__iter__()

    def __len__(self):
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
        :return: None
        """
        logger.debug(f"({self.name}) Replacing current config data")
        with self._lock:
            self._data = data
            self._hash = hashlib.md5(self._data.__str__().encode('utf8')).digest()

    def is_modified(self):
        """
        Note: This relies on the __str__ representation of the underlying data structure
        In case of ruamel, this ignores comments and only looks at the data
        :return:
        """
        with self._lock:
            is_modified = self._hash != hashlib.md5(self._data.__str__().encode('utf8')).digest()
        return is_modified

    def clear_modified(self):
        """
        Sets the current state as new baseline, clearing the is_modified state
        :return:
        """
        with self._lock:
            self._hash = hashlib.md5(self._data.__str__().encode('utf8')).digest()


# ---------------------------------------------------------------------------
# Pre-defined file I/O for yaml
# ---------------------------------------------------------------------------


def load_yaml(cfg, filename) -> None:
    """
    Load a yaml file into a ConfigHandler
    :param cfg: ConfigHandler instance
    :param filename: filename to yaml file
    :return: None
    """
    yaml = YAML(typ='rt')
    logger.info(f"({cfg.name}) Loading yaml file '{filename}'")
    with open(filename) as stream:
        cfg.config_dict(yaml.load(stream))


def write_yaml(cfg, filename, only_if_changed=False, *args, **kwargs) -> None:
    """
    Writes ConfigHandler data to yaml file / sys.stdout
    :param cfg: ConfigHandler instance
    :param filename: filename to output file. If sys.stdout, output is written to console
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

