
import os
import errno
import ctypes

libc = ctypes.CDLL(None, use_errno=True)

def errcheck(result, func, args):
    if result < 0:
        e = ctypes.get_errno()
        raise OSError(e, errno.strerror(e))
    return result

def lookup(restype, name, argtypes):
    f = libc[name]
    f.restye = restype
    f.argtypes = argtypes
    f.errcheck = errcheck
    return f


class SelfClosing(object):
    def __enter__(self):
        return self

    def __exit__(self, *exc):
        self.close()
        return False

    
