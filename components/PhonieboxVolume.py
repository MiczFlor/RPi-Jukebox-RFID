#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import alsaaudio

class volume_control_alsa:
    def __init__(self):
         self.mixer = alsaaudio.Mixer('Master', 0)
         self.volume = self.mixer.getvolume()[0]

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

    def inc(self, param=None):
        step = param.get('step')
        if step is None:
            step = 3
        volume = self.volume +step
        if (volume > 100): volume = 100
        self.volume = volume
        self.mixer.setvolume(self.volume)
        return ({'volume':self.volume})

    def dec(self, param=None):
        step = param.get('step')
        if step is None:
            step = 3
        volume = self.volume -step
        if (volume < 0): volume = 0
        self.volume = volume
        self.mixer.setvolume(self.volume)
        return ({'volume':self.volume})

    def mute(self,param=None):
        self.mixer.setmute(1)
        return ({})

    def unmute(self,param=None):
        self.mixer.setmute(0)
        return ({})

    def play_wave_file(self,file_name):	
        import wave
        with wave.open(file_name, 'rb') as f:
            format = None

            # 8bit is unsigned in wav files
            if f.getsampwidth() == 1:
                format = alsaaudio.PCM_FORMAT_U8
            # Otherwise we assume signed data, little endian
            elif f.getsampwidth() == 2:
                format = alsaaudio.PCM_FORMAT_S16_LE
            elif f.getsampwidth() == 3:
                format = alsaaudio.PCM_FORMAT_S24_3LE
            elif f.getsampwidth() == 4:
                format = alsaaudio.PCM_FORMAT_S32_LE
            else:
                raise ValueError('Unsupported format')

            periodsize = f.getframerate() // 8

            print('%d channels, %d sampling rate, format %d, periodsize %d\n' % (f.getnchannels(),f.getframerate(), format,	 periodsize))

            device = alsaaudio.PCM(channels=f.getnchannels(), rate=f.getframerate(), format=format, periodsize=periodsize, device="default")
    
            data = f.readframes(periodsize)
            while data:
                device.write(data)
                data = f.readframes(periodsize)


def list_cards():
    print("Available sound cards:")
    for i in alsaaudio.card_indexes():
        (name, longname) = alsaaudio.card_name(i)
        print("  %d: %s (%s)" % (i, name, longname))

def list_mixers(kwargs):
    print("Available mixer controls:")
    for m in alsaaudio.mixers(**kwargs):
        print("  '%s'" % m)

