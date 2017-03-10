from unittest import mock

from lazy_build import config


def test_from_args():
    conf = config.Config.from_args(mock.Mock(
        context=['requirements.txt', 'setup.py'],
        ignore=['*.py[co]', '*.swp'],
        output=['venv', 'node_modules'],
    ))
    assert conf.context == {'requirements.txt', 'setup.py'}
    assert conf.ignore == {'*.py[co]', '*.swp'}
    assert conf.output == {'venv', 'node_modules'}
    # TODO: make some assertions about the backend
