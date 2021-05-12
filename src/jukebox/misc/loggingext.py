import logging
import misc.simplecolors as sc


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
