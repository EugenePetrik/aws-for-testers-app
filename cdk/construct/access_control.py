from aws_cdk import (
    CfnOutput,
    aws_iam as iam
)
from constructs import Construct
from cdk.shared.tag import mark
from cdk.construct import CloudXConstruct


class AccessControl(CloudXConstruct):
    def __init__(self, scope: Construct, construct_id: str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

        self._create_ec2_resources()
        self._create_full_access_s3_resources()
        self._create_read_access_s3_resources()

        CfnOutput(self, 'FullAccessPolicyEC2Name',
                  value=self.policy_full_access_ec2.managed_policy_name)
        CfnOutput(self, 'FullAccessPolicyS3Name',
                  value=self.policy_full_access_s3.managed_policy_name)
        CfnOutput(self, 'ReadAccessPolicyS3Name',
                  value=self.policy_read_access_s3.managed_policy_name)

    def _create_ec2_resources(self):
        self.policy_full_access_ec2 = iam.ManagedPolicy(self, 'FullAccessPolicyEC2',
                                                        statements=[
                                                            iam.PolicyStatement(effect=iam.Effect.ALLOW,
                                                                                actions=[
                                                                                    'ec2:*'],
                                                                                resources=['*'])
                                                        ])

        self.group_full_access_ec2 = iam.Group(
            self, 'FullAccessGroupEC2', group_name='FullAccessGroupEC2')
        self.group_full_access_ec2.add_managed_policy(
            self.policy_full_access_ec2)

        self.role_full_access_ec2 = iam.Role(self, 'FullAccessRoleEC2', role_name='FullAccessRoleEC2',
                                             assumed_by=iam.ServicePrincipal('ec2.amazonaws.com'))
        self.role_full_access_ec2.add_managed_policy(
            self.policy_full_access_ec2)

        mark(self.policy_full_access_ec2)
        mark(self.group_full_access_ec2)
        mark(self.role_full_access_ec2)

    def _create_full_access_s3_resources(self):
        action = 's3:*' if self.version == 1 else 's3:Get*'
        
        self.policy_full_access_s3 = iam.ManagedPolicy(self, 'FullAccessPolicyS3',
                                                    statements=[
                                                        iam.PolicyStatement(
                                                            actions=[action], resources=['*'])
                                                    ])
        self.group_full_access_s3 = iam.Group(
            self, 'FullAccessGroupS3', group_name='FullAccessGroupS3')
        self.group_full_access_s3.add_managed_policy(
            self.policy_full_access_s3)

        self.role_full_access_s3 = iam.Role(self, 'FullAccessRoleS3', role_name='FullAccessRoleS3',
                                            assumed_by=iam.ServicePrincipal('ec2.amazonaws.com'))
        self.role_full_access_s3.add_managed_policy(self.policy_full_access_s3)

        mark(self.policy_full_access_s3)
        mark(self.group_full_access_s3)
        mark(self.role_full_access_s3)

    def _create_read_access_s3_resources(self):
        self.policy_read_access_s3 = iam.ManagedPolicy(self, 'ReadAccessPolicyS3',
                                                       statements=[
                                                           iam.PolicyStatement(
                                                               actions=[
                                                                   's3:Get*', 's3:List*', 's3:Describe*'],
                                                               resources=['*'])
                                                       ])
        self.group_read_access_s3 = iam.Group(
            self, 'ReadAccessGroupS3', group_name='ReadAccessGroupS3')
        self.group_read_access_s3.add_managed_policy(
            self.policy_read_access_s3)

        self.role_read_access_s3 = iam.Role(self, 'ReadAccessRoleEC2', role_name='ReadAccessRoleEC2',
                                            assumed_by=iam.ServicePrincipal('ec2.amazonaws.com'))
        self.role_read_access_s3.add_managed_policy(self.policy_read_access_s3)

        mark(self.policy_read_access_s3)
        mark(self.group_read_access_s3)
        mark(self.role_read_access_s3)
