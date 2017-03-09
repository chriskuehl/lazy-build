# -*- coding: utf-8 -*-
from __future__ import absolute_import
from __future__ import unicode_literals

import argparse
import json
import os
import subprocess

from lazy_build import config
from lazy_build import context


def build(conf, args):
    ctx = context.build_context(conf, args.command)

    if args.verbose:
        print('Generated build context with hash {}'.format(ctx.hash))
        print('Individual files:')
        print(json.dumps(ctx.files, indent=True, sort_keys=True))

    if conf.backend.has_artifact(ctx):
        print('[lazy-build] found pre-existing build artifact')
        return build_from_artifact(conf, ctx)
    else:
        print('[lazy-build] found no build artifact')
        return build_from_command(conf, ctx)


def build_from_artifact(conf, ctx):
    artifact = conf.backend.get_artifact(ctx)
    try:
        context.extract_artifact(conf, artifact)
    finally:
        os.remove(artifact)


def build_from_command(conf, ctx):
    subprocess.check_call(ctx.command)
    path = context.package_artifact(conf)
    try:
        conf.backend.store_artifact(ctx, path)
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
            'You must separate the command from the other arguments with a --!',
        )

    del args.command[0]
    if len(args.command) == 0:
        raise ValueError('You must specify a command!')

    conf = config.Config.from_args(args)
    return ACTIONS[args.action](conf, args)
