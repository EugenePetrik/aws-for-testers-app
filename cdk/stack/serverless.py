from constructs import Construct
from cdk.construct.network import Network
from cdk.construct.app_instance import AppInstance
from cdk.construct.nosql_database import NoSQLDatabase
from cdk.construct.queue import Queue
from cdk.construct.topic import Topic
from cdk.construct.image_store import ImageStore
from cdk.construct.event_handler import EventHandler
from cdk.construct.trail import Trail
from cdk.stack import CloudXStack


class CloudXServerlessStack(CloudXStack):

    def __init__(self, scope: Construct, construct_id: str, key: str, application: str,
                 **kwargs) -> None:
        super().__init__(scope, construct_id,  versions=[1, 2], **kwargs)

        self._setup_constructs()
        self._setup_instance(application, key)
        self._setup_lambda()
        self._setup_grants()

    def _setup_constructs(self):
        self.network = Network(self, 'Network', max_azs=2)
        self.queue = Queue(self, 'Queue')
        self.topic = Topic(self, 'Topic')
        self.image_store = ImageStore(self, 'ImageStore')
        self.database = NoSQLDatabase(self, 'Database')
        self.trail = Trail(self, 'Trail')

    def _setup_instance(self, application: str, key: str):
        env = {
            'S3_BUCKET': self.image_store.bucket.bucket_name,
            'QUEUE_URL': self.queue.url,
            'TOPIC_ARN': self.topic.arn,
            'TABLE_NAME': self.database.table_name,
        }

        self.instance = AppInstance(self, 'AppInstance',
                                    application, key,
                                    vpc=self.network.vpc,
                                    subnet=self.network.public_subnet,
                                    env=env,
                                    log_enabled=True)

    def _setup_lambda(self):
        env = {
            'TOPIC_ARN': self.topic.arn,
        }

        self.event_handler = EventHandler(self, 'EventHandler',
                                          vpc=self.network.vpc,
                                          subnet=self.network.private_subnet,
                                          env=env,
                                          version=self.version
                                          )
        self.event_handler.setup_sqs_trigger(self.queue.sqs_queue)

    def _setup_grants(self):
        self.instance.role.add_managed_policy(self.image_store.policy)
        self.instance.role.add_managed_policy(self.topic.subscription_policy)
        self.event_handler.role.add_managed_policy(self.topic.publish_policy)
        self.database.allow_instance(self.instance.instance)
        self.queue.grant_send_messages(self.instance.role)
        self.queue.grant_consume_messages(self.event_handler.role)
