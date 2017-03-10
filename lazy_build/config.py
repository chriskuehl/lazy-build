import collections

from lazy_build import cache


class Config(collections.namedtuple('Config', (
    'context',
    'ignore',
    'output',
    'backend',
))):

    __slots__ = ()

    @classmethod
    def from_args(cls, args):
        # TODO: this method should also consider config files

        # TODO: this
        backend = cache.S3Backend(
            bucket='some-bucket',
            path='ckuehl/lazy-build/',
        )

        return cls(
            context=frozenset(args.context),
            ignore=frozenset(args.ignore or ()),
            output=frozenset(args.output),
            backend=backend,
        )
