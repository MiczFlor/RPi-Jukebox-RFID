__name__ = "helpers"


def is_int(s):
    """ return True if string is an int """
    try:
        int(s)
        return True
    except ValueError:
        return False


def str2bool(s):
    """ convert string to a python boolean """
    return s.lower() in ("yes", "true", "t", "1")


def str2num(s):
    """ convert string to an int or a float """
    try:
        return int(s)
    except ValueError:
        return float(s)
