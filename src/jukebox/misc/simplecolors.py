"""
Zero 3rd-party dependency module to add colors to unix terminal output

Yes, there are modules out there to do the same and they have more features.
However, this is low-complexity and has zero dependencies
"""
import sys
import builtins


class Colors:
    """
    Container class for all the colors as constants
    """
    reset = '\033[0m'
    bold = '\033[01m'
    black = '\033[30m'
    red = '\033[31m'
    green = '\033[32m'
    orange = '\033[33m'
    blue = '\033[34m'
    purple = '\033[35m'
    cyan = '\033[36m'
    lightgrey = '\033[37m'
    darkgrey = '\033[90m'
    lightred = '\033[91m'
    lightgreen = '\033[92m'
    yellow = '\033[93m'
    lightblue = '\033[94m'
    pink = '\033[95m'
    lightcyan = '\033[96m'


# Convenience for easier iteration over colors
COLORS = {k: v for k, v in Colors.__dict__.items() if not k.startswith("__")}


def resolve(color_name: str):
    """
    Resolve a color name into the respective color constant

    :param color_name: Name of the color
    :return: color constant
    """
    return Colors.__dict__[color_name]


def print(color: Colors, *values, sep=' ', end='\n', file=sys.stdout, flush=False):
    """
    Drop-in replacement for print with color choice and auto color reset for convenience

    Use just as a regular print function, but with first parameter as color
    """
    return builtins.print(color, *values, Colors.reset, sep=sep, end=end, file=file, flush=flush)
