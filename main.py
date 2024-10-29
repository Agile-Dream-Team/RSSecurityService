import logging
import threading
from contextlib import asynccontextmanager

import uvicorn
from fastapi import FastAPI, status
from pydantic import BaseModel, ValidationError

from app.api.v1.auth_controller import auth_router
from app.config.config import Settings
from app.shared import (
    messages_consumed_user_event,
    messages_user_response,
    lock_user_response,
)
from RSKafkaWrapper.client import KafkaClient

base_path = '/auth'
version_1 = 'v1'


def configure_logging():
    logging.basicConfig(level=logging.INFO)


configure_logging()

app_settings = Settings()
app = FastAPI(docs_url=f'{base_path}/docs')

# Initialize KafkaClient using the singleton pattern
kafka_client = KafkaClient.instance(app_settings.kafka_bootstrap_servers, app_settings.kafka_group_id)


@asynccontextmanager
async def lifespan(fastapi_app: FastAPI):
    try:
        local_settings = Settings()
    except ValidationError as e:
        logging.error(f"Environment variable validation error: {e}")
        raise

    existing_topics = kafka_client.list_topics()
    logging.info(f"Creating Kafka topics: {local_settings.kafka_topics}")
    for topic in local_settings.kafka_topics:
        if topic not in existing_topics:
            kafka_client.create_topic(topic)
        else:
            logging.info(f"Topic '{topic}' already exists.")

    yield


app.router.lifespan_context = lifespan
app.include_router(auth_router)


class HealthCheck(BaseModel):
    webhook_status: str = "OK"
    kafka_status: str = "Not implemented"
    msg: str = "Hello world"


@app.get(base_path, response_model=HealthCheck, status_code=status.HTTP_200_OK)
async def get_health() -> HealthCheck:
    logging.info("Health check endpoint called")
    return HealthCheck()


@kafka_client.topic('user_response')
def consume_message_save_user(msg):
    try:
        with lock_user_response:
            messages_user_response.append(msg)
        logging.info(f"Consumed message in user_response: {msg}")
        messages_consumed_user_event.set()
        logging.info("Event set after consuming message.")
    except Exception as e:
        logging.error(f"Error processing message in user_response: {e}")


if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host=app_settings.webhook_host,
        port=app_settings.webhook_port,
        reload=app_settings.environment == 'dev'
    )
