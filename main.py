import logging
from contextlib import asynccontextmanager

import uvicorn
from fastapi import FastAPI, status
from pydantic import BaseModel, ValidationError

from app.api.v1.webhooks.webhook_routes import router as webhook_router
from app.config.config import Settings
from app.shared import messages_get_all_produce, messages_consumed_event
from kafka_rs.client import KafkaClient


def configure_logging():
    logging.basicConfig(level=logging.INFO)


configure_logging()

app_settings = Settings()
app = FastAPI()

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
app.include_router(webhook_router, prefix="/api/v1")


class HealthCheck(BaseModel):
    webhook_status: str = "OK"
    kafka_status: str = "Not implemented"
    msg: str = "Hello world"


@app.get("/", response_model=HealthCheck, status_code=status.HTTP_200_OK)
async def get_health() -> HealthCheck:
    logging.info("Health check endpoint called")
    return HealthCheck()


@kafka_client.topic('get_all_produce')
def consume_message_prod(msg):
    try:
        data = msg.value().decode('utf-8')
        messages_get_all_produce.append(data)
        logging.info(f"Consumed message in get_all_produce: {data}")
        messages_consumed_event.set()
    except Exception as e:
        logging.error(f"Error processing message in get_all_produce: {e}")

"""
@kafka_client.topic('get_all')
def consume_message_get_all(msg):
    try:
        data = msg.value().decode('utf-8')
        logging.info(f"Consumed message in get_all: {data}")
    except Exception as e:
        logging.error(f"Error processing message in get_all: {e}")
"""

if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host=app_settings.webhook_host,
        port=app_settings.webhook_port,
        reload=app_settings.environment == 'dev'
    )
