#!/usr/bin/env python
"""
Setup tool to register the PulseAudio sinks as primary and secondary audio outputs.

Will also setup equalizer and mono down mixer in the pulseaudio config file.

Run this once after installation. Can be re-run at any time to change the settings.
For more information see [Audio Configuration](../../builders/audio.md#audio-configuration).
"""
import os
import argparse
import re
import shutil
import sys

import pulsectl

from typing import (Optional, List)
import misc.inputminus as pyil
from misc.inputminus import msg_highlight
from misc.simplecolors import Colors
import jukebox.cfghandler
import jukebox.plugs

jukebox.plugs.ALLOW_DIRECT_IMPORTS = True
import components.hostif.linux as host  # noqa: E402


class PaConfigClass:
    def __init__(self, jukebox_cfg_file: str, pulse_cfg_file: str,
                 script_path: str,
                 treat_pulse_as_readonly: bool = False,
                 full_secondary_list: bool = False,
                 disable_switch_on_connect: bool = True):
        self.jukebox_cfg_file: str = jukebox_cfg_file
        self.pulse_cfg_file: str = pulse_cfg_file
        self.script_path: str = script_path
        self.primary: Optional[str] = None
        self.secondary: Optional[str] = None
        self.toggle_on_connect: bool = False
        self.enable_equalizer: bool = False
        self.enable_monomixer: bool = False
        self.set_system_default: bool = True
        self.disable_pulseaudio_autoswitch: bool = disable_switch_on_connect
        self.treat_pulse_as_readonly: bool = treat_pulse_as_readonly
        self.full_secondary_list: bool = full_secondary_list

    def __str__(self):
        string = f"jukebox_cfg_file        = {self.jukebox_cfg_file}\n"
        string += f"pulse_cfg_file          = {self.pulse_cfg_file}\n"
        string += f"treat_pulse_as_readonly = {self.treat_pulse_as_readonly}\n"
        string += f"primary                 = {self.primary}\n"
        string += f"secondary               = {self.secondary}\n"
        string += f"full_secondary_list     = {self.full_secondary_list}\n"
        string += f"toggle_on_connect       = {self.toggle_on_connect}\n"
        if not self.treat_pulse_as_readonly:
            string += f"add_equalizer           = {self.enable_equalizer}\n"
            string += f"add_monomixer           = {self.enable_monomixer}\n"
            string += f"disable PA's autoswitch = {self.disable_pulseaudio_autoswitch}\n"
            string += f"set_system_default      = {self.set_system_default}\n"
        return string


def sink_is_equalizer(sink: pulsectl.PulseSinkInfo):
    return sink.driver == 'module-ladspa-sink.c' and sink.description.__contains__('Eq10X2')


def sink_is_monomixer(sink: pulsectl.PulseSinkInfo):
    return sink.driver == 'module-remap-sink.c' and sink.description.__contains__('Mono')


def yield_upstream_sink(sink: pulsectl.PulseSinkInfo, all_sinks):
    while True:
        cnt = 0
        next_sink = []
        for candidate in all_sinks:
            print(f"Eval {candidate.name} // {sink.name}")
            if sink.name == candidate.proplist.get('device.master_device', ''):
                print(f" ---- {sink.name}")
                next_sink.append(candidate)
                cnt += 1
        print(f" FOR EXIT {cnt}")
        if cnt == 0:
            return
        if cnt > 1:
            msg_highlight("PANIC: Non unique signal processing chain", Colors.red)
            print(f"This means for the sink '{sink.name}', multiple sources exist!. These are:")
            for s in next_sink:
                print(f"  - {s.name}")
            print("\nThis tool cannot deal with that situation for automatic PulseAudio signal processing chain setup\n")
            print("You have three options:")
            print("  1) Yes, I know. I want it that way.")
            print("     Solution: Call this tool with parameter -n to disable automatic detection")
            print("  2) When selecting primary input start earlier in the signal chain to avoid ambiguities")
            print("     I.e. select the mono mixer sink directly and not the sound card sink")
            print("  3) There is a stale entry in your config.")
            print("     Solution: Delete one of the offending source from the PulseAudio configuration file\n")
            sys.exit(1)
        if cnt == 1:
            sink = next_sink[0]
            cnt = 0
            yield next_sink[0]


def yield_downstream_sink(sink: pulsectl.PulseSinkInfo, all_sinks):
    while True:
        for candidate in all_sinks:
            if candidate.name == sink.proplist.get('device.master_device', ''):
                break
        else:
            return
        sink = candidate
        yield candidate


