"""
Module for Cloud SQL client
"""
import datetime
import json
import os
import requests
import shutil
from typing import Optional, List

import boto3
import sqlalchemy
from sqlalchemy import text

DB_USERNAME = os.environ["DB_USERNAME"]
DB_PASSWORD_SECRET_NAME = os.environ['DB_PASSWORD_SECRET_NAME']
DB_NAME = os.environ["DB_NAME"]
DB_HOST = os.environ["DB_HOST"]
DB_PORT = int(os.environ['DB_PORT'])


class MySQLClient:
    GLOBAL_CERT_URL = 'https://truststore.pki.rds.amazonaws.com/global/global-bundle.pem'

    """Wrapper above mysql client with service related business logic"""

    def __init__(self):
        """Initializes Cloud SQL client"""

        self.__database = None
        self.__create_table()
        self.__db_config = None

    def __init_connection_engine(self):
        return self.__init_tcp_connection_engine()

    def __init_tcp_connection_engine(self):
        self.__db_config = {
            "pool_size": 5,
            "max_overflow": 2,
            "pool_timeout": 30,
            "pool_recycle": 1800
        }

        db_token = self.__init_db_password(DB_PASSWORD_SECRET_NAME)

        pool = sqlalchemy.create_engine(
            sqlalchemy.engine.url.URL.create(
                drivername="mysql+pymysql",
                username=DB_USERNAME,
                password=db_token,
                host=DB_HOST,
                port=DB_PORT,
                database=DB_NAME,
                query={"ssl_ca": self.__initialize_cert()},
            ),
            **self.__db_config
        )

        return pool

    @staticmethod
    def __initialize_cert() -> str:
        url = MySQLClient.GLOBAL_CERT_URL
        local_filename = url.split('/')[-1]
        path = os.path.join(os.getcwd(), local_filename)
        with requests.get(url, stream=True) as r:
            with open(path, 'wb') as f:
                shutil.copyfileobj(r.raw, f)

        return local_filename

    @staticmethod
    def __init_db_password(secret_name: str) -> str:
        """Generated token for connection by 02_iam role"""

        aws_region = os.environ['AWS_REGION']
        client = boto3.client('secretsmanager', region_name=aws_region)
        secret = client.get_secret_value(SecretId=secret_name)
        return json.loads(secret['SecretString'])['password']

    def __create_table(self):
        """try to check if table exists, and create if not"""

        self.__database = self.__database or self.__init_connection_engine()
        with self.__database.connect() as connection:
            connection.execute(
                "CREATE TABLE IF NOT EXISTS images "
                "(id SERIAL NOT NULL PRIMARY KEY, "
                "object_key TEXT NOT NULL, "
                "object_type TEXT NOT NULL, "
                "last_modified timestamp NOT NULL, "
                "object_size BIGINT NOT NULL);"
            )

    def create_image(self,
                     object_key: str,
                     object_type: str,
                     last_modified: datetime,
                     object_size: int) -> int:
        """Creates images table in mysql db"""

        with self.__database.connect() as connection:
            stmt = text("INSERT INTO images "
                        "(object_key, object_type, last_modified, object_size) "
                        "VALUES (:object_key, :object_type, :last_modified, :object_size)")
            result = connection.execute(stmt,
                                        object_key=object_key,
                                        object_type=object_type,
                                        last_modified=last_modified,
                                        object_size=object_size)
            return result.lastrowid

    def get_image(self, image_id: int) -> Optional[dict]:
        """Gets image by id from mysql db"""

        with self.__database.connect() as connection:
            stmt = text("SELECT * FROM images WHERE id = :id")
            result = connection.execute(stmt, id=image_id).fetchone()
            if result:
                image = dict(zip(result.keys(), result.values()))
                return image
        return None

    def delete_image(self, image_id: int):
        """Deletes image from mysql db"""

        with self.__database.connect() as connection:
            stmt = text("DELETE FROM images WHERE id = :id")
            connection.execute(stmt, id=image_id)

    def get_images(self) -> List[dict]:
        """Gets images from mysql db"""

        with self.__database.connect() as connection:
            stmt = text("SELECT * FROM images")
            results = connection.execute(stmt).fetchall()
            images = [dict(zip(result.keys(), result.values())) for result in results]
            return images
