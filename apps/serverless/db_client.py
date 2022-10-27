"""
Module for Cloud SQL client
"""
import datetime
from decimal import Decimal
from email.mime import image
import uuid
import os
from typing import Optional, List

import boto3

TABLE_NAME = os.environ["TABLE_NAME"]

class NoSQLClient:

    """Wrapper above mysql client with service related business logic"""

    def __init__(self, region_name: str):
        """Initializes DynamoDB client"""

        self.client = boto3.resource('dynamodb', region_name=region_name)
        self.table = self.client.Table(TABLE_NAME)

    def create_image(self,
                     object_key: str,
                     object_type: str,
                     last_modified: datetime,
                     object_size: int) -> str:
        """Creates images items in the table"""

        id = str(uuid.uuid4())
        self.table.put_item(
            Item={
                'id': id,
                'object_key': object_key,
                'object_type': object_type,
                'last_modified': Decimal(last_modified.timestamp()),
                'created_at': Decimal(int(datetime.datetime.now().timestamp())),
                'object_size': Decimal(object_size)
            }
        )
        return id


    def get_image(self, image_id: str) -> Optional[dict]:
        """Gets image by id from dynamoDB"""

        response = self.table.get_item(
            Key={
                'id': image_id
            }
        )
        return response['Item']

    def delete_image(self, image_id: str):
        """Deletes image from dynamoDB"""
        self.table.delete_item(
            Key={
                'id': image_id
            }
        )


    def get_images(self) -> List[dict]:
        """Gets images from mysql db"""

        response = self.table.scan()
        data = response['Items']

        while 'LastEvaluatedKey' in response:
            response = self.table.scan(ExclusiveStartKey=response['LastEvaluatedKey'])
            data.extend(response['Items'])
        return data
