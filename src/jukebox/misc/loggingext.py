"""
## Logger

We use a hierarchical Logger structure based on pythons logging module. It can be finely configured with a yaml file.

The top-level logger is called 'jb' (to make it short). In any module you may simple create a child-logger at any hierarchy
level below 'jb'. It will inherit settings from it's parent logger unless otherwise configured in the yaml file.
Hierarchy separator is the '.'. If the logger already exits, getLogger will return a reference to the same, else it will be
created on the spot.

Example: How to get logger and log away at your heart's content:

    >>> import logging
    >>> logger = logging.getLogger('jb.awesome_module')
    >>> logger.info('Started general awesomeness aura')

Example: YAML snippet, setting WARNING as default level everywhere and DEBUG for jb.awesome_module:

    loggers:
      jb:
        level: WARNING
        handlers: [console, debug_file_handler, error_file_handler]
        propagate: no
      jb.awesome_module:
        level: DEBUG


> [!NOTE]
> The name (and hierarchy path) of the logger can be arbitrary and must not necessarily match the module name (still makes
> sense).
> There can be multiple loggers per module, e.g. for special classes, to further control the amount of log output
"""
import sys
import logging
import logging.config
import logging.handlers
import jukebox.publishing as publishing
import misc.simplecolors as sc
from ruamel.yaml import YAML


class ColorFilter(logging.Filter):
    """
    This filter adds colors to the logger

    It adds all colors from simplecolors by using the color name as new keyword,
    i.e. use %(colorname)c or {colorname} in the formatter string

    It also adds the keyword {levelnameColored} which is an auto-colored drop-in replacement
    for the levelname depending on severity.

    Don't forget to {reset} the color settings at the end of the string.
    """
    def __init__(self, enable=True, color_levelname=True):
        """
        :param enable: Enable the coloring
        :param color_levelname: Enable auto-coloring when using the levelname keyword
        """
        super().__init__()
        self.enable = enable
        self.color_levelname = color_levelname
        self.colored_level = {'DEBUG': f'{sc.Colors.lightgreen}DEBUG   {sc.Colors.reset}',
                              'INFO': f'{sc.Colors.lightcyan}INFO    {sc.Colors.reset}',
                              'WARNING': f'{sc.Colors.yellow}WARNING {sc.Colors.reset}',
                              'ERROR': f'{sc.Colors.lightred}ERROR   {sc.Colors.reset}',
                              'CRITICAL': f'{sc.Colors.pink}CRITICAL{sc.Colors.reset}'}

    def filter(self, record):
        if self.enable:
            for color, code in sc.COLORS.items():
                record.__setattr__(color, code)
            if self.color_levelname:
                record.levelnameColored = self.colored_level[record.levelname]
            else:
                record.levelnameColored = record.levelname
        else:
            for color, code in sc.COLORS.items():
                record.__setattr__(color, '')
            record.levelnameColored = record.levelname
        return True


class PubStream:
    """
    Stream handler wrapper around the publisher for logging.StreamHandler

    Allows logging to send all log information (based on logging configuration)
    to the Publisher.

    > [!CAUTION]
    > This can lead to recursions!
    > Recursions come up when
    > * Publish.send / PublishServer.send also emits logs, which cause a another send, which emits a log,
    > which causes a send, .....
    > * Publisher initialization emits logs, which need a Publisher instance to send logs

    > [!IMPORTANT]
    > To avoid endless recursions: The creation of a Publisher MUST NOT generate any log messages! Nor any of the
    > functions in the send-function stack!
    """
    def __init__(self):
        self._topic = 'core.logger'
        self._message = ''

    def flush(self):
        publishing.get_publisher().send(self._topic, self._message.strip('\n '))
        self._message = ''

    def write(self, msg):
        self._message += msg


class PubStreamHandler(logging.StreamHandler):
    """Wrapper for logging.StreamHandler with stream = PubStream

    This serves one purpose: In logger.yaml custom handlers
    can be configured (which are automatically instantiated).
    Using this Handler, we can output to PubStream whithout
    support code to instantiate PubStream keeping this file generic"""
    def __init__(self):
        super().__init__(PubStream())


def configure_default(level=logging.DEBUG, name='jb', with_publisher=False):
    logger = logging.getLogger(name)
    logger.setLevel(level)
    console = logging.StreamHandler(sys.stdout)
    console.setLevel(level)
    formatter_color = logging.Formatter(
        fmt='{asctime} - {lineno:4}:{filename:18} - {name:20} - {threadName:15} - {levelnameColored:8} - '
            '{lightcyan}{message}{reset}',
        datefmt='%d.%m.%Y %H:%M:%S',
        style='{')
    console.addFilter(ColorFilter())
    console.setFormatter(formatter_color)
    logger.addHandler(console)
    if with_publisher:
        publisher = PubStreamHandler()
        publisher.setLevel(logging.WARNING)
        formatter_base = logging.Formatter(
            fmt='{asctime} - {lineno:4}:{filename:18} - {name:20} - {threadName:15} - {levelname:8} - '
                '{message}',
            datefmt='%d.%m.%Y %H:%M:%S',
            style='{')
        publisher.setFormatter(formatter_base)
        logger.addHandler(publisher)
    logger.info(f"Enabling default logger with level = {level} on console"
                + (" and level = WARNING on publisher" if with_publisher else ""))
    return logger


def configure_from_file(filename=None):
    if filename is None:
        return configure_default(level=logging.WARNING)
    yaml = YAML(typ='safe')
    try:
        with open(filename) as stream:
            cfg = yaml.load(stream)
        logging.config.dictConfig(cfg)
        logger = logging.getLogger('jb')
    except Exception as e:
        logger = configure_default(level=logging.DEBUG)
        logger.error(f"Using default fallback logger. Reason: while opening '{filename}' for logger configuration")
        logger.error(f"{e}")
    # This enforces a fresh file for all RotatingFileHandlers at start of application
    for h in logger.handlers:
        if isinstance(h, logging.handlers.RotatingFileHandler):
            h.doRollover()
    return logger
