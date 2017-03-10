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

    def has_artifact(self, ctx):
        # what a ridiculous dance we have to do here...
        try:
            self.s3.Object(self.bucket, self.key_for_ctx(ctx)).load()
        except botocore.exceptions.ClientError as ex:
            if ex.response['Error']['Code'] == '404':
                return False
            else:
                raise
        else:
            return True

    def get_artifact(self, ctx):
        fd, path = tempfile.mkstemp()
        os.close(fd)
        self.s3.Bucket(self.bucket).download_file(
            self.key_for_ctx(ctx),
            path,
        )
        return path

    def store_artifact(self, ctx, path):
        self.s3.Bucket(self.bucket).upload_file(
            path,
            self.key_for_ctx(ctx),
        )

    def invalidate_artifact(self, ctx):
        raise NotImplementedError()
