# -*- coding: utf-8 -*-
from __future__ import absolute_import
from __future__ import unicode_literals

import collections


class Config(collections.namedtuple('Config', (
    'context',
    'ignore',
    'cache',
))):

    __slots__ = ()

    @classmethod
    def from_args(cls, args):
        # TODO: this method should also consider config files

        # TODO: this
        cache = CacheConfigS3(
            bucket='my-cool-bucket',
            path='/',
        )

        return cls(
            context=frozenset(args.context or ()),
            ignore=frozenset(args.ignore or ()),
            cache=cache,
        )


CacheConfigS3 = collections.namedtuple('CacheConfigS3', (
    'bucket',
    'path',
))
