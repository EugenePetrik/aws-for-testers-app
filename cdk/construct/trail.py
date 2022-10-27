from aws_cdk import (
    RemovalPolicy,
    aws_cloudtrail as cloudtrail,
    aws_s3 as s3
)
from constructs import Construct
from cdk.construct import CloudXConstruct
from cdk.shared.tag import mark


class Trail(CloudXConstruct):
    def __init__(self, scope: Construct, construct_id: str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)
        self._setup_bucket()
        self._setup_trail()

    def _setup_bucket(self):
        self.bucket = s3.Bucket(
            self, 'TrailBucket',
            removal_policy=RemovalPolicy.DESTROY,
            auto_delete_objects=True)
        mark(self.bucket)

    def _setup_trail(self):
        self.trail = cloudtrail.Trail(
            self, 'Trail',
            bucket=self.bucket)
        mark(self.trail)
