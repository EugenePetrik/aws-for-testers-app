from typing import Optional
from aws_cdk import (
    aws_ec2 as ec2,
    aws_iam as iam,
    CfnOutput,
)
from constructs import Construct
from cdk.construct import CloudXConstruct
from cdk.construct.app_source import AppSource
from cdk.shared.tag import mark

CLOUD_CONFIG_SCRIPT = """
#cloud-config
cloud_final_modules:
- [scripts-user, always]
"""

CLOUD_WATCH_CONF = """
grep -q cloud-init-output /etc/awslogs/awslogs.conf | cat <<EOT >> /etc/awslogs/awslogs.conf
[/var/log/cloud-init-output.log]
datetime_format = %b %d %H:%M:%S
file = /var/log/cloud-init-output.log
buffer_duration = 5000
log_stream_name = {instance_id}
initial_position = start_of_file
log_group_name = /var/log/cloud-init
EOT
"""


class AppInstance(CloudXConstruct):
    def __init__(self, scope: Construct, construct_id: str,
                 application: str, key: str,
                 vpc: ec2.Vpc, subnet: ec2.SubnetSelection,
                 access_security_group: Optional[ec2.SecurityGroup] = None,
                 env: Optional[dict] = None,
                 log_enabled: Optional[bool] = False,
                 limit_ip: Optional[str] = None, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

        assert application, "application MUST be set (from apps)!"
        assert key, "Key MUST be set!"
        assert vpc, "Vpc MUST be set!"
        assert subnet, "Subnet MUST be set!"

        self._construct_id = construct_id
        self._deploy_application(application)
        self._create_role()
        self._create_security_group(vpc, access_security_group, limit_ip)
        self._create_instance(application, key, vpc, subnet, env, log_enabled)

        if not access_security_group:
            # assuming available from the internet
            CfnOutput(self, 'PublicIp',
                      value=self.instance.instance_public_ip)
            CfnOutput(self, 'PublicDns',
                      value=self.instance.instance_public_dns_name)
        CfnOutput(self, 'PrivateIp',
                  value=self.instance.instance_private_ip)
        CfnOutput(self, 'PrivateDns',
                  value=self.instance.instance_private_dns_name)
        CfnOutput(self, 'InstanceId',
                  value=self.instance.instance_id)

    def _deploy_application(self, application: str):
        self.deployment = AppSource(
            self, 'AppSource', application, version=self.version)

    def _create_security_group(self, vpc: ec2.Vpc, access_security_group: Optional[ec2.SecurityGroup] = None, limit_ip: Optional[str] = None):
        self.security_group = ec2.SecurityGroup(self, 'SecurityGroup',
                                                vpc=vpc,
                                                allow_all_outbound=True)
        if access_security_group:
            self.security_group.add_ingress_rule(
                ec2.Peer.security_group_id(access_security_group.security_group_id), ec2.Port.tcp(
                    22), 'SSH from Internet')
            self.security_group.add_ingress_rule(
                ec2.Peer.security_group_id(access_security_group.security_group_id), ec2.Port.tcp(
                    80), 'HTTP from Internet')
        else:
            self.security_group.add_ingress_rule(
                ec2.Peer.any_ipv4(), ec2.Port.tcp(22), 'SSH from Internet')
            self.security_group.add_ingress_rule(
                ec2.Peer.ipv4(limit_ip) if limit_ip else ec2.Peer.any_ipv4(),
                ec2.Port.tcp(80), 'HTTP from Internet')
        mark(self.security_group)

    def _create_role(self):
        self.role = iam.Role(self, 'InstanceRole',
                             assumed_by=iam.ServicePrincipal('ec2.amazonaws.com'))
        self.role.add_managed_policy(
            iam.ManagedPolicy.from_aws_managed_policy_name("CloudWatchAgentServerPolicy"))
        self.role.add_managed_policy(
            iam.ManagedPolicy.from_aws_managed_policy_name("AWSOpsWorksCloudWatchLogs"))
        self.role.add_managed_policy(self.deployment.policy)
        mark(self.role)

    def _create_instance(self,
                         application: str, key: str,
                         vpc: ec2.Vpc, subnet: ec2.SubnetSelection,
                         env: dict, log_enabled: bool = False):
        # t2.micro
        instance_type = ec2.InstanceType.of(
            ec2.InstanceClass.BURSTABLE2, ec2.InstanceSize.MICRO)
        user_data = self._get_user_data(application, env, log_enabled)
        self.instance = ec2.Instance(self, 'Instance',
                                     vpc=vpc,
                                     vpc_subnets=subnet,
                                     instance_type=instance_type,
                                     machine_image=ec2.MachineImage.latest_amazon_linux(),
                                     user_data=user_data,
                                     key_name=key,
                                     security_group=self.security_group,
                                     role=self.role)
        mark(self.instance)

    def _get_user_data(self, application: str, env: dict, log_enabled: bool = False):

        def log(s: str) -> str:
            return f'echo "---### {s} ###---"'

        multipart_user_data = ec2.MultipartUserData()

        cloud_config = ec2.UserData.custom(CLOUD_CONFIG_SCRIPT)
        multipart_user_data.add_user_data_part(
            cloud_config, 'text/cloud-config; charset="us-ascii"')

        if log_enabled:
            cloudwatch_script = ec2.UserData.for_linux(shebang="#!/bin/bash")
            cloudwatch_script.add_commands(
                log("Updating YUM"),
                "yum update -y",
                log("Installing CloudWatch Agent"),
                "yum install awslogs -y",
                log("Configuring up CloudWatch Agent"),
                CLOUD_WATCH_CONF,
                log("Starting CloudWatch Agent"),
                "service awslogs start")
            multipart_user_data.add_user_data_part(
                cloudwatch_script, 'text/x-shellscript; charset="us-ascii"')

        app_script = ec2.UserData.for_linux(shebang="#!/bin/bash")
        if env:
            for k, v in env.items():
                app_script.add_commands(f'export {k}="{v}"')

        app_script.add_commands(
            log("Updating YUM"),
            "yum update -y",
            log("Installing Python"),
            "yum install python36 -y",
            log("Cloning application"),
            f"aws s3 cp s3://{self.deployment.bucket.bucket_name}/{application} ~/{application} --recursive",
            f"cd ~/{application}",
            log("Installing application"),
            "python3 -m pip install -r requirements.txt",
            log("Starting application"),
            "python3 -m main")

        multipart_user_data.add_user_data_part(
            app_script, 'text/x-shellscript; charset="us-ascii"')

        return multipart_user_data
