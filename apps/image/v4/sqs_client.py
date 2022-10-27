"""Module to work with AWS SQS Service"""

import datetime
from typing import List, Optional

import boto3


class SQSClient:
    """AWS SQS Client"""

    def __init__(self, queue_url: str, region_name: str):
        """Initializes SQS client by queue url"""

        self.client = boto3.client('sqs', region_name=region_name)
        self.queue_url = queue_url

    def send_message(self, event_type: str,
                     object_key: str,
                     object_type: str,
                     last_modified: datetime,
                     object_size: int,
                     download_link: str) -> dict:
        """Sends message to SQS queue"""

        message_body = f'event_type: {event_type}\n' \
                       f'object_key: {object_key}\n' \
                       f'object_type: {object_type}\n' \
                       f'last_modified: {last_modified}\n' \
                       f'object_size: {object_size}\n' \
                       f'download_link: {download_link}'

        response = self.client.send_message(
            QueueUrl=self.queue_url,
            MessageBody=message_body
        )
        print(f'SQS Client: Sent message: id {response["MessageId"]}')
        print(f'SQS Client: Sent message: body {message_body}')
        return response

    def receive_messages(self) -> Optional[List[dict]]:
        """Receives messages from SQS queue"""

        response = self.client.receive_message(
            QueueUrl=self.queue_url,
            MaxNumberOfMessages=10,
            WaitTimeSeconds=15)
        messages = response.get('Messages')
        if messages:
            print(f'SQS Client: received {len(messages)}')
        else:
            print('SQS Client: no messages received')
        return messages

    def delete_message_batch(self, messages: List[dict]) -> dict:
        entries = [{'Id': message['MessageId'],
                    'ReceiptHandle': message['ReceiptHandle']}
                   for message in messages]
        response = self.client.delete_message_batch(
            QueueUrl=self.queue_url,
            Entries=entries)
        if response.get('Successful'):
            print(f'SQS Client: {len(messages)} messages deleted')
        else:
            print(f'SQS Client:unable to delete {len(messages)} messages')
        return response

