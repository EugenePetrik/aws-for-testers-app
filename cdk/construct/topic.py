from aws_cdk import (
    RemovalPolicy,
    aws_sns as sns,
    aws_iam as iam,
    CfnOutput
)
from constructs import Construct
from cdk.construct import CloudXConstruct
from cdk.shared.tag import mark


class Topic(CloudXConstruct):
    def __init__(self, scope: Construct, construct_id: str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)
        self._create_queue()
        self._create_policies()

        CfnOutput(self, 'TopicArn',
                  value=self.topic.topic_arn)

    def _create_queue(self):
        self.topic = sns.Topic(self, 'SNSTopic')
        self.topic.apply_removal_policy(RemovalPolicy.DESTROY)
        mark(self.topic)

    def _create_policies(self):
        self.subscription_policy = iam.ManagedPolicy(self, 'SubscriptionPolicy', statements=[
            iam.PolicyStatement(actions=['sns:ListSubscriptions*', 'sns:Subscribe', 'sns:Unsubscribe'],
                                resources=[self.topic.topic_arn])
        ])
        mark(self.subscription_policy)

        self.publish_policy = iam.ManagedPolicy(self, 'PublishPolicy', statements=[
            iam.PolicyStatement(actions=['sns:Publish'],
                                resources=[self.topic.topic_arn])
        ])
        mark(self.publish_policy)

    @property
    def arn(self):
        return self.topic.topic_arn
