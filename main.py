# main.py
import json
import logging

from confluent_kafka import Consumer, KafkaError, KafkaException
from fastapi import FastAPI, status, Depends
from pydantic import BaseModel, ValidationError
from contextlib import asynccontextmanager
import uvicorn

from app.api.v1.webhooks.webhook_routes import router as webhook_router
from app.config.config import Settings
from app.config.kafka_manager import KafkaManager
from app.services.kafka_consumer_service import KafkaConsumerService
from dependencies import startup_kafka_manager, has_access
from fastapi.middleware.cors import CORSMiddleware

origins = [
    "http://localhost",
    "http://localhost:10000",
]


def configure_logging():
    logging.basicConfig(level=logging.INFO)


def kafka_topic(topic_name):
    def decorator(func):
        def wrapper(*args, **kwargs):
            instance = args[0]
            instance.consumer.subscribe([topic_name])
            return func(*args, **kwargs)

        return wrapper

    return decorator


class KafkaConsumer:
    def __init__(self, settings: Settings):
        kafka_manager = KafkaManager(
            bootstrap_servers=settings.kafka_bootstrap_servers,
            topics=settings.kafka_topics,
            group_id=settings.kafka_group_id
        )
        self.consumer = Consumer({
            'bootstrap.servers': settings.kafka_bootstrap_servers,
            'group.id': settings.kafka_group_id,
            'auto.offset.reset': 'earliest'
        })
        self.consumer_service = KafkaConsumerService(kafka_manager)

    def consume_message(self, topic_name):
        while True:
            try:
                msg = self.consumer.poll(timeout=1.0)
                if msg is None:
                    continue
                if msg.error():
                    if msg.error().code() == KafkaError._PARTITION_EOF:
                        continue
                    else:
                        raise KafkaException(msg.error())
                logging.info(f"Consumed message from topic {msg.topic()}: {msg.value().decode('utf-8')}")

                # Parse the message into the appropriate DTO
                try:
                    message_data = json.loads(msg.value().decode('utf-8'))


                    # Process the message using KafkaConsumerService
                    self.consumer_service.process_message(message_data)
                except (json.JSONDecodeError, ValidationError) as e:
                    logging.error(f"Failed to parse message: {e}")
            except Exception as e:
                logging.error(f"Error in consume_message for topic {topic_name}: {e}")

    @kafka_topic('get_all_produce')
    def consume_get_all_messages(self):
        self.consume_message('get_all')

    @kafka_topic('create')
    def consume_create_messages(self):
        self.consume_message('create')


class MainApp:
    def __init__(self):
        self.app_settings = Settings()
        self.app = FastAPI(lifespan=self.lifespan)
        configure_logging()
        self.include_routes()

    @asynccontextmanager
    async def lifespan(self, fastapi_app: FastAPI):
        try:
            local_settings = Settings()
        except ValidationError as e:
            logging.error(f"Environment variable validation error: {e}")
            raise

        startup_kafka_manager(fastapi_app, local_settings)
        kafka_manager = fastapi_app.state.kafka_manager
        logging.info(f"Creating Kafka topics: {local_settings.kafka_topics}")
        kafka_manager.create_kafka_topics(local_settings.kafka_topics)
        kafka_consumer = KafkaConsumer(local_settings)
        kafka_consumer.consume_get_all_messages()
        yield
        # TODO: Add any cleanup code here if needed

    def include_routes(self):
        self.app.include_router(webhook_router, prefix="/api/v1")  #dependencies=[Depends(has_access)]

    def run(self):
        logging.info(
            f"Starting server at ://{self.app_settings.webhook_host}:{self.app_settings.webhook_port} "
            f"with reload={self.app_settings.environment == 'dev'}"
        )
        uvicorn.run(
            "main:app",
            host=self.app_settings.webhook_host,
            port=self.app_settings.webhook_port,
            reload=self.app_settings.environment == 'dev'
        )


class HealthCheck(BaseModel):
    webhook_status: str = "OK"
    kafka_status: str = "Not implemented"
    msg: str = "Hello world"


app_instance = MainApp()
app = app_instance.app
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/", response_model=HealthCheck, status_code=status.HTTP_200_OK)
async def get_health() -> HealthCheck:
    logging.info("Health check endpoint called")
    # TODO: Implement Kafka health check
    return HealthCheck()


if __name__ == "__main__":
    app_instance.run()
