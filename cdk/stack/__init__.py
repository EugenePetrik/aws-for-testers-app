from typing import List, Optional
from aws_cdk import Stack
from constructs import Construct


class CloudXStack(Stack):
    def __init__(self, scope: Construct, construct_id: str, versions: Optional[List[int]] = [1], **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)
        
        self.version = int(self.node.try_get_context('version') or "1")

        assert self.version in versions, f"There is no version like {self.version}, available versions: {versions}."