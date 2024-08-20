from confluent_kafka import Producer, Consumer, KafkaException, KafkaError
from confluent_kafka.admin import AdminClient, NewTopic
import logging


class KafkaManager:
    _instance = None

    def __new__(cls, *args, **kwargs):
        if not cls._instance:
            cls._instance = super(KafkaManager, cls).__new__(cls)
            cls._instance.__init__(*args, **kwargs)
        return cls._instance

    def __init__(self, bootstrap_servers: str, topics: list[str], group_id: str):
        if not hasattr(self, 'initialized'):  # Ensure initialization happens only once
            self.bootstrap_servers = bootstrap_servers
            self.topics = topics
            self.group_id = group_id
            self.producer = self.create_producer()
            self.consumer = self.create_consumer()
            self.initialized = True

    def create_producer(self):
        return Producer({
            'bootstrap.servers': self.bootstrap_servers,
            'socket.timeout.ms': 10000,  # 10 seconds timeout
            'message.timeout.ms': 10000  # 10 seconds timeout
        })

    def create_consumer(self):
        return Consumer({
            'bootstrap.servers': self.bootstrap_servers,
            'group.id': self.group_id,
            'auto.offset.reset': 'earliest',
            'session.timeout.ms': 10000,  # 10 seconds timeout
            'socket.timeout.ms': 10000  # 10 seconds timeout
        })

    def create_kafka_topics(self, topics):
        admin_client = AdminClient({'bootstrap.servers': self.bootstrap_servers})
        topic_list = [NewTopic(topic, num_partitions=1, replication_factor=1) for topic in topics]
        logging.info(f"Creating topics: {topic_list}")
        result = admin_client.create_topics(new_topics=topic_list)
        for topic, future in result.items():
            try:
                future.result()
                logging.info(f"Topic {topic} created successfully")
            except Exception as e:
                logging.error(f"Failed to create topic {topic}: {e}")

    def send_health_check_ping(self):
        try:
            for topic in self.topics:
                self.producer.produce(topic, key="ping", value="ping")
            self.producer.flush()
            logging.info("Health check ping sent")
        except KafkaException as e:
            logging.error(f"Failed to send health check ping: {e}")
