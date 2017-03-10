import collections
import json

from lazy_build import cache


def read_config():
    # TODO: should have some slightly nicer error messages here
    with open('.lazy-build.json') as f:
        return json.load(f)


class Config(collections.namedtuple('Config', (
    'context',
    'ignore',
    'output',
    'backend',
    'after_download',
))):

    __slots__ = ()

    @classmethod
    def from_args(cls, args):
        conf = read_config()
        conf_ignore = conf.get('ignore') or ()
        conf_ignore = frozenset(conf_ignore)

        if conf['cache']['source'] == 's3':
            backend = cache.S3Backend(
                bucket=conf['cache']['bucket'],
                path=conf['cache']['path'],
            )
        else:
            raise AssertionError('Unknown cache source')

        return cls(
            context=frozenset(args.context),
            ignore=frozenset(args.ignore or ()) | conf_ignore,
            output=frozenset(args.output),
            backend=backend,
            after_download=args.after_download,
        )
