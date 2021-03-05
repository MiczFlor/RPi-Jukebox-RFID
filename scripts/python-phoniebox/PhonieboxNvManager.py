#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import json

#Non Volatile data storage
# to avoid frequent file system writes to prevent sd card wereout this module should take care of non volatile data and their storage
# preferably as human readable, probaly json
# the idea is that submodules create an nv object, for data they like to store
#the Idea is just to handle dictionaries, do we need data type awareness here?
#this could offer the option, that instead of a central configuration, each subclass can handle its configuration on its own, with setter / getter methods
class nv_object():
    __instance = None
    @staticmethod 
    def getInstance():
        """ Static access method. """
        if nv_object.__instance == None:
            nv_object()
        return nv_object.__instance
    def __init__(self):
        """ Virtually private constructor. """
        if nv_object.__instance != None:
            raise Exception("This class is a singleton!")
        else:
            nv_object.__instance = self


        nv_manager register new object
    
    def get()

    sef set(val)


class nv_manager
    __init__(file_name)

    def register_new_nv_object:
        

    def set_storage_frequncey:

    read
        # Read data from file:
        data = json.load( open( "file_name.json" ) )

    write
        # Serialize data into file:
        json.dump( data, open( "file_name.json", 'w' ) )