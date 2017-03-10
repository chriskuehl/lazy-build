import collections
import fnmatch
import hashlib
import itertools
import json
import os
import os.path
import shutil
import tarfile
import tempfile


def hash(data):
    return hashlib.sha256(data).hexdigest()


class BuildContext(collections.namedtuple('BuildContext', (
    'command',
    'files',
))):

    __slots__ = ()

    @property
    def hash(self):
        return hash(json.dumps(
            (self.command, self.files),
            sort_keys=True,
        ).encode('utf8'))


class FileContext(collections.namedtuple('FileContext', (
    'type',
    'content_hash',
))):

    __slots__ = ()

    @classmethod
    def from_path(cls, path):
        assert os.path.lexists(path), path

        if os.path.islink(path):
            return cls(
                'link',
                hash(os.readlink(path).encode('utf8', 'surrogateescape')),
            )
        else:
            with open(path, 'rb') as f:
                return cls('file', hash(f.read()))


def should_ignore(patterns, path):
    """gitignore-like pattern matching"""
    path = '/' + path

    # We need to get all "substring" paths, e.g. for a/b/c we need:
    # a; a/b; a/b/c; b; b/c; c
    components = path.split('/')
    paths = {
        '/'.join(components[i:j + 1])
        for i in range(len(components))
        for j in range(len(components))
    }

    return any(
        fnmatch.fnmatch(path, pattern)
        for path, pattern in itertools.product(paths, patterns)
    )


def build_context(conf, command):
    ctx = {}
    fringe = {
        os.path.relpath(os.path.realpath(path)) for path in conf.context
    }
    explored = set()

    while len(fringe) > 0:
        path = fringe.pop()
        explored.add(path)

        if should_ignore(conf.ignore, path):
            continue

        if os.path.isdir(path) and not os.path.islink(path):
            for child in os.listdir(path):
                child = os.path.relpath(os.path.join(path, child))
                fringe.add(child)
        else:
            ctx[path] = FileContext.from_path(path)

    return BuildContext(command=command, files=ctx)


def package_artifact(conf):
    fd, tmp = tempfile.mkstemp()
    os.close(fd)
    with tarfile.open(tmp, mode='w:gz') as tf:
        for output_path in conf.output:
            if os.path.isdir(output_path):
                for path, _, filenames in os.walk(output_path):
                    for filename in filenames:
                        tf.add(os.path.join(path, filename))
            else:
                tf.add(output_path)
    return tmp


def extract_artifact(conf, artifact):
    for output_path in conf.output:
        if os.path.lexists(output_path):
            if os.path.isdir(output_path) and not os.path.islink(output_path):
                shutil.rmtree(output_path)
            else:
                os.remove(output_path)

    with tarfile.open(artifact, 'r:gz') as tf:
        tf.extractall()
