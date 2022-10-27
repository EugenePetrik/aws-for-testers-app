"""Module to process REST requests for image service"""
import os
from typing import List

import connexion
import flask
from uuid import uuid4
from ec2_metadata import ec2_metadata

from db_client import NoSQLClient
from sqs_client import SQSClient
from s3_client import S3Bucket

QUEUE_URL = os.environ['QUEUE_URL']
S3_BUCKET = os.environ['S3_BUCKET']
REGION = os.environ['AWS_REGION']

db_client = NoSQLClient(region_name=REGION)
sqs_client = SQSClient(queue_url=QUEUE_URL, region_name=REGION)
s3_bucket = S3Bucket(bucket_name=S3_BUCKET, region_name=REGION)


def upload_image() -> None:
    """Uploads image to s3 bucket and save record in database"""

    # save temp file
    uid = str(uuid4())
    file_to_upload = connexion.request.files['upfile']
    file_name = file_to_upload.filename
    file_to_upload.save(file_name)

    # put to S3 bucket
    key = f'images/{uid}-{file_name}'
    s3_bucket.upload_object(filepath=file_name, object_key=key)

    # get from S3 bucket
    s3_info = s3_bucket.get_object(object_key=key)
    object_type = s3_info.content_type
    modified = s3_info.last_modified
    size = s3_info.content_length

    # add record to DB
    image_id = db_client.create_image(object_key=key,
                                      object_type=object_type,
                                      last_modified=modified,
                                      object_size=size)

    # generate S3 link
    ip = ec2_metadata.public_hostname or ec2_metadata.public_ipv4
    download_link = f'http://{ip}/api/image/file/{image_id}'

    # send message to SQS
    sqs_client.send_message(event_type='upload',
                            object_key=key,
                            object_type=object_type,
                            last_modified=modified,
                            object_size=size,
                            download_link=download_link)

    # remove temporary file
    os.remove(file_name)


def delete_image(image_id: str) -> None:
    """Deletes iage from s3 bucket and deletes record from database"""

    image_info = db_client.get_image(image_id=image_id)
    if not image_info:
        return "Image not found!", 404
    
    # delete the image from the S3 bucket
    s3_bucket.delete_object(object_key=image_info['object_key'])
    # delete the image metadata from the DB
    db_client.delete_image(image_id=image_id)
    # send delete event to SQS queue
    sqs_client.send_message(event_type='delete',
                            object_key=image_info['object_key'],
                            object_type=image_info['object_type'],
                            last_modified=image_info['last_modified'],
                            object_size=image_info['object_size'],
                            download_link='')


def get_image_info(image_id: str) -> dict:
    """Gets image info by object key"""
    image_info = db_client.get_image(image_id=image_id)
    if not image_info:
        return "Image not found!", 404
    return image_info


def get_all_images_info() -> List[dict]:
    """Gets all images info in s3 bucket"""
    return db_client.get_images()


def download_image(image_id: str):
    """Downloads image file from s3 bucket"""

    image_info = db_client.get_image(image_id=image_id)
    if not image_info:
        return "Image is not found!", 404
    
    object_key = image_info['object_key']
    file_name = object_key.split('/')[-1]
    extension = os.path.splitext(file_name)[-1][1:]
    mime = f'image/{extension}'
    s3_bucket.download_object(object_key=object_key, filepath=file_name)

    resp = flask.send_from_directory(os.path.dirname(__file__),
                                     file_name,
                                     as_attachment=True,
                                     mimetype=mime,
                                     attachment_filename=file_name)

    return flask.Response(
        response=resp.response,
        status=200,
        content_type=mime,
        headers=resp.headers,
        mimetype=resp.mimetype
    )
