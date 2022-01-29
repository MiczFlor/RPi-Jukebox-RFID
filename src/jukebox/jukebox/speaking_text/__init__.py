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
def with_espeak(text, lang=None, speed=None, speak_punct=None, voice=None):
    # Language
    lang = lang or cfg.setndefault('speaking_text', 'lang', value='en')

    # Speak punctuation?
    speak_punct = speak_punct or cfg.setndefault('speaking_text', 'speak_punct', value=False)
    if speak_punct:
        speak_punct = '--punct="<characters>"'
    else:
        speak_punct = ''

    # speed in words-per-minute
    speed = speed or cfg.setndefault('speaking_text', 'speed', value='normal')
    if speed == 'normal':
        speed = 125
    elif speed == 'slow':
        speed = 85
    elif speed == 'fast':
        speed = 150

    # Voice for the speech
    voice = voice or cfg.setndefault('speaking_text', 'voice', value='female')
    if voice == 'female':
        voice = 'f2'
    elif voice == 'male':
        voice = 'm3'
    elif voice == 'croak':
        voice = 'croak'
    elif voice == 'whisper':
        voice = 'whisper'

    command = 'espeak -v%s+%s -s%s %s "%s" 2>>/dev/null' % (lang, voice, speed, speak_punct, text)
    logger.info(f"Command: '{command}'")
    run_unix_command(command)


def say(text, lang=None, speed=None, speak_punct=None, voice=None):
    with_espeak(text, lang, speed, speak_punct, voice)
