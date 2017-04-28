import contextlib
import os
import os.path
import tempfile


@contextlib.contextmanager
def atomic_write(path, mode='w'):
    tmp = tempfile.mktemp(
        prefix='.' + os.path.basename(path),
        dir=os.path.dirname(path),
    )
    try:
        with open(tmp, mode) as f:
            yield f
    except:
        os.remove(tmp)
        raise
    else:
        os.rename(tmp, path)


def copyfileobj(src, dest, callback):
    """Copy from one file object to another.

    Based on shutil.copyfileobj, but with a callback.
    """
    while True:
        buf = src.read(16 * 1024)
        if not buf:
            break
        callback(len(buf))
        dest.write(buf)
