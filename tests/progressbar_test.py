import contextlib
import sys
from unittest import mock

import pytest

from lazy_build import progressbar


ONE_MB = 2**20


@contextlib.contextmanager
def terminal_width(width):
    with mock.patch.object(
            progressbar.shutil,
            'get_terminal_size',
            return_value=mock.Mock(columns=width),
    ):
        yield


@contextlib.contextmanager
def mock_time(t):
    with mock.patch.object(progressbar.time, 'time', return_value=t):
        yield


@pytest.mark.parametrize(('b', 'expected'), (
    (0, ('B ', 1)),
    (1, ('B ', 1)),
    (2000, ('KB', 1024)),
    (2000000, ('MB', 1048576)),
    (2000000000, ('GB', 1073741824)),
    (2000000000000, ('TB', 1099511627776)),
    (2000000000000000, ('TB', 1099511627776)),
))
def test_best_unit(b, expected):
    assert progressbar.best_unit(b) == expected


@pytest.mark.parametrize(('cur', 'total', 'speed', 'width', 'expected'), (
    (
        0, 1, 0, 40,
        '\r[>           ] 0.0B  / 1.0B  |   0.0B /s',
    ),
    (
        300 * ONE_MB, 2000 * ONE_MB, 1.5 * ONE_MB, 40,
        '\r[=>          ] 0.3GB / 2.0GB |   1.5MB/s',
    ),
    (
        2000 * ONE_MB, 2000 * ONE_MB, 25000 * ONE_MB, 40,
        '\r[===========>] 2.0GB / 2.0GB |  24.4GB/s',
    ),

    # window too small
    (
        2000 * ONE_MB, 2000 * ONE_MB, 25000 * ONE_MB, 5,
        '',
    ),
))
def test_progressbar(cur, total, speed, width, expected):
    with terminal_width(width):
        assert progressbar.progressbar(
            cur, total, speed,
            file=mock.Mock(**{'isatty.return_value': True}),
        ) == expected


def test_progressbar_not_a_tty():
    with terminal_width(80):
        assert progressbar.progressbar(
            0, 100, 100,
            file=mock.Mock(**{'isatty.return_value': False}),
        ) == ''


def test_progress_manager(capsys):
    with terminal_width(40):
        with mock.patch.object(sys.stderr, 'isatty', return_value=True):
            with progressbar.Progress(5 * ONE_MB) as pb:
                with mock_time(100):
                    pb(0)
                with mock_time(101):
                    pb(10)
                with mock_time(107):
                    pb(ONE_MB)
                with mock_time(108):
                    pb(4 * ONE_MB)

    out, err = capsys.readouterr()
    assert err == (
        '\r[>           ] 0.0MB / 5.0MB |   0.0B /s'
        '\r[>           ] 0.0MB / 5.0MB |  10.0B /s'
        '\r[==>         ] 1.0MB / 5.0MB | 146.3KB/s'
        '\r[===========>] 5.0MB / 5.0MB |   4.0MB/s'
        '\n'
    )
