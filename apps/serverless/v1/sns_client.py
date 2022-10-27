"""Module to work with AWS SNS Service"""
from typing import List

import boto3


class PendingConfirmationException(Exception):
    pass


class SubscriptionNotFoundException(Exception):
    pass

class InvalidEmailException(Exception):
    pass


class SNSClient:
    """SNS Client to manage user subscriptions by email"""

    def __init__(self, topic_arn: str, protocol: str, region_name: str):
        self.client = boto3.client('sns', region_name=region_name)
        self.topic_arn = topic_arn
        self.protocol = protocol

    def subscribe(self, email: str) -> dict:
        """Subscribe by email to SNS topic"""

        try:
            response = self.client.subscribe(
                TopicArn=self.topic_arn,
                Protocol=self.protocol,
                Endpoint=email,
                ReturnSubscriptionArn=True
            )

            print(f'SNS Client: subscribed {email}')
            print(f'SNS Client: subscription ID - {response["SubscriptionArn"]}')
            return response
        except self.client.exceptions.InvalidParameterException:
            raise InvalidEmailException

    def unsubscribe(self, email: str):
        """Unsubscribes user by email from topic"""

        subscription_arn = self.__get_subscription_arn(email=email)
        if subscription_arn == "PendingConfirmation":
            raise PendingConfirmationException
        self.client.unsubscribe(SubscriptionArn=subscription_arn)
        print(f'SNS Client: unsubscribed {email}')

    def __get_subscription_arn(self, email: str) -> str:
        """Gets subscription arn by email"""

        subscriptions = self.list_subscriptions()
        subscription = next(
            filter(lambda x: x['Endpoint'] == email, subscriptions), None)
        if not subscription:
            raise SubscriptionNotFoundException
        return subscription['SubscriptionArn']
    
    def list_subscriptions(self) -> List[dict]:
        """Get all subscriptions list"""

        response = self.client.list_subscriptions_by_topic(TopicArn=self.topic_arn)
        return response['Subscriptions']

    def publish(self, message: str) -> dict:
        """Publishes message to SNS topic"""

        response = self.client.publish(
            TopicArn=self.topic_arn,
            Message=message)
        print(f'SNS Client: Published message id: {response["MessageId"]}')
        print(f'SNS Client: Published message body: {message}')
        return response