def build_processing_chain(sink: pulsectl.PulseSinkInfo, all_sinks):
    chain: List[pulsectl.PulseSinkInfo] = [sink]
    index = 0
    for downstream in yield_downstream_sink(sink, all_sinks):
        chain.append(downstream)
    for upstream in yield_upstream_sink(sink, all_sinks):
        chain = [upstream, *chain]
        index += 1
    return chain, index


def query_sinks(pulse_config: PaConfigClass):  # noqa: C901
    pulse = pulsectl.Pulse('jukebox-config')
    sinks = pulse.sink_list()
    msg_highlight('Available audio outputs')
    for idx, sink in enumerate(sinks):
        print(f"{Colors.lightgreen}{idx:2d}{Colors.reset}:"
              f"  {Colors.lightcyan}{sink.name}{Colors.reset}")
        print(f"       {Colors.lightgrey}Description: {sink.description}{Colors.reset}")
        print(f"       {Colors.lightgrey}Module     : {sink.driver}{Colors.reset}")
        master_device = sink.proplist.get('device.master_device', None)
        if master_device:
            print(f"       {Colors.lightgrey}Sink       : {master_device}{Colors.reset}")
    print("")
    primary_idx = pyil.input_int("Primary audio output (no bluetooth)?", min=0, max=len(sinks) - 1,
                                 prompt_color=Colors.lightgreen,
                                 prompt_hint=True, blank=0)
    pulse_config.primary = sinks[primary_idx].name
    print(f"\n*** Primary audio output = {pulse_config.primary}\n")
    length_secondary = len(sinks) - 1

    if pulse_config.treat_pulse_as_readonly is False:
        print("\n*** Signal chain: ")
        primary_signal_chain, sidx = build_processing_chain(sinks[primary_idx], sinks)
        for idx, r in enumerate(primary_signal_chain):
            mark = '-->' if sidx == idx else '   '
            print(f"***   {mark} {idx} :: {r.name}")
        length_secondary -= len(primary_signal_chain) + 1
        print('')

    if pulse_config.full_secondary_list or length_secondary > 0:
        secondary_idx = pyil.input_int("Secondary audio output (typically bluetooth)? Set to -1 for empty.",
                                       min=-1, max=len(sinks) - 1,
                                       prompt_color=Colors.lightgreen,
                                       prompt_hint=True, blank=-1)
        if secondary_idx >= 0:
            pulse_config.secondary = sinks[secondary_idx].name
            print(f"\n*** Secondary audio output = {pulse_config.secondary}\n")
            pulse_config.toggle_on_connect = pyil.input_yesno("Automatically toggle output on connection of secondary device?",
                                                              prompt_color=Colors.lightgreen,
                                                              prompt_hint=True, blank=True)

    if pulse_config.treat_pulse_as_readonly is False:
        primary_is_mono = sink_is_monomixer(sinks[primary_idx])
        primary_is_equalizer = sink_is_equalizer(sinks[primary_idx])

        if primary_is_mono:
            print("*** Primary selection already is a Mono Down Mixer")
        if primary_is_equalizer:
            print("*** Primary selection already is an Equalizer")

        # User input: For changing the processing chain, always start at card level!

        if not primary_is_equalizer and not primary_is_mono:
            msg_highlight('Equalizer')
            print('\nYou may add an software equalizer to the primary output\n'
                  'to compensate for bass deficiencies of small-speaker setups.\n'
                  'If enabled, the default is to lift bass and treble slightly.\n'
                  'You can configure the coefficients in the pulse audio configuration file:\n'
                  f'{os.path.abspath(pulse_config.pulse_cfg_file)}\n')
            pulse_config.enable_equalizer = pyil.input_yesno("Enable an equalizer for the primary output?",
                                                             blank=pulse_config.enable_equalizer,
                                                             prompt_color=Colors.lightgreen,
                                                             prompt_hint=True)
            if pulse_config.enable_equalizer:
                try:
                    if sink_is_equalizer(primary_signal_chain[sidx - 1]):
                        pulse_config.enable_equalizer = False
                        print(f"\n*** Equalizer already configured for '{pulse_config.primary}' with name\n"
                              f"    '{primary_signal_chain[sidx - 1].name}'. Shifting entry point...")
                        pulse_config.primary = primary_signal_chain[sidx - 1].name
                        sidx -= 1
                except ValueError:
                    pass

        if not primary_is_mono:
            msg_highlight('Mono Speaker Box')
            print('\nIf you building a box with a single speaker, you probably want to\n'
                  'down-mix both stereo channels into mono signals.\n'
                  'Note: It does not matter if you connect you speaker to the left or right channel\n')
            pulse_config.enable_monomixer = pyil.input_yesno("Enable mono down mix for the primary output?",
                                                             blank=pulse_config.enable_monomixer,
                                                             prompt_color=Colors.lightgreen,
                                                             prompt_hint=True)
            # Let's check if we already have a Mono mixer in the signal chain
            # It must be the device directly upstream to this device!
            if pulse_config.enable_monomixer:
                try:
                    if sink_is_monomixer(primary_signal_chain[sidx - 1]):
                        pulse_config.enable_monomixer = False
                        print(f"\n*** Mono mixer already configured for '{pulse_config.primary}' with name\n"
                              f"    '{primary_signal_chain[sidx - 1].name}'. Shifting entry point...")
                        pulse_config.primary = primary_signal_chain[sidx - 1].name
                        sidx -= 1
                except ValueError:
                    pass

    print('\nSummary:')
    print(pulse_config)
    # sys.exit(0)

    return pulse_config


