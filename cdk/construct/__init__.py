from constructs import Construct
from cdk.shared.tag import mark


class CloudXConstruct(Construct):
    def __init__(self, scope: Construct, construct_id: str, version: int = 1, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)
        
        self.version = version
