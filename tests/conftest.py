from unittest import mock

import pytest

from lazy_build import config


@pytest.fixture
def simple_config():
    return config.Config(
        action='build',
        dry_run=False,
        verbose=False,
        context={'venv'},
        command=('touch venv'),
        ignore={'*.py[co]'},
        output={'venv'},
        backend=mock.Mock(),
        after_download=(),
    )
