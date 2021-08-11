import boto3
from os import getenv
from multiprocessing import Process


class Uploader:

    def __init__(self):
        self.s3 = boto3.resource('s3')
        self.bucket = getenv('BUCKET')
        self.key = getenv('S3_KEY')

    def run(self, path, filename):
        if self.key[-1] != '/':
            key = f'{self.key}/{filename}'
        else:
            key = f'{self.key}{filename}'

        Process(target=upload, args=(self.s3, path, self.bucket, key))


def upload(s3, path, bucket, key):
    s3.meta.client.upload_file(path, bucket, key)
