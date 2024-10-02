import json
import time
from typing import Union, List, Dict, Any

from confluent_kafka import Consumer, Producer, KafkaException, KafkaError
from confluent_kafka.admin import AdminClient, NewTopic
import threading
import logging


class SingletonMeta(type):
    _instances = {}

    def __call__(cls, *args, **kwargs):
        if cls not in cls._instances:
            instance = super().__call__(*args, **kwargs)
            cls._instances[cls] = instance
        return cls._instances[cls]


def consume_loop(consumer, callback):
    try:
        while True:
            msg = consumer.poll(timeout=1.0)
            if msg is None:
                continue
            if msg.error():
                if msg.error().code() == KafkaError._PARTITION_EOF:
                    logging.info("End of partition reached.")
                    continue
                else:
                    raise KafkaException(msg.error())

            start_time = time.time()

            # Decode the message from bytes to string
            data = msg.value().decode('utf-8')
            logging.info(f"Consumed message: {data}")

            # Deserialize JSON string to dictionary
            try:
                json_data = json.loads(data)
            except json.JSONDecodeError as e:
                logging.error(f"JSON decoding error: {e}")
                continue  # Skip this message and continue with the next one

            # Pass the dictionary to the callback
            callback(json_data)

            end_time = time.time()
            duration = end_time - start_time
            logging.info(f"Processed message in {duration:.10f} seconds")
    except Exception as e:
        logging.error(f"Error in consume loop: {e}")
    finally:
        consumer.close()
        logging.info("Consumer closed for topic.")


class KafkaClient(metaclass=SingletonMeta):
    _instance = None

    def __init__(self, bootstrap_servers, group_id):
        self.bootstrap_servers = bootstrap_servers
        self.group_id = group_id
        self.producer = Producer({'bootstrap.servers': self.bootstrap_servers})
        self.admin_client = AdminClient({'bootstrap.servers': self.bootstrap_servers})
        self.consumers = {}
        self.threads = {}

    @classmethod
    def instance(cls, bootstrap_servers=None, group_id=None):
        """
        Access the singleton of KafkaClient.
        """
        if cls._instance is None:
            if bootstrap_servers is None or group_id is None:
                logging.error("bootstrap_servers and group_id must be provided for the first instantiation")
                raise ValueError("bootstrap_servers and group_id must be provided for the first instantiation")
            else:
                logging.info(
                    f"Creating new instance of KafkaClient with servers: {bootstrap_servers} and group_id: {group_id}")
                cls._instance = cls(bootstrap_servers, group_id)
        else:
            logging.info("Returning existing instance of KafkaClient")
        return cls._instance

    def get_config(self, group_id):
        return {
            'bootstrap.servers': self.bootstrap_servers,
            'group.id': group_id,
            'auto.offset.reset': 'earliest',
            'enable.auto.commit': True,
            'session.timeout.ms': 6000,
            'heartbeat.interval.ms': 2000
        }

    def topic(self, topic):
        def decorator(func):
            if topic not in self.consumers:
                consumer_config = self.get_config(self.group_id + "_" + topic)
                consumer = Consumer(consumer_config)
                consumer.subscribe([topic])
                self.consumers[topic] = consumer
                logging.info(f"Subscribed to topic: {topic}")

                thread = threading.Thread(target=consume_loop, args=(consumer, func), daemon=True)
                thread.start()
                self.threads[topic] = thread
            return func

        return decorator

    def send_message(self, topic: Union[str, List[str]], message: Dict[str, Any]) -> None:
        try:
            # Ensure message is a dictionary and serialize it to JSON
            if not isinstance(message, dict):
                raise ValueError("Message must be a dictionary")

            # Serialize the dictionary to a JSON string
            json_message = json.dumps(message)

            # Encode the JSON string to bytes
            encoded_message = json_message.encode('utf-8')

            # Check if topic is a string (single topic) or a list (multiple topics)
            if isinstance(topic, str):
                self.producer.produce(topic, encoded_message)
                logging.info(f"Message sent to topic {topic}: {json_message}")
            elif isinstance(topic, list):
                for t in topic:
                    self.producer.produce(t, encoded_message)
                    logging.info(f"Message sent to topic {t}: {json_message}")
            else:
                raise ValueError("Topic must be a string or a list of strings")

            self.producer.flush()
        except (KafkaException, ValueError) as e:
            logging.error(f"Failed to send message: {e}")

    def list_topics(self):
        try:
            metadata = self.admin_client.list_topics(timeout=5)
            return metadata.topics.keys()
        except Exception as e:
            logging.error(f"Failed to list topics: {e}")
            return []

    def create_topic(self, topic_name, num_partitions=1, replication_factor=1):
        new_topic = NewTopic(topic_name, num_partitions=num_partitions, replication_factor=replication_factor)
        logging.info(f"Creating topic: {new_topic}")
        result = self.admin_client.create_topics([new_topic])
        for topic, future in result.items():
            try:
                future.result()
                logging.info(f"Topic {topic} created successfully")
            except Exception as e:
                logging.error(f"Failed to create topic {topic}: {e}")
