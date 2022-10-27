from constructs import Construct
from cdk.construct.network import Network
from cdk.construct.app_instance import AppInstance
from cdk.stack import CloudXStack


class CloudXInfoStack(CloudXStack):
    def __init__(self, scope: Construct, construct_id: str, key: str, **kwargs) -> None:
        super().__init__(scope, construct_id, versions=[1, 2, 3], **kwargs)

        application = 'info'

        self._setup_network()
        self._setup_public_instance(application, key)
        self._setup_private_instance(application, key)

    def _setup_network(self):
        self.network = Network(self, 'Network')

    def _setup_public_instance(self, application: str, key: str):
        self.public_instance = AppInstance(self, 'PublicInstance',
                                           application=application,
                                           key=key,
                                           vpc=self.network.vpc,
                                           subnet=self.network.public_subnet,
                                           env=None,
                                           limit_ip="1.2.3.4/32" if self.version == 3 else None,
                                           version=self.version)

    def _setup_private_instance(self, application: str, key: str):
        self.private_instance = AppInstance(self, 'PrivateInstance',
                                            application=application,
                                            key=key,
                                            vpc=self.network.vpc,
                                            subnet=self.network.public_subnet if self.version == 3 else self.network.private_subnet,
                                            access_security_group=None if self.version == 3 else self.public_instance.security_group,
                                            env=None,
                                            version=self.version)
