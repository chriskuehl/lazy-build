import collections
import os
import tempfile

import boto3
import botocore


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

    def has_artifact(self, ctx):
        tarball, json = self.artifact_paths(ctx)
        # what a ridiculous dance we have to do here...
        try:
            self.s3.Object(self.bucket, tarball).load()
        except botocore.exceptions.ClientError as ex:
            if ex.response['Error']['Code'] == '404':
                return False
            else:
                raise
        else:
            return True

    def get_artifact(self, ctx):
        tarball, json = self.artifact_paths(ctx)
        fd, path = tempfile.mkstemp()
        os.close(fd)
        self.s3.Bucket(self.bucket).download_file(
            tarball,
            path,
        )
        return path

    def store_artifact(self, ctx, path):
        tarball, json = self.artifact_paths(ctx)
        self.s3.Bucket(self.bucket).upload_file(
            path,
            tarball,
        )

    def invalidate_artifact(self, ctx):
        raise NotImplementedError()
