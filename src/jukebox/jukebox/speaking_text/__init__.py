"""
Text to Speech. Plugin to speak any given text via speaker
"""

import logging
import jukebox.cfghandler
import shlex
import subprocess

logger = logging.getLogger('jb.speaking_text')
cfg = jukebox.cfghandler.get_handler('jukebox')


def run_unix_command(command):
    cmds = shlex.split(command)
    return subprocess.Popen(cmds, start_new_session=True)


# http://espeak.sourceforge.net/commands.html
def with_espeak(text, params):
    lang = params['lang']

    speakPunct = ''
    if params['speakPunct']:
        speakPunct = '--punct="<characters>"'

    if params['speed'] == 'slow':
        speed = 75
    elif params['speed'] == 'fast':
        speed = 125
    else:
        speed = 100

    if params['voice'] == 'male':
        voice = 'm3'
    elif params['voice'] == 'croak':
        voice = 'croak'
    elif params['voice'] == 'whisper':
        voice = 'whisper'
    # female is default
    else:
        voice = 'f3'

    command = 'espeak -v%s+%s -s%s %s "%s" 2>>/dev/null' % (lang, voice , speed, speakPunct, text)
    run_unix_command(command)


def say(text, params={'lang': 'en', 'speed': 'normal', 'speakPunct': False, 'voice': 'female'}):
    with_espeak(text, params)
