from multiprocessing import Process
from os import getenv

import boto3
from dotenv import load_dotenv


class Uploader:
    def __init__(self) -> None:
        load_dotenv()
        self.s3 = boto3.resource("s3")
        self.bucket = getenv("BUCKET")
        self.key = getenv("S3_KEY")

    def run(self, path: str, filename: str) -> None:
        if self.key is None:
            raise ValueError
        if self.key[-1] != "/":
            key = f"{self.key}/{filename}"
        else:
            key = f"{self.key}{filename}"
        file_path = f"{path}/{filename}"

        Process(target=upload, args=(self.s3, file_path, self.bucket, key)).start()


def upload(s3, file_path: str, bucket, key: str) -> None:
    s3.meta.client.upload_file(file_path, bucket, key)
