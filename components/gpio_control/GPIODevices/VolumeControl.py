from GPIODevices import TwoButtonControl, RotaryEncoder
#from gpio_control import logger, getFunctionCall


class VolumeControl:
    def __new__(self, config,getFunctionCall,logger):
        if config.get('Type') == 'TwoButtonControl':
            logger.info('VolumeControl as TwoButtonControl')
            return TwoButtonControl(
                config.getint('pinUp'),
                config.getint('pinDown'),
                getFunctionCall(config.get('functionCallUp')),
                getFunctionCall(config.get('functionCallDown')),
                functionCallTwoBtns=getFunctionCall(config.get('functionCallTwoButtons')),
                pull_up=config.getboolean('pull_up', fallback=True),
                hold_repeat=config.getboolean('hold_repeat', fallback=True),
                hold_time=config.getfloat('hold_time', fallback=0.3),
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
