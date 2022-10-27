from constructs import Construct
from cdk.construct.access_control import AccessControl
from cdk.stack import CloudXStack


class CloudXIAMStack(CloudXStack):
    def __init__(self, scope: Construct, construct_id: str, **kwargs) -> None:
        super().__init__(scope, construct_id, versions=[1,2], **kwargs)
        
        self.access_control = AccessControl(self, 'CloudXAccessControl', version=self.version)
