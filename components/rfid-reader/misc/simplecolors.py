import sys


class colors:
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

    @staticmethod
    def print(color, *values, sep=' ', end='\n', file=sys.stdout, flush=False):
        print(color, *values, Colors.reset, sep=sep, end=end, file=file, flush=flush)
