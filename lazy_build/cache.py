import collections
import os
import tempfile

import boto3
import botocore

from lazy_build import util


ArtifactDetails = collections.namedtuple('ArtifactDetails', ('size',))


class S3Backend(collections.namedtuple('S3Backend', (
    'bucket',
    'path',
))):

    __slots__ = ()

    @property
    def _s3(self):
        return boto3.resource('s3')

    def _key_for_ctx(self, ctx):
        return self.path.rstrip('/') + '/' + ctx.hash

    def _artifact_paths(self, ctx):
        key = self._key_for_ctx(ctx)
        return f'{key}.tar', f'{key}.json'

    def artifact_details(self, ctx):
        tarball, json = self._artifact_paths(ctx)
        try:
            obj = self._s3.Object(self.bucket, tarball)
            obj.load()
            return ArtifactDetails(obj.content_length)
        except botocore.exceptions.ClientError as ex:
            if ex.response['Error']['Code'] == '404':
                return None
            else:
                raise

    def get_artifact(self, ctx, callback):
        tarball, json = self._artifact_paths(ctx)
        fd, path = tempfile.mkstemp()
        os.close(fd)
        self._s3.meta.client.download_file(
            self.bucket,
            tarball,
            path,
            Callback=callback,
        )
        return path

    def store_artifact(self, ctx, path, callback):
        tarball, json = self._artifact_paths(ctx)
        self._s3.meta.client.upload_file(
            path,
            Key=tarball,
            Bucket=self.bucket,
            Callback=callback,
        )

    def invalidate_artifact(self, ctx):
        raise NotImplementedError()


class FilesystemBackend(collections.namedtuple('FilesystemBackend', (
    'path',
))):

    __slots__ = ()

    def _path_for_ctx(self, ctx):
        return self.path.rstrip('/') + '/' + ctx.hash

    def _artifact_paths(self, ctx):
        key = self._path_for_ctx(ctx)
        return f'{key}.tar', f'{key}.json'

    def artifact_details(self, ctx):
        tarball, json = self._artifact_paths(ctx)
        try:
            return ArtifactDetails(os.path.getsize(tarball))
        except FileNotFoundError:
            return None

    def get_artifact(self, ctx, callback):
        # TODO: ideally for this backend we wouldn't bother writing the
        # temporary file in the first place (currently we have to do this
        # because the code deletes it after restore)
        tarball, json = self._artifact_paths(ctx)
        fd, path = tempfile.mkstemp()
        with os.fdopen(fd, 'wb') as tf:
            with open(tarball, 'rb') as f:
                util.copyfileobj(f, tf, callback)
        return path

    def store_artifact(self, ctx, path, callback):
        tarball, json = self._artifact_paths(ctx)
        with util.atomic_write(tarball, 'wb') as dest:
            # TODO: ideally for this backend we wouldn't bother writing the
            # temporary file in the first place
            with open(path, 'rb') as src:
                util.copyfileobj(src, dest, callback)

    def invalidate_artifact(self, ctx):
        raise NotImplementedError()
