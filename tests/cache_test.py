import collections
import os
from unittest import mock

import botocore.exceptions
import pytest

from lazy_build import cache


class FakeS3:

    meta = mock.Mock()

    def __init__(self):
        self._buckets = collections.defaultdict(dict)

    def Object(self, bucket, key):
        return FakeS3Object(self._buckets[bucket], key)


class FakeS3Object:

    def __init__(self, bucket, key):
        self._bucket = bucket
        self._key = key

    def load(self):
        if self._key in self._bucket:
            self.content_length = len(self._bucket[self._key])
        else:
            raise botocore.exceptions.ClientError(
                {'Error': {'Code': '404'}},
                None,
            )


@pytest.fixture
def s3_backend():
    backend = cache.S3Backend(bucket='my-cool-bucket', path='artifacts')
    with mock.patch.object(cache.boto3, 'resource', return_value=FakeS3()):
        yield backend


def test_s3_artifact_details_exists(s3_backend):
    s3_backend._s3._buckets['my-cool-bucket']['artifacts/my-hash.tar'] = b'hi'
    assert (
        s3_backend.artifact_details(mock.Mock(hash='my-hash')) ==
        cache.ArtifactDetails(size=2)
    )


def test_s3_artifact_details_does_not_exist(s3_backend):
    assert (
        s3_backend.artifact_details(mock.Mock(hash='my-hash')) is
        None
    )


def test_s3_artifact_get_artifact(s3_backend):
    s3_backend._s3._buckets['my-cool-bucket']['artifacts/my-hash.tar'] = b'hi'
    callback = mock.Mock()
    path = s3_backend.get_artifact(mock.Mock(hash='my-hash'), callback)
    assert path.startswith('/tmp/')
    s3_backend._s3.meta.client.download_file.assert_called_once_with(
        'my-cool-bucket',
        'artifacts/my-hash.tar',
        mock.ANY,
        Callback=callback,
    )
    os.remove(path)


def test_s3_artifact_store_artifact(s3_backend):
    callback = mock.Mock()
    s3_backend.store_artifact(
        mock.Mock(hash='my-hash'), '/my/path', callback,
    )
    s3_backend._s3.meta.client.upload_file.assert_called_once_with(
        '/my/path',
        Bucket='my-cool-bucket',
        Key='artifacts/my-hash.tar',
        Callback=callback,
    )
