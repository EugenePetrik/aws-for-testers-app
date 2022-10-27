import os
from typing import Optional

from aws_cdk import (
    aws_ec2 as ec2,
    aws_logs as logs,
    aws_iam as iam,
    aws_lambda as lambda_,
    aws_lambda_event_sources as event_sources,
    aws_sqs as sqs
)
from constructs import Construct
from cdk.construct import CloudXConstruct
from cdk.shared.tag import mark


class EventHandler(CloudXConstruct):
    def __init__(self, scope: Construct, construct_id: str,
                 vpc: ec2.Vpc, subnet: ec2.SubnetSelection,
                 env: Optional[dict] = None, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

        self._create_role()
        self._create_lambda(vpc, subnet, env)

    def setup_sqs_trigger(self, queue: sqs.Queue):
        self.fn.add_event_source(event_sources.SqsEventSource(queue))

    def _create_lambda(self, vpc: ec2.Vpc, subnet: ec2.SubnetSelection, env: Optional[dict] = None):
        lambda_path = os.path.join(os.getcwd(), 'lambda', 'event_handler', f"v{self.version}")
        if self.version > 1 and not os.path.isdir(lambda_path):
            print(f"Lambda version (v{self.version}) does not exist, using default: v1.")
            lambda_path = os.path.join(os.getcwd(), 'lambda', 'event_handler', "v1")
        self.fn = lambda_.Function(self, 'Lambda',
                                   vpc=vpc,
                                   vpc_subnets=subnet,
                                   handler="event_handler.lambda_handler",
                                   code=lambda_.Code.from_asset(lambda_path),
                                   environment=env,
                                   runtime=lambda_.Runtime.PYTHON_3_8,
                                   role=self.role,
                                   log_retention=logs.RetentionDays.ONE_WEEK,
                                   )
        if env:
            for k, v in env.items():
                self.fn.add_environment(k, v)
        mark(self.fn)

    def _create_role(self):
        self.role = iam.Role(self, 'LambdaRole',
                             assumed_by=iam.ServicePrincipal('lambda.amazonaws.com'))
        self.role.add_managed_policy(
            iam.ManagedPolicy.from_aws_managed_policy_name("service-role/AWSLambdaVPCAccessExecutionRole"))
        mark(self.role)
