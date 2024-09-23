import logging
import threading
from contextlib import asynccontextmanager

import uvicorn
from fastapi import FastAPI, status
from pydantic import BaseModel, ValidationError

from app.api.v1.prediction_controller import prediction_router
from app.api.v1.sensor_data_controller import sensor_data_router as sensor_data_router
from app.api.v1.camera_controller import camera_router as camera_router
from app.config.config import Settings
from app.shared import (
    messages_get_all_sensor_data_response,
    messages_consumed_sensor_data_event,
    messages_consumed_camera_event,
    messages_sensor_data_response,
    messages_camera_response,
    messages_get_by_id_sensor_data_response,
    messages_get_all_camera_response,
    messages_get_by_id_camera_response,
    messages_prediction_response,
    messages_consumed_prediction_event,
    messages_consumed_get_by_id_camera_event,
    messages_consumed_get_all_camera_event,
    messages_consumed_get_by_id_sensor_data_event,
    messages_consumed_get_all_sensor_data_event,
    lock_sensor_data_response,
    lock_get_all_sensor_data_response,
    lock_get_by_id_sensor_data_response,
    lock_camera_response,
    lock_get_all_camera_response,
    lock_get_by_id_camera_response,
    lock_prediction_response
)
from RSKafkaWrapper.client import KafkaClient


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
app.include_router(camera_router, prefix="/api/v1/camera", tags=["camera"])
app.include_router(prediction_router, prefix="/api/v1/prediction", tags=["prediction"])


class HealthCheck(BaseModel):
    webhook_status: str = "OK"
    kafka_status: str = "Not implemented"
    msg: str = "Hello world"


@app.get("/", response_model=HealthCheck, status_code=status.HTTP_200_OK)
async def get_health() -> HealthCheck:
    logging.info("Health check endpoint called")
    return HealthCheck()


@kafka_client.topic('sensor_data_response')
def consume_message_save_sensor_data(msg):
    try:
        with lock_sensor_data_response:
            messages_sensor_data_response.append(msg)
        logging.info(f"Consumed message in sensor_data_response: {msg}")
        messages_consumed_sensor_data_event.set()
        logging.info("Event set after consuming message.")
    except Exception as e:
        logging.error(f"Error processing message in sensor_data_response: {e}")


@kafka_client.topic('get_all_sensor_data_response')
def consume_message_get_all_sensor_data(msg):
    try:
        with lock_get_all_sensor_data_response:
            messages_get_all_sensor_data_response.append(msg)
        logging.info(f"Consumed message in get_all_sensor_data_response: {msg}")
        messages_consumed_get_all_sensor_data_event.set()
        logging.info("Event set after consuming message.")
    except Exception as e:
        logging.error(f"Error processing message in get_all_sensor_data_response: {e}")


@kafka_client.topic('get_by_id_sensor_data_response')
def consume_message_get_by_id_sensor_data(msg):
    try:
        with lock_get_by_id_sensor_data_response:
            messages_get_by_id_sensor_data_response.append(msg)
        logging.info(f"Consumed message in get_by_id_response: {msg}")
        messages_consumed_get_by_id_sensor_data_event.set()
    except Exception as e:
        logging.error(f"Error processing message in get_by_id_response: {e}")


@kafka_client.topic('camera_response')
def consume_message_camera(msg):
    try:
        with lock_camera_response:
            messages_camera_response.append(msg)
        logging.info(f"Consumed message in camera_response: {msg}")
        messages_consumed_camera_event.set()
    except Exception as e:
        logging.error(f"Error processing message in camera_response: {e}")


@kafka_client.topic('get_all_camera_response')
def consume_message_get_all_camera(msg):
    try:
        with lock_get_all_camera_response:
            messages_get_all_camera_response.append(msg)
        logging.info(f"Consumed message in get_all_camera_response: {msg}")
        messages_consumed_get_all_camera_event.set()
    except Exception as e:
        logging.error(f"Error processing message in get_all_camera_response: {e}")


@kafka_client.topic('get_by_id_camera_response')
def consume_message_get_by_id_camera(msg):
    try:
        logging.info(f"Received message in get_by_id_camera_response: {msg}")
        with lock_get_by_id_camera_response:
            messages_get_by_id_camera_response.append(msg)
        logging.info(f"Appended message to messages_get_by_id_camera_response: {messages_get_by_id_camera_response}")
        messages_consumed_get_by_id_camera_event.set()
        logging.info("Event set for get_by_id_camera_response")
    except Exception as e:
        logging.error(f"Error processing message in get_by_id_camera_response: {e}")


@kafka_client.topic('prediction_response')
def consume_message_prediction(msg):
    try:
        with lock_prediction_response:
            messages_prediction_response.append(msg)
        logging.info(f"Consumed message in prediction_response: {msg}")
        messages_consumed_prediction_event.set()
    except Exception as e:
        logging.error(f"Error processing message in prediction_response: {e}")


if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host=app_settings.webhook_host,
        port=app_settings.webhook_port,
        reload=app_settings.environment == 'dev'
    )
