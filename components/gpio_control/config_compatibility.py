#!/usr/bin/env python3
import configparser
import os
from shutil import copyfile

def Ini_CheckAndUpgrade(config):
    has_changed = False
    for section in config.sections():
        # enable: True  --> enabled: True
        # enable: False --> enabled: False
        if config.has_option(section, 'enable'):
            v = config.getboolean(section, 'enable', fallback=False)
            config.remove_option(section, 'enable')
            has_changed = True
            if not config.has_option(section, 'enabled'):
                config.set(section, 'enabled', 'True' if v else 'False')
        # pull_up: True  --> pull_up_down: pull_up
        # pull_up: False --> pull_up_down: pull_off
        if config.has_option(section, 'pull_up'):
            v = config.getboolean(section, 'pull_up', fallback=True)
            config.remove_option(section, 'pull_up')
            has_changed = True
            if not config.has_option(section, 'pull_up_down'):
                config.set(section, 'pull_up_down', 'pull_up' if v else 'pull_off')
        # hold_repeat: True --> hold_mode: Repeat
        # hold_repeat: False --> hold_mode: None
        if config.has_option(section, 'hold_repeat'):
            v = config.getboolean(section, 'hold_repeat', fallback=False)
            config.remove_option(section, 'hold_repeat')
            has_changed = True
            if not config.has_option(section, 'hold_mode'):
                config.set(section, 'hold_mode', 'Repeat' if v else 'None')
        # time_pressed <float> --> hold_time <float>
        if config.has_option(section, 'time_pressed'):
            v = config.getfloat(section, 'time_pressed')
            config.remove_option(section, 'time_pressed')
            has_changed = True
            if not config.has_option(section, 'hold_time'):
                config.set(section, 'hold_time', str(v))
        #PinUp: <int> --> Pin1 <int>
        #PinDown: <int> --> Pin2 <int>
        if config.has_option(section, 'PinUp'):
            v = config.getint(section, 'PinUp')
            config.remove_option(section, 'PinUp')
            has_changed = True
            if not config.has_option(section, 'Pin1'):
                config.set(section, 'Pin1', str(v))
        if config.has_option(section, 'PinDown'):
            v = config.getint(section, 'PinDown')
            config.remove_option(section, 'PinDown')
            has_changed = True
            if not config.has_option(section, 'Pin2'):
                config.set(section, 'Pin2', str(v))
        # functionCallUp <String> --> functionCall1  <String>
        # functionCallDown <String> --> functionCall2  <String>
        if config.has_option(section, 'functionCallUp'):
            v = config.get(section, 'functionCallUp')
            config.remove_option(section, 'functionCallUp')
            has_changed = True
            if not config.has_option(section, 'functionCall1'):
                config.set(section, 'functionCall1', v)
        if config.has_option(section, 'functionCallDown'):
            v = config.get(section, 'functionCallDown')
            config.remove_option(section, 'functionCallDown')
            has_changed = True
            if not config.has_option(section, 'functionCall2'):
                config.set(section, 'functionCall2', v)

    return has_changed
    
    
def ConfigCompatibilityChecks(config, config_path):
    # Check for deprecated settings in gpio_settings.ini
    if not Ini_CheckAndUpgrade(config):
        return
    
    # If we reach here, gpio_settings.ini needed some patching...

    # Try creating a backup of the previous ini file
    backup_path = config_path+'.bak'
    if os.path.isfile(backup_path):
        return
    copyfile(config_path, backup_path)

    # Save fixed gpio_settings.ini
    with open(config_path, 'w') as inifile:
        config.write(inifile)
