import argparse
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


def build(conf, args):
    ctx = context.build_context(conf, args.command)

    if args.verbose:
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


def invalidate(conf, args):
    raise NotImplementedError()


ACTIONS = {
    'build': build,
    'invalidate': invalidate,
}


def main(argv=None):
    parser = argparse.ArgumentParser(
        description='Cache build artifacts based on files on disk.',
    )
    parser.add_argument(
        '--context', nargs='+', required=True,
        help='file or directory to include in the build context',
    )
    parser.add_argument(
        '--ignore', nargs='+', required=False,
        help='paths to exclude when creating the build context',
    )
    parser.add_argument(
        '--output', nargs='+', required=True,
        help='file or directory to consider as output from a successful build',
    )
    parser.add_argument(
        '--after-download',
        help=(
            'command to run after downloading an artifact '
            '(for example, to adjust shebangs for the new path)'
        ),
    )
    parser.add_argument(
        '--dry-run', default=False, action='store_true',
        help='say what would be done, without doing it',
    )
    parser.add_argument(
        '--verbose', '-v', default=False, action='store_true',
    )
    parser.add_argument(
        '--action', choices=ACTIONS.keys(), required=True,
        help='action to take',
    )
    parser.add_argument(
        'command', nargs=argparse.REMAINDER,
        help='build command to execute',
    )

    args = parser.parse_args(argv)

    # TODO: is there a way we can get argparse to do this for us?
    if args.command[0] != '--':
        raise ValueError(
            'You must separate the command from the other arguments with a --!',  # noqa
        )

    del args.command[0]
    if len(args.command) == 0:
        raise ValueError('You must specify a command!')

    conf = config.Config.from_args(args)
    return ACTIONS[args.action](conf, args)
