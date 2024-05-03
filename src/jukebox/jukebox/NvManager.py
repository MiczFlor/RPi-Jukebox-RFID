#!/usr/bin/env python
# -*- coding: utf-8 -*-
import json
import os
import hashlib
class nv_manager():
    def __init__(self):
        self.all_nv_objects = []

    def load(self,default_filename,type=None):
        new_nv_dict = nv_dict(default_filename)
        self.all_nv_objects.append(new_nv_dict)
        return new_nv_dict

    def save_all(self):
        for nv_obj in self.all_nv_objects:
            #print ("Saving {} ".format(nv_obj))
            nv_obj.save_to_json()




# Todo: add hashing support

# this is inherting from dict
# you should not do this!
# In this case it is ok since we are just adding methods, and are not overwriting any parent methods
class nv_dict(dict):
    def __init__(self,default_filename=None):
        super().__init__()

        self.initial_hash = None
        self.default_filename=default_filename

        if self.default_filename is not None:
            if (os.path.isfile(self.default_filename) and os.access(self.default_filename, os.R_OK)):
                self.init_from_json(self.default_filename)
                self.default_filename_is_writeable = os.access(self.default_filename, os.W_OK)
            else:
                print ("File {} does not exist, creating it".format(self.default_filename))
                #self['nv_dict_version'] = 1.0
                self.default_filename_is_writeable = True
                self.save_to_json()
        self.initial_hash = self.hash()

    def __setitem__(self, item, value):
        self.dirty = True   #not working, see comment above, intention is to just write dicts which content has changed
        super(nv_dict,self).__setitem__(item, value)

    def init_from_json(self,path=None,merge=False):
        if merge is False:
            self.clear()
        self.update(json.load( open( path ) ))

    def hash(self):
        return hashlib.md5(json.dumps(self).encode('UTF8')).digest()

    def save_to_json(self,filename=None):
        actual_hash = self.hash()
        if self.initial_hash != actual_hash:
            self.initial_hash = actual_hash
            print ("Saving {} ".format(self))

            save_to_filename = None
            if filename is not None:
                if os.access(filename, os.W_OK) :
                    save_to_filename = filename
            else :
                if (self.default_filename_is_writeable):
                    save_to_filename = self.default_filename

            if save_to_filename is not None:
                with open(save_to_filename, 'w') as outfile:
                    json.dump( self, outfile, indent=2)
        else:
            print ("dont need to save")


if __name__ == "__main__":

    nvd = nv_dict()

    nvd['a'] = 1
    nvd['b'] = 2

    nvd['c'] = {'abc':123}

    nvd.save_to_json("test.json")
    nvd['d'] = {'abc':987}  #will not be stored in test

    nvd.save_to_json("test2.json")

    print (nvd)

    nvd.init_from_json("test.json")

    print (nvd)

    nvd2 = nv_dict(default_filename="test2.json")
    nvd2['b'] = {"xyz":"a string"}
    nvd2.save_to_json()

    nvd3 = nv_dict(default_filename="test3.json")



    nvm = nv_manager()

    nvd4 =nvm.load("test4.json")
    nvd4['a'] = 'A'

    print (nvm.all_nv_objects)

    nvd5 =nvm.load("test5.json")
    nvd5['B'] = 'B'

    print (nvm.all_nv_objects)

    nvm.save_all()
