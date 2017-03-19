import json
import os
import shlex
import subprocess
import sys

from lazy_build import color
from lazy_build import config
from lazy_build import context


def log(line, **kwargs):
    kwargs.setdefault('file', sys.stderr)
    kwargs.setdefault('flush', True)
    print('{}'.format(line), **kwargs)


def build(conf):
    ctx = context.build_context(conf)

    if conf.verbose:
        log('Generated build context with hash {}'.format(ctx.hash))
        log('Individual files:')
        log(json.dumps(ctx.files, indent=True, sort_keys=True))

    if conf.backend.has_artifact(ctx):
        log(color.bg_gray('Found remote build artifact, downloading.'))
        return build_from_artifact(conf, ctx)
    else:
        log(color.bg_gray('Found no remote build artifact, building locally.'))
        return build_from_command(conf, ctx)


def build_from_artifact(conf, ctx):
    log(color.yellow('Downloading artifact...'), end=' ')
    artifact = conf.backend.get_artifact(ctx)
    log(color.yellow('done!'))
    try:
        log(color.yellow('Extracting artifact...'), end=' ')
        context.extract_artifact(conf, artifact)
        log(color.yellow('done!'))
    finally:
        os.remove(artifact)
    if conf.after_download:
        log(color.yellow('Running after-download script...'))
        log(color.yellow('$ ' + conf.after_download))
        # TODO: let's use trailing equal syntax so we can avoid this?
        subprocess.check_call(shlex.split(conf.after_download))
        log(color.yellow('done!'))


def build_from_command(conf, ctx):
    log(color.yellow('$ ' + ' '.join(shlex.quote(arg) for arg in ctx.command)))
    subprocess.check_call(ctx.command)
    log(color.yellow('Packaging artifact...'), end=' ')
    path = context.package_artifact(conf)
    log(color.yellow('done!'))
    try:
        log(color.yellow('Uploading artifact to shared cache...'), end=' ')
        conf.backend.store_artifact(ctx, path)
        log(color.yellow('done!'))
    finally:
        os.remove(path)


def invalidate(conf):
    raise NotImplementedError()


ACTIONS = {
    'build': build,
    'invalidate': invalidate,
}


def main(argv=None):
    conf = config.Config.from_args(argv or sys.argv[1:])
    return ACTIONS[conf.action](conf)
