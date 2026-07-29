#!/usr/bin/env python
"""
Setup tool to register the audio sinks as primary and secondary audio outputs.

Run this once after installation. Can be re-run at any time to change the settings.
For more information see [Audio Configuration](../../builders/audio.md#configuration).
"""
import os
import argparse

import pulsectl

from typing import Optional
import misc.inputminus as pyil
from misc.inputminus import msg_highlight
from misc.simplecolors import Colors
import jukebox.cfghandler
import jukebox.plugs

jukebox.plugs.ALLOW_DIRECT_IMPORTS = True
import components.hostif.linux as host  # noqa: E402


class AudioConfig:
    def __init__(self, jukebox_cfg_file: str,
                 full_secondary_list: bool = False):
        self.jukebox_cfg_file: str = jukebox_cfg_file
        self.primary: Optional[str] = None
        self.secondary: Optional[str] = None
        self.toggle_on_connect: bool = False
        self.full_secondary_list: bool = full_secondary_list

    def __str__(self):
        string = f"jukebox_cfg_file        = {self.jukebox_cfg_file}\n"
        string += f"primary                 = {self.primary}\n"
        string += f"secondary               = {self.secondary}\n"
        string += f"full_secondary_list     = {self.full_secondary_list}\n"
        string += f"toggle_on_connect       = {self.toggle_on_connect}\n"
        return string


def query_sinks(audio_config: AudioConfig):
    pulse = pulsectl.Pulse('jukebox-config')
    sinks = pulse.sink_list()
    msg_highlight('Available audio outputs')
    for idx, sink in enumerate(sinks):
        print(f"{Colors.lightgreen}{idx:2d}{Colors.reset}:"
              f"  {Colors.lightcyan}{sink.name}{Colors.reset}")
        print(f"       {Colors.lightgrey}Description: {sink.description}{Colors.reset}")
        print(f"       {Colors.lightgrey}Module     : {sink.driver}{Colors.reset}")
    print("")
    primary_idx = pyil.input_int("Primary audio output (no bluetooth)?", min=0, max=len(sinks) - 1,
                                 prompt_color=Colors.lightgreen,
                                 prompt_hint=True, blank=0)
    audio_config.primary = sinks[primary_idx].name
    print(f"\n*** Primary audio output = {audio_config.primary}\n")

    if audio_config.full_secondary_list or len(sinks) > 1:
        secondary_idx = pyil.input_int(
            "Secondary audio output (typically bluetooth)? Set to -1 for empty.",
            min=-1, max=len(sinks) - 1,
            prompt_color=Colors.lightgreen,
            prompt_hint=True, blank=-1)
        if secondary_idx >= 0:
            audio_config.secondary = sinks[secondary_idx].name
            print(f"\n*** Secondary audio output = {audio_config.secondary}\n")
            audio_config.toggle_on_connect = pyil.input_yesno(
                "Automatically toggle output on connection of secondary device?",
                prompt_color=Colors.lightgreen,
                prompt_hint=True, blank=True)

    print('\nSummary:')
    print(audio_config)
    return audio_config


def configure_jukebox(audio_config: AudioConfig):
    cfg_jukebox = jukebox.cfghandler.get_handler('juke')
    cfg_jukebox.load(audio_config.jukebox_cfg_file)

    cfg_jukebox.setn('pulse', 'toggle_on_connect', value=audio_config.toggle_on_connect)

    cfg_jukebox.setn('pulse', 'outputs', value={})
    key = 'primary'
    cfg_jukebox.setn('pulse', 'outputs', key, 'alias', value='Speakers')
    cfg_jukebox.setn('pulse', 'outputs', key, 'volume_limit', value=100)
    cfg_jukebox.setn('pulse', 'outputs', key, 'pulse_sink_name', value=audio_config.primary)

    if audio_config.secondary is not None:
        key = 'secondary'
        cfg_jukebox.setn('pulse', 'outputs', key, 'alias', value='Bluetooth Headset')
        cfg_jukebox.setn('pulse', 'outputs', key, 'volume_limit', value=100)
        cfg_jukebox.setn('pulse', 'outputs', key, 'pulse_sink_name', value=audio_config.secondary)

    print(f"\n*** Writing {audio_config.jukebox_cfg_file}")
    cfg_jukebox.save()
    return audio_config


def welcome(audio_config: AudioConfig):
    msg_highlight('The Jukebox audio output configuration tool')
    print("Please note:")
    print(" - Read the documentation page 'Audio Configuration'")
    print(" - Primary output must be available on system boot - i.e. not a bluetooth device")
    print(" - Secondary output is typically a bluetooth device")
    print(" - Connect your bluetooth device before running this script (or run it again later)")
    print(" - Exit all running Jukeboxes (including services) before continuing")
    print("     $ systemctl --user stop jukebox-daemon")
    print(f" - Will replace your jukebox audio output configuration in\n   '{audio_config.jukebox_cfg_file}'")
    print(" - To get a list of all sinks, check out the list shown by this tool or run")
    print("     $ wpctl status")
    print(" - To test a sink directly with its ID from wpctl status:")
    print("     $ pw-play --target=<id> /usr/share/sounds/alsa/Front_Center.wav")


def goodbye(audio_config: AudioConfig):
    msg_highlight('All done!')
    print('Summary:')
    print(audio_config)

    msg_highlight('Note:')
    print('You must restart the Jukebox service for changes to take effect:')
    print('$ systemctl --user restart jukebox-daemon\n')


def main():
    script_path = os.path.abspath(os.path.dirname(os.path.realpath(__file__)))
    default_cfg_jukebox = os.path.abspath(os.path.join(script_path, '../../shared/settings/jukebox.yaml'))

    argparser = argparse.ArgumentParser(description='The Jukebox audio configuration tool')
    argparser.add_argument('-j', '--jukebox', type=argparse.FileType('r'), default=default_cfg_jukebox,
                           help=f"Jukebox configuration file [default: '{default_cfg_jukebox}'",
                           metavar="FILE")
    argparser.add_argument('-f', '--full', default=False, action='store_true',
                           help='Show full, unfiltered list of sinks for secondary output')
    args = argparser.parse_args()

    audio_config = AudioConfig(jukebox_cfg_file=os.path.abspath(os.path.expanduser(args.jukebox.name)),
                               full_secondary_list=args.full)

    welcome(audio_config)

    if host.is_any_jukebox_service_active():
        msg_highlight('Jukebox service is running!')
        print("\nPlease stop jukebox-daemon service and restart tool")
        print("$ systemctl --user stop jukebox-daemon\n\n")
        print("Don't forget to start the service again :-)")
        return

    audio_config = query_sinks(audio_config)
    audio_config = configure_jukebox(audio_config)
    goodbye(audio_config)


if __name__ == '__main__':
    main()