def configure_pa_equalizer(pulse_cfg_file_content, pulse_config: PaConfigClass):
    equalizer_name = f"equalizer_for_{pulse_config.primary}"
    print(f"\n*** Add equalizer for {pulse_config.primary}\n"
          f"    with name {equalizer_name}")
    pulse_cfg_file_content += f'\n# Jukebox option: Equalizer for sink {pulse_config.primary}\n'
    pulse_cfg_file_content += '# This is a 10 band equalizer, with center frequencies: '
    pulse_cfg_file_content += '31 Hz, 63 Hz, 125 Hz, 250 Hz, 500 Hz, 1 kHz, 2 kHz 4 kHz, 8 kHz, 16 kHz\n'
    pulse_cfg_file_content += '# For each frequency band the factor must be in range -48.0 ... + 24.0 (db)\n'
    pulse_cfg_file_content += f'load-module module-ladspa-sink sink_name={equalizer_name} ' \
                              f'sink_master={pulse_config.primary} ' \
                              f'plugin=caps label=Eq10X2 control=15.12,9.36,4.32,0,0,0,0,0,2.88,4.32\n'
    pulse_config.primary = equalizer_name

    return pulse_cfg_file_content, pulse_config


def configure_pa_monomixer(pulse_cfg_file_content, pulse_config: PaConfigClass):
    # load-module module-remap-sink master=alsa_output.platform-soc_sound.stereo-fallback
    # sink_name=mono sink_properties="device.description='Mono'" channels=2 channel_map=mono,mono
    mono_name = f"mono_downmix_of_{pulse_config.primary}"
    print(f"\n*** Add mono down mix for {pulse_config.primary}\n"
          f"    with name {mono_name}")
    pulse_cfg_file_content += f'\n# Jukebox option: Mono down-mix for sink {pulse_config.primary}\n'
    pulse_cfg_file_content += f'load-module module-remap-sink master={pulse_config.primary} ' \
                              f'sink_name={mono_name} ' \
                              f'sink_properties="device.description=\'Mono version of {pulse_config.primary}\'" ' \
                              f'channels=2 channel_map=mono,mono\n'
    pulse_config.primary = mono_name

    return pulse_cfg_file_content, pulse_config


def configure_pa_system_default(pulse_cfg_file_content: str, pulse_config: PaConfigClass):
    # Rewrite the current setting
    print(f"\n*** Set system default sink to {pulse_config.primary}")
    pulse_cfg_file_content, cnt = re.subn(r'^\s*set-default-sink\s+.*', 'set-default-sink ' + pulse_config.primary,
                                          pulse_cfg_file_content, flags=re.MULTILINE)
    if cnt == 0:
        # Add the setting, if there was no default sink
        pulse_cfg_file_content += '# The default sink. Note that is may still be changed at run time by various PulseAudio '
        pulse_cfg_file_content += 'rules e.g. when connecting a USB Sound Card\n'
        pulse_cfg_file_content += f'set-default-sink {pulse_config.primary}\n'
        # # Check if primary already set as default
        # if re.search(r'^\s*(set-default-sink\s+' + pulse_config.primary + r')',
        #              pulse_cfg_file_content, flags=re.MULTILINE) is None:
        #     # Comment out all default sink settings (if any)
        #     pulse_cfg_file_content = re.sub(r'^\s*(set-default-sink.*)', r'#\1', pulse_cfg_file_content, flags=re.MULTILINE)
        #     # Add the new setting
        #     pulse_cfg_file_content += f'set-default-sink {pulse_config.primary}\n'
    return pulse_cfg_file_content, pulse_config


