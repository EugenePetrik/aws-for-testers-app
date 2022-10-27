from ensurepip import version
from constructs import Construct
from cdk.construct.network import Network
from cdk.construct.app_instance import AppInstance
from cdk.construct.mysql_database import MySQLDatabase
from cdk.construct.queue import Queue
from cdk.construct.topic import Topic
from cdk.construct.image_store import ImageStore
from cdk.stack import CloudXStack


class CloudXImageStack(CloudXStack):

    def __init__(self, scope: Construct, construct_id: str, key: str, application: str,
                 **kwargs) -> None:
        super().__init__(scope, construct_id, versions=[1, 2, 3, 4], **kwargs)

        self._setup_constructs(application, key)
        self._setup_grants(self.instance.role)

    def _setup_constructs(self, application: str, key: str):
        self.network = Network(self, 'Network', max_azs=2)
        self.queue = Queue(self, 'Queue')
        self.topic = Topic(self, 'Topic')
        self.image_store = ImageStore(self, 'ImageStore', version=self.version)

        self.database = MySQLDatabase(
            self, 'Database', vpc=self.network.vpc,
            subnets=self.network.private_subnet,
            version=self.version)

        env = {
            'S3_BUCKET': self.image_store.bucket.bucket_name,
            'QUEUE_URL': self.queue.url,
            'TOPIC_ARN': self.topic.arn,
            'DB_NAME': self.database.database_name,
            'DB_HOST': self.database.host,
            'DB_PORT': self.database.port,
            'DB_USERNAME': self.database.username,
            'DB_PASSWORD_SECRET_NAME': self.database.secret_name,
        }

        self.instance = AppInstance(self, 'AppInstance',
                                    application, key,
                                    vpc=self.network.vpc,
                                    subnet=self.network.public_subnet,
                                    env=env,
                                    version=self.version)

    def _setup_grants(self, role):
        role.add_managed_policy(self.image_store.policy)
        role.add_managed_policy(self.database.policy)
        role.add_managed_policy(self.topic.subscription_policy)
        role.add_managed_policy(self.topic.publish_policy)
        self.database.allow_instance(self.instance.instance)
        self.queue.grant_send_messages(role)
        self.queue.grant_consume_messages(role)
