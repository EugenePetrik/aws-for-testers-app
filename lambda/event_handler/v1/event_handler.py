import os
import boto3

AWS_REGION = os.environ['AWS_REGION']
TOPIC_ARN = os.environ['TOPIC_ARN']


class SNSClient:
    """SNS Client to manage user subscriptions by email"""

    def __init__(self, topic_arn: str, protocol: str, region_name: str):
        self.client = boto3.client('sns', region_name=region_name)
        self.topic_arn = topic_arn
        self.protocol = protocol

    def publish(self, message: str) -> dict:
        """Publishes message to SNS topic"""

        response = self.client.publish(
            TopicArn=self.topic_arn,
            Message=message)
        print(f'SNS Client: Published message id: {response["MessageId"]}')
        print(f'SNS Client: Published message body: {message}')
        return response


def lambda_handler(event, context):
    print(f"HANDLER: {event=}")
    sns_client = SNSClient(topic_arn=TOPIC_ARN, protocol='email', region_name=AWS_REGION)
    records = event.get('Records', [])
    print(f"HANDLER: {records=}")
    for record in records:
        sns_client.publish(record['body'])
