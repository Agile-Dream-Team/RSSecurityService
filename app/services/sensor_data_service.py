import json
import logging
import threading
from typing import Any
from RSKafkaWrapper.client import KafkaClient
from app.shared import (
    messages_sensor_data_response,
    messages_get_all_sensor_data_response,
    messages_consumed_sensor_data_event,
    lock_sensor_data_response,
    lock_get_all_sensor_data_response, lock_get_by_id_sensor_data_response, messages_get_by_id_sensor_data_response,
    messages_consumed_get_by_id_sensor_data_event
)
from app.api.utils import parse_and_flatten_messages
from app.mapper.sensor_data_mapper import SensorDataMapper


class SensorDataService:

    def __init__(self, client: KafkaClient):
        self.client = client

    def save_sensor_data(self, sensor_data_dto):
        try:
            logging.debug("Clearing previous messages and events.")
            with lock_sensor_data_response:
                messages_sensor_data_response.clear()
            messages_consumed_sensor_data_event.clear()

            sensor_data_mapper = SensorDataMapper(
                event_id=sensor_data_dto.event_id,
                data=sensor_data_dto.data.dict(),
                date_time=sensor_data_dto.date_time,
                bucket_id=sensor_data_dto.bucket_id,
                uuid=sensor_data_dto.uuid
            )
            logging.info(f"Sending message: {sensor_data_mapper.model_dump()}")
            self.client.send_message("sensor_data", sensor_data_mapper.model_dump())

            logging.info("Waiting for message consumption event to be set.")
            messages_consumed_sensor_data_event.wait(timeout=10)  # Add a timeout for safety
            logging.info("Event set, proceeding to parse messages.")

            with lock_sensor_data_response:
                response = parse_and_flatten_messages(messages_sensor_data_response)
            logging.info(f"Received data SAVE: {response}")
            return response

        except Exception as e:
            logging.error(f"An error occurred while saving sensor data: {e}")
            raise

    def get_all_sensor_data(self):
        try:
            logging.info("Clearing previous messages and events.")
            with lock_get_all_sensor_data_response:
                messages_get_all_sensor_data_response.clear()
            messages_consumed_sensor_data_event.clear()

            to_send = {"event": "get_all"}
            logging.info(f"Sending message: {to_send}")
            self.client.send_message("get_all_sensor_data", to_send)

            logging.info("Waiting for message consumption event to be set.")
            messages_consumed_sensor_data_event.wait(timeout=10)  # Add a timeout for safety
            logging.info("Event set, proceeding to parse messages.")

            with lock_get_all_sensor_data_response:
                response = parse_and_flatten_messages(messages_get_all_sensor_data_response)
            logging.info(f"Received data GET ALL: {response}")
            return response

        except Exception as e:
            logging.error(f"An error occurred while fetching all sensor data: {e}")
            raise

    def get_by_id_sensor_data(self, record_id: int):
        try:
            with lock_get_by_id_sensor_data_response:
                messages_get_by_id_sensor_data_response.clear()
            messages_consumed_get_by_id_sensor_data_event.clear()  # Clear the event before waiting
            to_send = {
                "event": "get_by_id",
                "id": record_id
            }
            self.client.send_message("get_by_id_sensor_data", to_send)
            logging.info("Waiting for message consumption event to be set.")
            messages_consumed_get_by_id_sensor_data_event.wait(timeout=10)
            logging.info("Event set, proceeding to parse messages.")

            logging.info(f"Messages before parsing: {messages_get_by_id_sensor_data_response}")

            with lock_get_by_id_sensor_data_response:
                response = parse_and_flatten_messages(messages_get_by_id_sensor_data_response)
            logging.info(f"Received data sensor_data: {response}")
            return response
        except Exception as e:
            logging.error(f"Error in get_by_id_sensor_data: {e}")
            return None
