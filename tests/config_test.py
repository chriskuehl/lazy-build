import json
from unittest import mock

import pytest

from lazy_build import config


@pytest.fixture
def with_config_file(tmpdir):
    tmpdir.chdir()
    tmpdir.join('.lazy-build.json').write(json.dumps({
        'cache': {
            'source': 's3',
            'bucket': 'my-cool-bucket',
            'path': 'some/path',
        },
        'ignore': [
            '.DS_Store',
        ],
    }))


@pytest.mark.parametrize(('args', 'expected'), (
    (
        (
            '--verbose',
            '--dry-run',
            'build',
            'context=', 'requirements.txt', 'setup.py',
            'ignore=', '*.py[co]', '*.swp',
            'output=', 'venv', 'node_modules',
            'after-download=', 'python', '-m', 'virtualenv_tools',
            'command=', 'venv-update', 'venv=', '-ppython2.7',
        ),
        config.Config(
            action='build',
            dry_run=True,
            verbose=True,
            context={'requirements.txt', 'setup.py'},
            command=('venv-update', 'venv=', '-ppython2.7'),
            ignore={'*.py[co]', '*.swp', '.DS_Store'},
            output={'venv', 'node_modules'},
            backend=mock.ANY,
            after_download=('python', '-m', 'virtualenv_tools'),
        ),
    ),
    (
        ('build',),
        config.Config(
            action='build',
            dry_run=False,
            verbose=False,
            context=set(),
            command=(),
            ignore={'.DS_Store'},
            output=set(),
            backend=mock.ANY,
            after_download=(),
        ),
    ),
    (
        ('--help',),
        config.Config(
            action='help',
            dry_run=False,
            verbose=False,
            context=set(),
            command=(),
            ignore={'.DS_Store'},
            output=set(),
            backend=mock.ANY,
            after_download=(),
        ),
    ),
))
def test_from_args(with_config_file, args, expected):
    assert config.Config.from_args(args) == expected


def test_from_args_multiple_actions(with_config_file):
    with pytest.raises(config.UsageError) as exc_info:
        config.Config.from_args(('build', 'invalidate'))
    assert exc_info.value.args == (
        'You already specified an action: build\n'
        "You can't specify another: invalidate",
    )


def test_from_args_no_action_before_long_args(with_config_file):
    with pytest.raises(config.UsageError) as exc_info:
        config.Config.from_args(('command=', 'invalidate'))
    assert exc_info.value.args == (
        'You must specify an action before any long options.',
    )


def test_from_args_unknown_option(with_config_file):
    with pytest.raises(config.UsageError) as exc_info:
        config.Config.from_args(('build', 'blah=', 'hello'))
    assert exc_info.value.args == ('Unknown option: blah',)


def test_from_args_unknown_second_option(with_config_file):
    with pytest.raises(config.UsageError) as exc_info:
        config.Config.from_args(('build', 'context=', 'hello', 'blah=', 'bar'))
    assert exc_info.value.args == ('Unknown option: blah',)


def test_from_args_bogus_flag(with_config_file):
    with pytest.raises(config.UsageError) as exc_info:
        config.Config.from_args(('build', '--yolo', '--wuddup'))
    assert exc_info.value.args == ('Unknown flags: --wuddup, --yolo',)


def test_from_args_no_action(with_config_file):
    with pytest.raises(config.UsageError) as exc_info:
        config.Config.from_args(())
    assert exc_info.value.args == ('You must provide an action',)
