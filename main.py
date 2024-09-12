import logging
from contextlib import asynccontextmanager

import uvicorn
from fastapi import FastAPI, status
from pydantic import BaseModel, ValidationError

from app.api.v1.sensor_data.sensor_data_controller import sensor_data_router as sensor_data_router
from app.api.v1.image.image_controller import image_router as image_router
from app.config.config import Settings
from app.shared import messages_get_all_response, messages_consumed_event, messages_save_response
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
app.include_router(sensor_data_router, prefix="/api/v1/sensor_data", tags=["sensor_data"])
app.include_router(image_router, prefix="/api/v1/image", tags=["image"])


class HealthCheck(BaseModel):
    webhook_status: str = "OK"
    kafka_status: str = "Not implemented"
    msg: str = "Hello world"


@app.get("/", response_model=HealthCheck, status_code=status.HTTP_200_OK)
async def get_health() -> HealthCheck:
    logging.info("Health check endpoint called")
    return HealthCheck()


@kafka_client.topic('get_all_response')
def consume_message_prod(msg):
    try:
        data = msg.value().decode('utf-8')
        messages_get_all_response.append(data)
        logging.info(f"Consumed message in get_all_response: {data}")
        messages_consumed_event.set()
    except Exception as e:
        logging.error(f"Error processing message in get_all_response: {e}")


@kafka_client.topic('save_response')
def consume_message_get_all(msg):
    try:
        data = msg.value().decode('utf-8')
        messages_save_response.append(data)
        logging.info(f"Consumed message in save_response: {data}")
        messages_consumed_event.set()
    except Exception as e:
        logging.error(f"Error processing message in save_response: {e}")


if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host=app_settings.webhook_host,
        port=app_settings.webhook_port,
        reload=app_settings.environment == 'dev'
    )
