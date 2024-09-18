import json
import logging
from typing import Any
from RSKafkaWrapper.client import KafkaClient
from app.shared import (
    messages_sensor_data_response,
    messages_get_all_sensor_data_response,
    messages_consumed_sensor_data_event
)
from app.api.utils import parse_and_flatten_messages
from app.mapper.sensor_data_mapper import SensorDataMapper


class SensorDataService:

    def __init__(self, client: KafkaClient):
        self.client = client

    def save_sensor_data(self, sensor_data_dto):
        try:
            logging.debug("Clearing previous messages and events.")
            messages_sensor_data_response.clear()
            messages_consumed_sensor_data_event.clear()

            sensor_data_mapper = SensorDataMapper(
                event_id=sensor_data_dto.event_id,
                data=sensor_data_dto.data.dict(),
                date_time=sensor_data_dto.date_time,
                bucket_id=sensor_data_dto.bucket_id,
                uuid=sensor_data_dto.uuid
            )
            logging.info(f"Sending message: {sensor_data_mapper.json()}")
            self.client.send_message("sensor_data", sensor_data_mapper.json())

            logging.info("Waiting for message consumption event to be set.")
            messages_consumed_sensor_data_event.wait(timeout=10)  # Add a timeout for safety
            logging.info("Event set, proceeding to parse messages.")

            response = parse_and_flatten_messages(messages_sensor_data_response)
            logging.info(f"Received data SAVE: {response}")
            return response

        except Exception as e:
            logging.error(f"An error occurred while saving sensor data: {e}")
            raise

    def get_all_sensor_data(self) -> list[Any]:
        try:
            logging.debug("Clearing previous messages and events.")
            messages_get_all_sensor_data_response.clear()
            messages_consumed_sensor_data_event.clear()

            to_send = {"event": "get_all"}
            logging.debug(f"Sending message: {to_send}")
            self.client.send_message("get_all_sensor_data", str(to_send))

            logging.debug("Waiting for message consumption event to be set.")
            messages_consumed_sensor_data_event.wait(timeout=10)  # Add a timeout for safety
            logging.debug("Event set, proceeding to parse messages.")

            response = parse_and_flatten_messages(messages_get_all_sensor_data_response)
            logging.info(f"Received data GET ALL: {response}")
            return response

        except Exception as e:
            logging.error(f"An error occurred while fetching all sensor data: {e}")
            raise

    def get_by_id_sensor_data(self, record_id: int):
        pass
