from aws_cdk import (
    RemovalPolicy,
    aws_dynamodb as dynamo,
    aws_ec2 as ec2,
    CfnOutput
)
from constructs import Construct
from cdk.construct import CloudXConstruct
from cdk.shared.tag import mark


class NoSQLDatabase(CloudXConstruct):
    def __init__(self, scope: Construct, construct_id: str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

        self._setup_table()

        CfnOutput(self, 'TableName',
                  value=self.table.table_name)

    def _setup_table(self):
        self.table = dynamo.Table(self, 'ImagesTable',
                                  partition_key=dynamo.Attribute(
                                      name='id', type=dynamo.AttributeType.STRING),
                                  billing_mode=dynamo.BillingMode.PROVISIONED,
                                  removal_policy=RemovalPolicy.DESTROY,
                                  )
        self.table.auto_scale_write_capacity(
            min_capacity=1,
            max_capacity=5
        ).scale_on_utilization(target_utilization_percent=75)

        mark(self.table)

    def allow_instance(self, instance: ec2.Instance):
        self.table.grant_read_write_data(instance)

    @property
    def table_name(self):
        return self.table.table_name
