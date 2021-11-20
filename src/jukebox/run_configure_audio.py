#!/usr/bin/env python3
"""

"""
import os
import argparse

import pulsectl

import misc.inputminus as pyil
from misc.simplecolors import Colors
import jukebox.cfghandler

deliminator_length = 79


def msg_highlight(msg, color=Colors.lightblue):
    print(f"\n{color}" + "*" * deliminator_length)
    print(msg)
    print("*" * deliminator_length + f"{Colors.reset}")


def check_jukebox_running():
    pass


def query_sinks():
    pulse = pulsectl.Pulse('jukebox-config')
    sinks = pulse.sink_list()
    msg_highlight('Available audio outputs')
    for idx, sink in enumerate(sinks):
        print(f"{Colors.lightgreen}{idx:2d}{Colors.reset}:"
              f"  {Colors.lightcyan}{sink.name}{Colors.reset}")
    print("")
    primary_idx = pyil.input_int("Primary audio output (no bluetooth)?", min=0, max=len(sinks) - 1,
                                 prompt_color=Colors.lightgreen,
                                 prompt_hint=True, blank=0)
    primary = sinks[primary_idx].name
    print(f"Primary audio output = {primary}\n")
    secondary_idx = pyil.input_int("Secondary audio output (typically bluetooth)? Set to -1 for empty.",
                                   min=-1, max=len(sinks) - 1,
                                   prompt_color=Colors.lightgreen,
                                   prompt_hint=True, blank=-1)
    secondary = None
    toggle_on_connect = False
    if secondary_idx >= 0:
        secondary = sinks[secondary_idx].name
        print(f"Secondary audio output = {secondary}\n")
        toggle_on_connect = pyil.input_yesno("Automatically toggle output on connection of secndary device?",
                                             prompt_color=Colors.lightgreen,
                                             prompt_hint=True, blank=True)
    return primary, secondary, toggle_on_connect


def configure_jukebox(filename, primary, secondary, toggle_on_connect):
    cfg_jukebox = jukebox.cfghandler.get_handler('juke')
    cfg_jukebox.load(filename)

    cfg_jukebox.setn('pulse', 'toggle_on_connect', value=toggle_on_connect)

    cfg_jukebox.setn('pulse', 'outputs', value={})
    key = 'primary'
    cfg_jukebox.setn('pulse', 'outputs', key, 'alias', value='Speakers')
    cfg_jukebox.setn('pulse', 'outputs', key, 'volume_limit', value=100)
    cfg_jukebox.setn('pulse', 'outputs', key, 'soft_max_volume', value=100)
    cfg_jukebox.setn('pulse', 'outputs', key, 'pulse_sink_name', value=primary)

    if secondary is not None:
        key = 'secondary'
        cfg_jukebox.setn('pulse', 'outputs', key, 'alias', value='Bluetooth Headset')
        cfg_jukebox.setn('pulse', 'outputs', key, 'volume_limit', value=100)
        cfg_jukebox.setn('pulse', 'outputs', key, 'soft_max_volume', value=100)
        cfg_jukebox.setn('pulse', 'outputs', key, 'pulse_sink_name', value=secondary)

    cfg_jukebox.save()


def welcome():
    msg_highlight('The Jukebox audio output configuration tool')
    print("""
Please note:
 - Primary output must be available on system boot - i.e. not a bluetooth device
 - Secondary output is typically a bluetooth device
 - Connect your bluetooth device before running this script (or run it again later)
 - Will overwrite your audio output configuration in 'filename'
 - Exit all running Jukeboxes (including services) before continuing
     $ sudo systemctl stop jukebox-daemon
 - Checkout the documentation at TBD
 - If you are not sure which device is which, you can try them with
     $ paplay -d sink_name /usr/share/sounds/alsa/Front_Center.wav
 - To get a list of all sinks, check out below list or use
     $ pactl list sinks short
    """)


def goodbye():
    # Adjust Aliases and Volume Limits in the config file
    pass


def main():
    # Get absolute path of this script
    script_path = os.path.abspath(os.path.dirname(os.path.realpath(__file__)))
    default_cfg_jukebox = os.path.abspath(os.path.join(script_path, '../../shared/settings/jukebox.yaml'))

    argparser = argparse.ArgumentParser(description='The Jukebox audio configuration tool')
    argparser.add_argument('-c', '--conf', type=argparse.FileType('r'), default=default_cfg_jukebox,
                           help=f"jukebox configuration file [default: '{default_cfg_jukebox}'",
                           metavar="FILE")
    args = argparser.parse_args()

    welcome()
    primary, secondary, toggle_on_connect = query_sinks()
    configure_jukebox(args.conf.name, primary, secondary, toggle_on_connect)
    goodbye()


if __name__ == '__main__':
    main()
