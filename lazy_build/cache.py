import collections
import os
import tempfile

import boto3
import botocore


ArtifactDetails = collections.namedtuple('ArtifactDetails', ('size',))


class S3Backend(collections.namedtuple('S3Backend', (
    'bucket',
    'path',
))):

    __slots__ = ()

    @property
    def s3(self):
        return boto3.resource('s3')

    def key_for_ctx(self, ctx):
        return self.path.rstrip('/') + '/' + ctx.hash

    def artifact_paths(self, ctx):
        key = self.key_for_ctx(ctx)
        return key + '.tar.gz', key + '.json'

    def artifact_details(self, ctx):
        tarball, json = self.artifact_paths(ctx)
        try:
            obj = self.s3.Object(self.bucket, tarball)
            obj.load()
            return ArtifactDetails(obj.content_length)
        except botocore.exceptions.ClientError as ex:
            if ex.response['Error']['Code'] == '404':
                return None
            else:
                raise

    def get_artifact(self, ctx, callback):
        tarball, json = self.artifact_paths(ctx)
        fd, path = tempfile.mkstemp()
        os.close(fd)
        self.s3.meta.client.download_file(
            self.bucket,
            tarball,
            path,
            Callback=callback,
        )
        return path

    def store_artifact(self, ctx, path, callback):
        tarball, json = self.artifact_paths(ctx)
        self.s3.meta.client.upload_file(
            path,
            Key=tarball,
            Bucket=self.bucket,
            Callback=callback,
        )

    def invalidate_artifact(self, ctx):
        raise NotImplementedError()
