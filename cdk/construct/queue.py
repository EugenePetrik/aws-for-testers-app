from aws_cdk import (
    CfnOutput,
    aws_sqs as sqs
)
from constructs import Construct
from cdk.construct import CloudXConstruct
from cdk.shared.tag import mark


class Queue(CloudXConstruct):
    def __init__(self, scope: Construct, construct_id: str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)
        self._create_queue()

        CfnOutput(self, 'QueueUrl',
                  value=self.sqs_queue.queue_url)

    def _create_queue(self):
        self.sqs_queue = sqs.Queue(self, 'SQSQueue')
        mark(self.sqs_queue)

    def grant_send_messages(self, g):
        self.sqs_queue.grant_send_messages(g)

    def grant_consume_messages(self, g):
        self.sqs_queue.grant_consume_messages(g)

    @property
    def url(self):
        return self.sqs_queue.queue_url
