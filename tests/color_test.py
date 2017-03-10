import sys
from unittest import mock

import pytest

import lazy_build.color


COLORS = (
    'black', 'red', 'green', 'yellow', 'blue', 'magenta', 'cyan', 'white',
)


@pytest.mark.parametrize('color', COLORS)
def test_color_wrappers_with_tty(color):
    with mock.patch.object(sys.stdout, 'isatty', return_value=True):
        fore = getattr(lazy_build.color, color)
        assert fore('hi') == fore('hi', tty_only=True)
        assert fore('hi') == (
            lazy_build.color.FG_CODES[color] +
            'hi' +
            lazy_build.color.FG_CODES['reset']
        )

        bg = getattr(lazy_build.color, 'bg_' + color)
        assert bg('hi') == bg('hi', tty_only=True)
        assert bg('hi') == (
            lazy_build.color.BG_CODES[color] +
            'hi' +
            lazy_build.color.BG_CODES['reset']
        )


@pytest.mark.parametrize('color', COLORS)
def test_color_wrappers_without_tty(color):
    with mock.patch('sys.stdout.isatty', return_value=False):
        fore = getattr(lazy_build.color, color)
        assert fore('hi') == 'hi'

        bg = getattr(lazy_build.color, 'bg_' + color)
        assert bg('hi') == 'hi'