def configure_pa_switch_on_connect(pulse_cfg_file_content):
    pulse_cfg_file_content, cnt = re.subn(r'^\s*(load-module\s+module-switch-on-connect)',
                                          '# Must be disabled for proper Jukebox function!\n' + r'# \1',
                                          pulse_cfg_file_content, flags=re.MULTILINE)
    if cnt > 0:
        print("\n*** Disable PA's module module-switch-on-connect (conflicts with Jukebox toggle function)")
    return pulse_cfg_file_content


def query_create_default_pa_config(script_path, config_file_path):
    default_config_path = os.path.normpath(os.path.join(script_path,
                                                        '../../resources/default-settings/pulseaudio.default.pa'))
    print(f"\n*** PulseAudio configuration file does not exist: '{config_file_path}'.")
    print(f"    RPI-Jukebox-RFID's default is: '{default_config_path}'.\n")
    query = pyil.input_yesno("Create new config file from RPi-Jukebox-RFID default?",
                             blank=True,
                             prompt_color=Colors.lightgreen,
                             prompt_hint=True)

    if query:
        shutil.copyfile(default_config_path, config_file_path)
    return query


def configure_pulseaudio(pulse_config: PaConfigClass):
    if pulse_config.treat_pulse_as_readonly:
        print("\n*** Not touching pulse audio configuration file due to command line parameter")
        return pulse_config

    if not os.path.isfile(pulse_config.pulse_cfg_file):
        query_create_default_pa_config(pulse_config.script_path, pulse_config.pulse_cfg_file)

    with open(pulse_config.pulse_cfg_file) as f:
        pulse_cfg_file_content = f.read()

    if pulse_config.enable_equalizer:
        pulse_cfg_file_content, pulse_config = configure_pa_equalizer(pulse_cfg_file_content, pulse_config)
    if pulse_config.enable_monomixer:
        pulse_cfg_file_content, pulse_config = configure_pa_monomixer(pulse_cfg_file_content, pulse_config)
    if pulse_config.set_system_default:
        pulse_cfg_file_content, pulse_config = configure_pa_system_default(pulse_cfg_file_content, pulse_config)
    if pulse_config.disable_pulseaudio_autoswitch:
        pulse_cfg_file_content = configure_pa_switch_on_connect(pulse_cfg_file_content)

    print(f"\n*** Writing {pulse_config.pulse_cfg_file}")
    with open(pulse_config.pulse_cfg_file, 'w') as f:
        f.write(pulse_cfg_file_content)

    return pulse_config


def configure_jukebox(pulse_config: PaConfigClass):
    cfg_jukebox = jukebox.cfghandler.get_handler('juke')
    cfg_jukebox.load(pulse_config.jukebox_cfg_file)

    cfg_jukebox.setn('pulse', 'toggle_on_connect', value=pulse_config.toggle_on_connect)

    cfg_jukebox.setn('pulse', 'outputs', value={})
    key = 'primary'
    cfg_jukebox.setn('pulse', 'outputs', key, 'alias', value='Speakers')
    cfg_jukebox.setn('pulse', 'outputs', key, 'volume_limit', value=100)
    cfg_jukebox.setn('pulse', 'outputs', key, 'pulse_sink_name', value=pulse_config.primary)

    if pulse_config.secondary is not None:
        key = 'secondary'
        cfg_jukebox.setn('pulse', 'outputs', key, 'alias', value='Bluetooth Headset')
        cfg_jukebox.setn('pulse', 'outputs', key, 'volume_limit', value=100)
        cfg_jukebox.setn('pulse', 'outputs', key, 'pulse_sink_name', value=pulse_config.secondary)

    print(f"\n*** Writing {pulse_config.jukebox_cfg_file}")
    cfg_jukebox.save()
    return pulse_config


