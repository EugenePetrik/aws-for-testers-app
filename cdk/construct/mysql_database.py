import json
from aws_cdk import (
    Duration,
    RemovalPolicy,
    aws_rds as rds,
    aws_ec2 as ec2,
    aws_iam as iam,
    aws_secretsmanager as secretsmanager,
    CfnOutput
)
from constructs import Construct
from cdk.construct import CloudXConstruct
from cdk.shared.tag import mark


class MySQLDatabase(CloudXConstruct):
    DATABASE_NAME = 'cloudximages'
    DB_USERNAME = 'mysql_admin'
    DB_PORT = 3306

    def __init__(self, scope: Construct, construct_id: str,
                 vpc: ec2.Vpc, subnets: ec2.SubnetSelection, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

        self._setup_credentials()
        self._setup_mysql(vpc, subnets)

        CfnOutput(self, 'DbName',
                  value=self.DATABASE_NAME)
        CfnOutput(self, 'DbUsername',
                  value=self.DB_USERNAME)
        CfnOutput(self, 'DbSecretName',
                  value=self.secret.secret_name)
        CfnOutput(self, 'DbHost',
                  value=self.db.db_instance_endpoint_address)
        CfnOutput(self, 'DbPort',
                  value=self.db.db_instance_endpoint_port)

    @property
    def database_name(self):
        return self.DATABASE_NAME

    @property
    def username(self):
        return self.DB_USERNAME

    @property
    def secret_name(self):
        return self.secret.secret_name

    @property
    def host(self):
        return self.db.db_instance_endpoint_address

    @property
    def port(self):
        return self.db.db_instance_endpoint_port

    def allow_instance(self, instance: ec2.Instance):
        self.db.connections.allow_from(
            ec2.Peer.any_ipv4(), ec2.Port.tcp(self.DB_PORT))
        self.db.connections.allow_from(instance, ec2.Port.tcp(self.DB_PORT))

    def _setup_credentials(self):
        self.secret = secretsmanager.Secret(self, 'DBSecret',
                                            generate_secret_string=secretsmanager.SecretStringGenerator(
                                                secret_string_template=json.dumps({
                                                    'username': self.DB_USERNAME
                                                }),
                                                exclude_punctuation=True,
                                                include_space=False,
                                                generate_string_key='password'
                                            ), removal_policy=RemovalPolicy.DESTROY)
        mark(self.secret)

        self.policy = iam.ManagedPolicy(self, 'SecretPolicy', statements=[
            iam.PolicyStatement(actions=['secretsmanager:GetSecretValue'], resources=[
                                self.secret.secret_arn]),
        ])
        mark(self.policy)

        self.creds = rds.Credentials.from_secret(self.secret)
        mark(self.creds)

    def _setup_mysql(self, vpc: ec2.Vpc, subnets: ec2.SubnetSelection):
        self.engine = rds.DatabaseInstanceEngine.mysql(
            version=rds.MysqlEngineVersion.VER_8_0_28)
        
        # db.t3.micro
        instance_type = ec2.InstanceType.of(
            ec2.InstanceClass.BURSTABLE3, ec2.InstanceSize.MICRO)
        self.db = rds.DatabaseInstance(self, 'MySQLInstance',
                                       engine=self.engine,
                                       vpc=vpc,
                                       vpc_subnets=subnets,
                                       multi_az=False,
                                       database_name=self.DATABASE_NAME,
                                       instance_type=instance_type,
                                       credentials=self.creds,
                                       delete_automated_backups=True,
                                       backup_retention=Duration.days(0),
                                       removal_policy=RemovalPolicy.DESTROY
                                       )
        mark(self.db)
