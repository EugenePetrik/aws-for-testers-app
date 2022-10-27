import os
from aws_cdk import (
    CfnOutput,
    RemovalPolicy,
    aws_iam as iam,
    aws_s3 as s3,
    aws_s3_deployment as s3d,
    aws_logs as logs
)
from constructs import Construct
from cdk.construct import CloudXConstruct
from cdk.shared.tag import mark


class AppSource(CloudXConstruct):
    EXCLUDE_FROM_SOURCE = ['**/__pycache__',
                           '**/.pytest_cache', '**/.venv', '**/venv', '.pylintrc']

    def __init__(self, scope: Construct, construct_id: str, application: str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

        self.application = application
        self.application_path = os.path.join(os.getcwd(), 'apps', application, f"v{self.version}")
        if self.version > 1 and not os.path.isdir(self.application_path):
            print(f"Application version ({application}@v{self.version}) does not exist, using default: v1.")
            self.application_path = os.path.join(os.getcwd(), 'apps', application, "v1")
        assert os.path.isdir(
            self.application_path), f"Application in {self.application_path} does not exist!"

        self._create_bucket()
        self._create_policy()
        self._create_deployment()

    def _create_bucket(self):
        self.bucket = s3.Bucket(self, 'Bucket',
                                public_read_access=False,
                                removal_policy=RemovalPolicy.DESTROY,
                                auto_delete_objects=True)
        mark(self.bucket)

    def _create_policy(self):
        self.policy = iam.ManagedPolicy(self, 'BucketPolicy', statements=[
            iam.PolicyStatement(actions=['s3:ListBucket'], resources=[
                                self.bucket.bucket_arn]),
            iam.PolicyStatement(
                actions=['s3:GetObject*'], resources=[self.bucket.bucket_arn + "/*"])
        ])
        mark(self.policy)

    def _create_deployment(self):
        source = s3d.Source.asset(
            self.application_path, exclude=self.EXCLUDE_FROM_SOURCE)
        self.deployment = s3d.BucketDeployment(self, 'Deployment',
                                               sources=[source],
                                               destination_bucket=self.bucket,
                                               destination_key_prefix=self.application,
                                               log_retention=logs.RetentionDays.ONE_WEEK,
                                               retain_on_delete=False)
        mark(self.deployment)
