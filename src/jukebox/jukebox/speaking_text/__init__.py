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
    # Language
    lang = cfg.getn('speaking_text', 'lang') or 'en'
    if 'lang' in params:
        lang = params['lang']

    # Speak punctuation?
    speakPunct = ''
    speakPunctOption = cfg.getn('speaking_text', 'speakPunct') or False
    if 'speakPunct' in params:
        speakPunctOption = params['speakPunct']

    if speakPunctOption:
        speakPunct = '--punct="<characters>"'

    # speed in words-per-minute
    speedOption = cfg.getn('speaking_text', 'speed') or 'normal'
    if 'speed' in params:
        speedOption = params['speed']

    if speedOption == 'slow':
        speed = 75
    elif speedOption == 'fast':
        speed = 125
    else:
        speed = 100

    # Voice for the speech
    voiceOption = cfg.getn('speaking_text', 'voice') or 'female'
    if 'voice' in params:
        voiceOption = params['voice']

    if voiceOption == 'male':
        voice = 'm3'
    elif voiceOption == 'croak':
        voice = 'croak'
    elif voiceOption == 'whisper':
        voice = 'whisper'
    # female is default
    else:
        voice = 'f2'

    command = 'espeak -v%s+%s -s%s %s "%s" 2>>/dev/null' % (lang, voice, speed, speakPunct, text)
    run_unix_command(command)


def say(text, params={}):
    with_espeak(text, params)
