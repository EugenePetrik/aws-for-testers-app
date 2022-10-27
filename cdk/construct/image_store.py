from aws_cdk import (
    CfnOutput,
    RemovalPolicy,
    aws_s3 as s3,
    aws_iam as iam
)
from constructs import Construct
from cdk.construct import CloudXConstruct
from cdk.shared.tag import mark


class ImageStore(CloudXConstruct):
    def __init__(self, scope: Construct, construct_id: str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)
        self._create_bucket()
        self._create_policy()

        CfnOutput(self, 'ImageBucketName',
                  export_name='ImageBucketName',
                  value=self.bucket.bucket_name)

    def _create_bucket(self):
        """
        The bucket which stored the image data.
        """
        self.bucket = s3.Bucket(self, 'Bucket',
                                public_read_access=self.version == 2,
                                removal_policy=RemovalPolicy.DESTROY,
                                auto_delete_objects=True)
        mark(self.bucket)

    def _create_policy(self):
        """
        The policy which allows to list, retrieve and put images to the bucket.
        """
        self.policy = iam.ManagedPolicy(self, 'BucketPolicy', statements=[
            iam.PolicyStatement(actions=['s3:ListBucket'], resources=[
                                self.bucket.bucket_arn]),
            iam.PolicyStatement(actions=['s3:GetObject*', 's3:PutObject*', 's3:DeleteObject*'],
                                resources=[self.bucket.bucket_arn + "/*"])
        ])
        mark(self.policy)
