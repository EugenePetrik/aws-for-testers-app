"""Module for s3 related actions"""
from typing import List

import boto3


class S3Bucket:
    """
    S3Bucket class is wrapper for s3 bucket object provide by AWS api.
    """

    def __init__(self, bucket_name: str, region_name: str):
        """
        Gets s3 bucket object form AWS api
        """
        self.client = boto3.client('s3', region_name=region_name)
        self.resource = boto3.resource('s3', region_name=region_name)
        self.bucket_name = bucket_name

    def upload_object(self, filepath: str, object_key: str) -> None:
        """Upload object to s3 bucket"""

        self.client.upload_file(filepath, self.bucket_name, object_key)

    def get_object(self, object_key: str) -> dict:
        """Get object info from s3"""

        return self.resource.Object(bucket_name=self.bucket_name, key=object_key)

    def delete_object(self, object_key: str) -> dict:
        """Deletes object from s3 bucket"""

        return self.client.delete_object(Bucket=self.bucket_name, Key=object_key)

    def list_objects(self, prefix: str) -> dict:
        """Lists objects by specified prefix"""

        return self.client.list_objects_v2(
            Bucket=self.bucket_name,
            Delimiter='/',
            EncodingType='url',
            MaxKeys=123,
            Prefix=prefix
        )

    def download_object(self, object_key: str, filepath: str) -> None:
        """Downloads file from s3 bucket"""

        self.resource.meta.client.download_file(self.bucket_name, object_key, filepath)
