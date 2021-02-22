#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import json

#Non Volatile data storage
# to avoid frequent file system writes to prevent sd card wereout this module should take care of non volatile data and their storage
#preferably as homan readable
# the idea is that submodules create an nv object, for data they like to store, these are then interacting with a singletonm.

#do we need data type awareness?

class nv_object():
    __init__(instance_name,object_name)
        check ifexist
        nv_manager register new object
    
    def get()

    sef set(val)


class nv_manager
    __init__(file_name)

    register new object:

    set storage frequncex:

    read
        # Read data from file:
        data = json.load( open( "file_name.json" ) )

    write
        # Serialize data into file:
        json.dump( data, open( "file_name.json", 'w' ) )