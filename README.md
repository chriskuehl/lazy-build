# lazy-build

[![Build Status](https://travis-ci.org/chriskuehl/lazy-build.svg?branch=master)](https://travis-ci.org/chriskuehl/lazy-build)
[![Coverage Status](https://coveralls.io/repos/github/chriskuehl/lazy-build/badge.svg?branch=master)](https://coveralls.io/github/chriskuehl/lazy-build?branch=master)
[![PyPI version](https://badge.fury.io/py/lazy-build.svg)](https://pypi.python.org/pypi/lazy-build)

Cache build artifacts based on files on disk.


## Interface
### Building

```bash
$ lazy-build \
    --context requirements*.txt \
    --context setup.py \
    --context /etc/lsb_release \
    --output venv \
    --after-download venv/bin/python -m virtualenv_tools --update-path {pwd}/venv venv \
    build -- \
    bash -euxc 'virtualenv -ppython3 venv && venv/bin/pip install -r requirements.txt'
```


### Invalidating artifacts

`lazy-build invalidate` takes all of the same arguments as `lazy-build build`.
It builds up the context, then deletes the artifact matching it.

```bash
$ lazy-build
    --context requirements*.txt \
    --context setup.py \
    --context /etc/lsb_release \
    --output venv \
    --after-download venv/bin/python -m virtualenv_tools --update-path {pwd}/venv venv \
    invalidate -- \
    bash -euxc 'virtualenv -ppython3 venv && venv/bin/pip install -r requirements.txt'
```

Ideally it would have an option to mark that the artifact should *not* be
used/re-uploaded again, in cases where something might be broken with the
generated artifacts. This could be used as an off-switch until fixes can be
made.


### The config file

Located as `.lazy-build.yaml` at the root of your project.

```yaml
cache:
    source: s3
    bucket: my-cool-bucket
    path: cache/my-cool-service

ignore: [
    '*.py[co]',
    '*~',
    '.*.sw*',
    '.DS_Store',
    '.nfs*',
]
```
