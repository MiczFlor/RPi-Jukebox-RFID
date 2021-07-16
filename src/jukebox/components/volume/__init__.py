import logging
import jukebox.plugin as plugin
import jukebox.cfghandler

logger = logging.getLogger('jb.volume')
cfg = jukebox.cfghandler.get_handler('jukebox')


@plugin.register
class VolumeFactory:

    def __init__(self):
        self._builders = {}

    def register(self, key, builder):
        logger.debug(f"Register '{key}' in {self.__class__}")
        self._builders[key] = builder

    def get(self, key):
        return self._builders.get(key)()

    def list(self):
        return self._builders.keys()

    def set_active(self, key):
        logger.debug("Set active '{key}' in VolumeFactory")
        # plugin.replace(self.get(key), module_name="volume", obj_name="ctrl")
        plugin.register(self.get(key), module="volume", name="ctrl", replace=True)


factory = None


def initialize():
    global factory
    logger.debug("Initialize ...")
    factory = VolumeFactory(plugin_name='factory')


def finalize():
    logger.debug("------------------- Finalize ...")
    interface_name = cfg.getn('volume', 'interface', default=None)
    if interface_name is not None:
        factory.set_active(interface_name)


