import io
import json
import os
import tarfile

import pytest

from lazy_build import context


@pytest.mark.parametrize(('patterns', 'path'), (
    ({'/venv'}, 'venv'),
    ({'venv'}, 'venv'),
    ({'venv'}, 'this/is/some/venv'),
    ({'venv'}, 'this/is/some/venv/with/a/file'),
    ({'venv/with'}, 'this/is/some/venv/with/a/file'),
    ({'*.swp'}, 'something.swp'),
    ({'*.swp'}, 'hello/there/something.swp'),
    ({'.*.sw[a-z]'}, 'my/.thing.txt.swo'),
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


def test_build_context_simple(simple_config, tmpdir):
    tmpdir.chdir()
    conf = simple_config._replace(
        context={tmpdir.strpath, tmpdir.join('a').strpath},
        ignore={'d'},
        command=('command',),
    )
    tmpdir.join('a').write(b'foo')
    tmpdir.join('b').mkdir()
    tmpdir.join('b/c').write(b'bar')
    tmpdir.join('d').mkdir()
    tmpdir.join('d/e').write(b'baz')
    tmpdir.join('f').mksymlinkto('/etc/passwd')

    ctx = context.build_context(conf)
    assert ctx == context.BuildContext(
        files={
            'a': context.FileContext('file', context.hash(b'foo')),
            'b/c': context.FileContext('file', context.hash(b'bar')),
            'f': context.FileContext('link', context.hash(b'/etc/passwd')),
        },
        command=('command',),
    )
    assert ctx.hash == context.hash(
        json.dumps((('command',), ctx.files), sort_keys=True).encode('utf8'),
    )


def test_package_artifact(simple_config, tmpdir):
    tmpdir.chdir()
    tmpdir.join('a').ensure()
    tmpdir.join('b').mkdir()
    tmpdir.join('b/c').ensure()
    tmpdir.join('c').ensure()

    tmp = context.package_artifact(simple_config._replace(
        ignore={},
        output={'b', 'c'},
    ))
    try:
        with tarfile.open(tmp, 'r') as tf:
            members = {member.name for member in tf.getmembers()}
    finally:
        os.remove(tmp)

    assert members == {'b/c', 'c'}


def test_extract_artifact(simple_config, tmpdir):
    tmpdir.chdir()
    tmpdir.join('my.txt').write('this is not the text you are looking for')
    tmpdir.join('a').mkdir()
    tmpdir.join('a/b').mkdir()
    tmpdir.join('a/sup').ensure()
    tmpdir.join('a/b/sup').ensure()

    tar = tmpdir.join('my.tar').strpath
    with tarfile.open(tar, 'w') as tf:
        for path in ('my.txt', 'hello/there.txt', 'a/b/c/d.txt'):
            ti = tarfile.TarInfo(path)
            ti.size = 6
            tf.addfile(ti, fileobj=io.BytesIO(b'wuddup'))

    context.extract_artifact(simple_config._replace(
        output={'my.txt', 'hello', 'a/b'},
    ), tar)

    assert tmpdir.join('my.txt').read() == 'wuddup'
    assert tmpdir.join('hello/there.txt').isfile()
    assert tmpdir.join('a/b/c/d.txt').isfile()

    assert tmpdir.join('a/sup').isfile()
    assert not tmpdir.join('a/b/sup').isfile()
