"""
Text to Speech. Plugin to speak any given text via speaker
"""

import logging
import jukebox.cfghandler
import shlex
import subprocess

logger = logging.getLogger('jb.tts')
cfg = jukebox.cfghandler.get_handler('jukebox')


def run_unix_command(command):
    cmds = shlex.split(command)
    return subprocess.Popen(cmds, start_new_session=True)


def say(text, kwargs={'lang': 'en', 'speed': 125, 'speakPunct': '--punct="<characters>"'}):
    # http://espeak.sourceforge.net/commands.html
    command = 'espeak -v%s+f3 -s%s %s "%s" 2>>/dev/null' % (kwargs['lang'], kwargs['speed'], kwargs['speakPunct'], text)
    run_unix_command(command)
