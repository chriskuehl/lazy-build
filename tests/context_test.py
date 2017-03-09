# -*- coding: utf-8 -*-
from __future__ import absolute_import
from __future__ import unicode_literals

import pytest

from lazy_build import config
from lazy_build import context


@pytest.mark.parametrize(('patterns', 'path'), (
    ({'/venv'}, 'venv'),
    ({'venv'}, 'venv'),
    ({'venv'}, 'this/is/some/venv'),
    ({'venv'}, 'this/is/some/venv/with/a/file'),
    ({'venv/with'}, 'this/is/some/venv/with/a/file'),
    ({'*.swp'}, 'something.swp'),
    ({'*.swp'}, 'hello/there/something.swp'),
))
def test_should_ignore_true(patterns, path):
    assert context.should_ignore(patterns, path) is True


@pytest.mark.parametrize(('patterns', 'path'), (
    ({'/venv'}, 'this/is/some/venv'),
    ({'a/venv'}, 'this/is/some/venv'),
    ({'venv'}, 'venv2'),
))
def test_should_ignore_false(patterns, path):
    assert context.should_ignore(patterns, path) is False


def test_build_context_simple(tmpdir):
    tmpdir.chdir()
    conf = config.Config(
        context={tmpdir.strpath, tmpdir.join('a').strpath},
        ignore={'d'},
        cache=None,
    )
    tmpdir.join('a').write(b'foo')
    tmpdir.join('b').mkdir()
    tmpdir.join('b/c').write(b'bar')
    tmpdir.join('d').mkdir()
    tmpdir.join('d/e').write(b'baz')
    tmpdir.join('f').mksymlinkto('/etc/passwd')
    assert context.build_context(conf) == context.BuildContext(files={
        'a': context.FileContext('file', context.hash(b'foo')),
        'b/c': context.FileContext('file', context.hash(b'bar')),
        'f': context.FileContext('link', context.hash(b'/etc/passwd')),
    })
