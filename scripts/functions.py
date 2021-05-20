
def read_config_bash(paths_all):

    # paths_all must be a list like [a, b, c]
    conf = {}
    for path_config in paths_all:
        # read config
        with open(path_config) as myfile:
            for line in myfile:
                if not line.lstrip().startswith('#'):
                    name, var = line.partition("=")[::2]
                    conf[name.strip()] = var.strip()
    # strip " off values in dictionary conf
    conf = {k: v.strip('"') for (k, v) in conf.items()}
    return conf

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
