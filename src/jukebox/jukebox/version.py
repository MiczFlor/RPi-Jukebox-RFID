
VERSION_MAJOR = 3
VERSION_MINOR = 2
VERSION_PATCH = 1
VERSION_EXTRA = ""

__version__ = '%i.%i.%i' % (VERSION_MAJOR, VERSION_MINOR, VERSION_PATCH)
__version_info__ = (VERSION_MAJOR, VERSION_MINOR, VERSION_PATCH)

if VERSION_EXTRA:
    __version__ = "%s.%s" % (__version__, VERSION_EXTRA)
    __version_info__ = (VERSION_MAJOR, VERSION_MINOR, VERSION_PATCH, VERSION_EXTRA)


def version():
    """Return the Jukebox version as a string"""
    return __version__


def version_info():
    """Return the Jukebox version as a tuple of three numbers

    If this is a development version, an identifier string will be appended after the third integer.
    """
    return __version_info__