def welcome(pulse_config: PaConfigClass):
    msg_highlight('The Jukebox audio output configuration tool')
    print("Please note:")
    print("  - This two does two steps:")
    print("       1) Setup up PulseAudio signal processing chain")
    print("       2) Register audio outputs with Jukebox")
    print(" - Read the documentation page 'Audio Configuration'")
    print(" - Primary output must be available on system boot - i.e. not a bluetooth device")
    print(" - Secondary output is typically a bluetooth device")
    print(" - Connect your bluetooth device before running this script (or run it again later)")
    print(" - Exit all running Jukeboxes (including services) before continuing")
    print("     $ systemctl --user stop jukebox-daemon")
    print(f" - Will replace your jukebox audio output configuration in\n   '{pulse_config.jukebox_cfg_file}'")
    print(f" - Will adjust your pulse audio configuration in\n   '{pulse_config.pulse_cfg_file}'")
    print(" - If you are not sure which device is which, you can try them with")
    print("     $ paplay -d sink_name /usr/share/sounds/alsa/Front_Center.wav")
    print(" - To get a list of all sinks, check out below list or use")
    print("     $ pactl list sinks short")
    print(" - When re-running this tool, always select the earliest desired entry point into the")
    print("   signal processing chain, i.e. mono mixer or equalizer (if enabled)")
    print(" - This tool has limitations: it can add or disable modules to the PulseAudio")
    print("   processing chain. It cannot remove them: edit the PulseAudio file directly, if it bothers you.")
    print(" - Equally, this tool can only build the signal chain ")
    print("     mono mix (optional) -> equalizer (optional) -> sound card")
    print("   If you want to use a more complex setup, configure the PulseAudio manually and ")
    print("   run this tool with the -n parameter!")
    if pulse_config.treat_pulse_as_readonly:
        print("\n   NOTE: Started with option don't touch PulseAudio configuration.")


def goodbye(pulse_config: PaConfigClass):
    # Adjust Aliases and Volume Limits in the config file
    msg_highlight('All done!')

    print('Summary:')
    print(pulse_config)

    msg_highlight('Note:')
    print('You must restart PulseAudio if you changed and of the PulseAudio settings (equalizer, mono mixer, system default')
    print('You must always restart the Jukebox Service for changes to take effect.')
    print('Do this also even if you want to re-run this tool right now!')
    print('$ systemctl --user restart pulseaudio')
    print('$ systemctl --user restart jukebox-daemon\n')


def main():
    # Get absolute path of this script
    script_path = os.path.abspath(os.path.dirname(os.path.realpath(__file__)))
    default_cfg_jukebox = os.path.abspath(os.path.join(script_path, '../../shared/settings/jukebox.yaml'))
    default_cfg_pulse = os.path.abspath(os.path.expanduser('~/.config/pulse/default.pa'))

    argparser = argparse.ArgumentParser(description='The Jukebox audio configuration tool')
    argparser.add_argument('-j', '--jukebox', type=argparse.FileType('r'), default=default_cfg_jukebox,
                           help=f"Jukebox configuration file [default: '{default_cfg_jukebox}'",
                           metavar="FILE")
    argparser.add_argument('-p', '--pulseaudio', default=default_cfg_pulse,
                           help=f"PulseAudio configuration file [default: '{default_cfg_pulse}'",
                           metavar="FILE")
    argparser.add_argument('-n', '--ro_pulse', default=False, action='store_true',
                           help='Do not touch PulseAudio configuration file (e.g. in case of already perfect custom config)')
    argparser.add_argument('-f', '--full', default=False, action='store_true',
                           help='Show full, unfiltered list of sinks for secondary output')
    args = argparser.parse_args()

    pulse_config = PaConfigClass(jukebox_cfg_file=os.path.abspath(os.path.expanduser(args.jukebox.name)),
                                 pulse_cfg_file=os.path.abspath(os.path.expanduser(args.pulseaudio)),
                                 script_path=script_path,
                                 treat_pulse_as_readonly=args.ro_pulse,
                                 full_secondary_list=args.full)

    welcome(pulse_config)

    if host.is_any_jukebox_service_active():
        msg_highlight('Jukebox service is running!')
        print("\nPlease stop jukebox-daemon service and restart tool")
        print("$ systemctl --user stop jukebox-daemon\n\n")
        print("Don't forget to start the service again :-)")
        return

    pulse_config = query_sinks(pulse_config)
    pulse_config = configure_pulseaudio(pulse_config)
    pulse_config = configure_jukebox(pulse_config)
    goodbye(pulse_config)


if __name__ == '__main__':
    main()
