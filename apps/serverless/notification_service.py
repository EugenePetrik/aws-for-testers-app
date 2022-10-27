"""Module to process subscriptions to SNS topic"""
import os
from typing import List

from sns_client import InvalidEmailException, SNSClient, PendingConfirmationException, SubscriptionNotFoundException

TOPIC_ARN = os.environ['TOPIC_ARN']
REGION = os.environ['AWS_REGION']

sns_client = SNSClient(topic_arn=TOPIC_ARN, protocol='email', region_name=REGION)


def list_subscriptions() -> List[dict]:
    return sns_client.list_subscriptions()


def subscribe(email_address: str):
    try:
        sns_client.subscribe(email=email_address)
    except InvalidEmailException:
        return "Invalid e-mail address!", 400

def unsubscribe(email_address: str):
    try:
        sns_client.unsubscribe(email=email_address)
    except PendingConfirmationException:
        return "Subscription is still pending!", 412
    except SubscriptionNotFoundException:
        return "Subscription is not found!", 404
