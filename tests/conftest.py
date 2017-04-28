import pytest

from lazy_build import cache
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
        backend=cache.FilesystemBackend(path='cache'),
        after_download=(),
    )
