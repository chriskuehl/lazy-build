"""Stolen from ocflib.misc.shell"""
import sys

# terminal text color wrappers;
# this is pretty ugly, but defining them manually lets us avoid hacking flake8


def _wrap_colors(color, reset):
    """Create functions like red('hello') and bg_red('hello') for wrapping
    strings in ANSI color escapes.
    >>> red('hello')
    '\x1b[31mhello\x1b[39m'
    """
    def wrapper(string, tty_only=True):
        """Return colorized string.
        Takes an optional tty_only argument (defaults to True). When tty_only
        is set, colors will only be applied if stdout is a tty.  This is useful
        when you don't want color output (e.g. if redirecting to a file).
        """
        if tty_only and not sys.stdout.isatty():
            return string
        return '{color}{string}{reset}'.format(
            color=color,
            string=string,
            reset=reset,
        )
    return wrapper


# Define ANSI color codes
FG_COLORS = {
    'black': 30,
    'red': 31,
    'green': 32,
    'yellow': 33,
    'blue': 34,
    'magenta': 35,
    'cyan': 36,
    'white': 37,
    'reset': 39,
    'gray': 90,
}

BG_COLORS = {k: v + 10 for k, v in FG_COLORS.items()}


def code_to_chars(code):
    """Convert each numeric code to its corresponding characters"""
    return '\033[' + str(code) + 'm'


FG_CODES = {k: code_to_chars(v) for k, v in FG_COLORS.items()}
BG_CODES = {k: code_to_chars(v) for k, v in BG_COLORS.items()}


black = _wrap_colors(FG_CODES['black'], FG_CODES['reset'])
bg_black = _wrap_colors(BG_CODES['black'], BG_CODES['reset'])

red = _wrap_colors(FG_CODES['red'], FG_CODES['reset'])
bg_red = _wrap_colors(BG_CODES['red'], BG_CODES['reset'])

green = _wrap_colors(FG_CODES['green'], FG_CODES['reset'])
bg_green = _wrap_colors(BG_CODES['green'], BG_CODES['reset'])

yellow = _wrap_colors(FG_CODES['yellow'], FG_CODES['reset'])
bg_yellow = _wrap_colors(BG_CODES['yellow'], BG_CODES['reset'])

blue = _wrap_colors(FG_CODES['blue'], FG_CODES['reset'])
bg_blue = _wrap_colors(BG_CODES['blue'], BG_CODES['reset'])

magenta = _wrap_colors(FG_CODES['magenta'], FG_CODES['reset'])
bg_magenta = _wrap_colors(BG_CODES['magenta'], BG_CODES['reset'])

cyan = _wrap_colors(FG_CODES['cyan'], FG_CODES['reset'])
bg_cyan = _wrap_colors(BG_CODES['cyan'], BG_CODES['reset'])

white = _wrap_colors(FG_CODES['white'], FG_CODES['reset'])
bg_white = _wrap_colors(BG_CODES['white'], BG_CODES['reset'])

gray = _wrap_colors(FG_CODES['gray'], FG_CODES['reset'])
bg_gray = _wrap_colors(BG_CODES['gray'], BG_CODES['reset'])

bold = _wrap_colors('\033[1m', '\033[0m')
