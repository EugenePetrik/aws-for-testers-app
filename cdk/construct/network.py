from typing import Optional

from aws_cdk import (aws_ec2 as ec2)
from constructs import Construct
from cdk.construct import CloudXConstruct
from cdk.shared.tag import mark


class Network(CloudXConstruct):
    def __init__(self, scope: Construct, construct_id: str,
                 private_subnet_type: ec2.SubnetType = ec2.SubnetType.PRIVATE_WITH_NAT,
                 max_azs: Optional[int] = 1, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)
        
        self._create_vpc(private_subnet_type, max_azs)

    def _create_vpc(self,
                    private_subnet_type: ec2.SubnetType = ec2.SubnetType.PRIVATE_WITH_NAT,
                    max_azs: int = 1):
        self.vpc = ec2.Vpc(self, 'Vpc',
                           max_azs=max_azs,
                           subnet_configuration=[
                               ec2.SubnetConfiguration(name='PublicSubnet',
                                                       subnet_type=ec2.SubnetType.PUBLIC),
                               ec2.SubnetConfiguration(name='PrivateSubnet',
                                                       subnet_type=private_subnet_type),
                           ])
        self.public_subnet = ec2.SubnetSelection(
            subnet_type=ec2.SubnetType.PUBLIC)
        self.private_subnet = ec2.SubnetSelection(
            subnet_type=private_subnet_type)

        mark(self.vpc)
