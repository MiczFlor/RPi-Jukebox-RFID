

def is_int(s):
    """ return True if string is an int """
    try:
        int(s)
        return True
    except ValueError:
        return False
        
def is_float(s):
    """ return True if string is an int """
    try:
        float(s)
        return True
    except ValueError:
        return False

def parse_args_tuple(self, args_tuple):
    if len(args_tuple) == 0:
        args = {}
    else:
        args = dict(pair.split('__') for pair in args_tuple)
    return args
