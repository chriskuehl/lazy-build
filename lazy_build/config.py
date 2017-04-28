import collections
import json
import re

from lazy_build import cache


def read_config():
    # TODO: should have some slightly nicer error messages here
    with open('.lazy-build.json') as f:
        return json.load(f)


class UsageError(Exception):
    pass


class Config(collections.namedtuple('Config', (
    'action',
    'dry_run',
    'verbose',
    'context',
    'command',
    'ignore',
    'output',
    'backend',
    'after_download',
))):

    __slots__ = ()

    @classmethod
    def from_args(cls, args):
        """Return a config based on arguments and the config file.

        The interface looks like this:

            lazy-build [flags] {action} \
                option= ... \
                option= ... \
                command= ...

        "command" is special and must come last. All of its arguments are
        accepted verbatim.

        Phase 0: flags and action
        Phase 1: trailing equal
        Phase 2: final trailing equal (command)
        """

        flags = set()
        options = {
            'context': [],
            'ignore': [],
            'output': [],
            'after-download': [],
            'command': [],
        }
        toggles = {
            'dry-run': False,
            'verbose': False,
        }
        phase = 0
        action = None
        current_option = None

        for arg in args:
            parsed = re.match('([a-z\-]+)=$', arg)
            if phase == 0:
                if parsed is None:
                    if arg.startswith('-'):
                        flags.add(arg)
                    elif action is None:
                        action = arg
                    else:
                        raise UsageError(
                            f'You already specified an action: {action}\n'
                            f"You can't specify another: {arg}"
                        )
                else:
                    if action is None:
                        raise UsageError(
                            'You must specify an action before any long options.',  # noqa
                        )
                    else:
                        current_option = parsed.group(1)
                        phase = 1
                        if current_option not in options:
                            raise UsageError(
                                f'Unknown option: {current_option}',
                            )
            elif phase == 1:
                if parsed is not None:
                    current_option = parsed.group(1)
                    if current_option not in options:
                        raise UsageError(
                            f'Unknown option: {current_option}',
                        )
                    elif current_option == 'command':
                        phase = 2
                else:
                    options[current_option].append(arg)
            elif phase == 2:
                options[current_option].append(arg)
            else:
                raise AssertionError('Got lost parsing arguments...')

        # handle flags
        def remove(s1, s2):
            matches = s1 & s2
            s1 -= s2
            return matches

        if remove(flags, {'--help', '-h'}):
            action = 'help'

        if remove(flags, {'--verbose', '-v'}):
            toggles['verbose'] = True

        if remove(flags, {'--dry-run'}):
            toggles['dry-run'] = True

        if flags:
            raise UsageError(
                'Unknown flags: {}'.format(', '.join(sorted(flags))),
            )

        if action is None:
            raise UsageError('You must provide an action')

        # read config file and merge the two
        conf = read_config()
        conf_ignore = conf.get('ignore') or ()
        conf_ignore = frozenset(conf_ignore)

        if conf['cache']['source'] == 's3':
            backend = cache.S3Backend(
                bucket=conf['cache']['bucket'],
                path=conf['cache']['path'],
            )
        elif conf['cache']['source'] == 'filesystem':
            backend = cache.FilesystemBackend(
                path=conf['cache']['path'],
            )
        else:
            raise AssertionError('Unknown cache source')

        return cls(
            action=action,
            dry_run=toggles['dry-run'],
            verbose=toggles['verbose'],
            context=frozenset(options['context']),
            command=tuple(options['command']),
            ignore=frozenset(options['ignore']) | conf_ignore,
            output=frozenset(options['output']),
            backend=backend,
            after_download=tuple(options['after-download']),
        )
