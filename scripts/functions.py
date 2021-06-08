
def list_pagination(list_all,page_items_count,page):

    if((len(list_all) % page_items_count) > 0):
        pages_count = int(len(list_all) / page_items_count) + 1
    else:
        pages_count = int(len(list_all) / page_items_count)

    list_paginated = [list_all[i:i+pages_count] for i in range(0, len(list_all), pages_count)]

    return(list_paginated[page])

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
    
def config_key_conversion(conf):
    
    # Start the future now...: convert some of the old naming into new naming
    if('AUDIOVOLCHANGESTEP' in conf):
        conf['VOL_CHANGE_STEP'] = conf.pop('AUDIOVOLCHANGESTEP')
    if('AUDIOVOLMAXLIMIT' in conf):
        conf['VOL_LIMIT_MAX'] = conf.pop('AUDIOVOLMAXLIMIT')
    if('AUDIOVOLMINLIMIT' in conf):
        conf['VOL_LIMIT_MIN'] = conf.pop('AUDIOVOLMINLIMIT')
    if('AUDIOVOLSTARTUP' in conf):
        conf['VOL_LEVEL_SYSTEM'] = conf.pop('AUDIOVOLSTARTUP')
    if('VOLCHANGEIDLE' in conf):
        conf['VOL_CHANGE_IF_IDLE'] = conf.pop('VOLCHANGEIDLE')
    if('VOLUMEMANAGER' in conf):
        conf['VOL_MANAGER'] = conf.pop('VOLUMEMANAGER')
    if('AUDIOFOLDERSPATH' in conf):
        conf['AUDIO_FOLDER_PATH'] = conf.pop('AUDIOFOLDERSPATH')
    if('AUDIOIFACEACTIVE' in conf):
        conf['AUDIO_IFACE_ACTIVE'] = conf.pop('AUDIOIFACEACTIVE')
    if('AUDIOIFACENAME' in conf):
        conf['AUDIO_IFACE_NAME'] = conf.pop('AUDIOIFACENAME')
    if('IDLETIMESHUTDOWN' in conf):
        conf['SHUTDOWN_IDLE_TIME'] = conf.pop('IDLETIMESHUTDOWN')
    
    return(conf)

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
