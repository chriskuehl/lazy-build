import pytest

from lazy_build import util


def test_atomic_write(tmpdir):
    a = tmpdir.join('a')
    a.write('sup')
    with util.atomic_write(a.strpath) as f:
        f.write('lol')
    assert a.read() == 'lol'


def test_atomic_write_exception(tmpdir):
    a = tmpdir.join('a')
    a.write('sup')
    with pytest.raises(ValueError):
        with util.atomic_write(a.strpath) as f:
            f.write('lol')
            f.flush()
            raise ValueError('sorry buddy')
    assert a.read() == 'sup'
