from GPIODevices import TwoButtonControl, RotaryEncoder
# from gpio_control import logger, getFunctionCall


class VolumeControl:
    def __new__(self, config, getFunctionCall, logger):
        if config.get('Type') == 'TwoButtonControl':
            logger.info('VolumeControl as TwoButtonControl')
            return TwoButtonControl(
                config.getint('Pin1'),
                config.getint('Pin2'),
                getFunctionCall(config.get('functionCall1')),
                getFunctionCall(config.get('functionCall2')),
                functionCallTwoBtns=getFunctionCall(config.get('functionCallTwoButtons')),
                pull_up_down=config.get('pull_up_down', fallback='pull_up'),
                hold_mode=config.get('hold_mode', fallback='Repeat'),
                hold_time=config.getfloat('hold_time', fallback=0.3),
                bouncetime=config.getint('bouncetime', fallback=500),
                edge=config.get('edge', fallback='falling'),
                antibouncehack=config.getboolean('antibouncehack', fallback=False),
                name='VolumeControl'
            )
        elif config.get('Type') == 'RotaryEncoder':
            return RotaryEncoder(
                config.getint('pinUp'),
                config.getint('pinDown'),
                getFunctionCall(config.get('functionCallUp')),
                getFunctionCall(config.get('functionCallDown')),
                config.getfloat('timeBase', fallback=0.1),
                name='RotaryVolumeControl')
