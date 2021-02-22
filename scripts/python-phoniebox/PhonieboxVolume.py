#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import alsaaudio

class volume_control_alsa:
    def __init__(self):
         self.mixer = alsaaudio.Mixer('Master', 0)
         self.volume = 0
         #self.mixer.getvolume()

    def get(self, param):
        return ({'volume':self.volume})

    def set(self, param):
        volume = param.get('volume')
        if isinstance(volume, int):
            if (volume < 0): volume = 0;
            if (volume > 100): volume = 100;
            self.volume = volume
            self.mixer.setvolume(self.volume)
        else:
            volume = -1
        return ({'volume':volume})

    def inc(self, param):
        volume = self.volume +3
        if (volume > 100): volume = 100
        self.volume = volume
        self.mixer.setvolume(self.volume)
        return ({'volume':self.volume})

    def dec(self, param):
        volume = self.volume -3
        if (volume < 0): volume = 0
        self.volume = volume
        self.mixer.setvolume(self.volume)
        return ({'volume':self.volume})



def list_cards():
    print("Available sound cards:")
    for i in alsaaudio.card_indexes():
        (name, longname) = alsaaudio.card_name(i)
        print("  %d: %s (%s)" % (i, name, longname))

def list_mixers(kwargs):
    print("Available mixer controls:")
    for m in alsaaudio.mixers(**kwargs):
        print("  '%s'" % m)

