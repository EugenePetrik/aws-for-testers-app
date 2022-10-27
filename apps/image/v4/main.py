"""Main module for IMAGE Application"""

import os
import threading
import connexion
import yaml

from sns_client import SNSClient
from sqs_client import SQSClient

with open('config.yaml', encoding='utf-8') as f:
    config = yaml.safe_load(f.read())
    for k, v in config.items():
        if k not in os.environ:
            os.environ[k] = str(v)

AWS_REGION = os.environ['AWS_REGION']
QUEUE_URL = os.environ['QUEUE_URL']
TOPIC_ARN = os.environ['TOPIC_ARN']

options = {'swagger_ui': True}
app = connexion.FlaskApp(__name__,
                         specification_dir='openapi/',
                         options=options)
app.add_api('swagger.yml')

def background_process():
    """
    Background process that checks for events in SQS queue,
    and published notifications in SNS topic
    """

    sqs_client = SQSClient(queue_url=QUEUE_URL, region_name=AWS_REGION)
    sns_client = SNSClient(topic_arn=TOPIC_ARN,
                           protocol='email-json', region_name=AWS_REGION)

    while True:
        messages = sqs_client.receive_messages()
        if messages:
            for message in messages:
                sns_client.publish(message['Body'])
            sqs_client.delete_message_batch(messages)


if __name__ == '__main__':
    thread = threading.Thread(target=background_process)
    thread.start()
    app.run(host='0.0.0.0', port=80, debug=True)
