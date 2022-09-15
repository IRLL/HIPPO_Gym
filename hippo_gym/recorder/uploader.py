import boto3
from os import getenv
from multiprocessing import Process
from dotenv import load_dotenv


class Uploader:
    def __init__(self):
        load_dotenv()
        self.s3 = boto3.resource("s3")
        self.bucket = getenv("BUCKET")
        self.key = getenv("S3_KEY")

    def run(self, path, filename):
        if self.key[-1] != "/":
            key = f"{self.key}/{filename}"
        else:
            key = f"{self.key}{filename}"
        file_path = f"{path}/{filename}"

        Process(target=upload, args=(self.s3, file_path, self.bucket, key)).start()


def upload(s3, file_path, bucket, key):
    s3.meta.client.upload_file(file_path, bucket, key)
