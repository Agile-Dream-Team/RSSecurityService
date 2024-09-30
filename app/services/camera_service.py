import json
import logging
import threading
import time
from typing import Any

from RSKafkaWrapper.client import KafkaClient
from app.shared import (
    messages_camera_response,
    messages_get_all_camera_response,
    messages_consumed_camera_event,
    messages_consumed_get_by_id_camera_event,
    messages_get_by_id_camera_response,
    lock_camera_response,
    lock_get_all_camera_response,
    lock_get_by_id_camera_response
)
from app.api.utils import parse_and_flatten_messages
from app.mapper.camera_mapper import CameraMapper


class CameraService:

    def __init__(self, client: KafkaClient):
        self.client = client

    def save_camera(self, camera_dto):
        try:
            #with lock_camera_response:
            messages_camera_response.clear()
            #messages_consumed_camera_event.clear()  # Clear the event before waiting

            camera_mapper = CameraMapper(
                image_b64=camera_dto.image_b64,
                sensor_data_id=camera_dto.sensor_data_id
            )
            self.client.send_message("camera", camera_mapper.model_dump())
            time.sleep(5)
            #logging.info("Waiting for message consumption event to be set.")
            #messages_consumed_camera_event.wait(timeout=10)
            #messages_consumed_camera_event.wait()
            #logging.info("Event set, proceeding to parse messages.")
            #with lock_camera_response:
            response = parse_and_flatten_messages(messages_camera_response)
            logging.info(f"Received data camera: {response}")
            return response

        except Exception as e:
            logging.error(f"An error occurred while saving camera: {e}")
            raise

    def get_all_camera(self):
        try:
            #with lock_get_all_camera_response:
            messages_get_all_camera_response.clear()
            #messages_consumed_camera_event.clear()  # Clear the event before waiting
            to_send = {
                "event": "get_all"
            }
            self.client.send_message("get_all_camera", to_send)
            time.sleep(1)
            logging.info("Waiting for message consumption event to be set.")
            #messages_consumed_camera_event.wait(timeout=10)
            logging.info("Event set, proceeding to parse messages.")
            #with lock_get_all_camera_response:
            response = parse_and_flatten_messages(messages_get_all_camera_response)
            logging.info(f"Received data camera: {response}")
            return response

        except Exception as e:
            logging.error(f"An error occurred while fetching all camera: {e}")
            raise

    def get_by_id_camera(self, record_id: int):
        try:
            #with lock_get_by_id_camera_response:
            messages_get_by_id_camera_response.clear()
            #messages_consumed_get_by_id_camera_event.clear()  # Clear the event before waiting
            to_send = {
                "event": "get_by_id",
                "id": record_id
            }
            self.client.send_message("get_by_id_camera", to_send)
            time.sleep(0.5)
            logging.info("Waiting for message consumption event to be set.")
            #messages_consumed_get_by_id_camera_event.wait(timeout=10)
            logging.info("Event set, proceeding to parse messages.")

            logging.info(f"Messages before parsing: {messages_get_by_id_camera_response}")

            #with lock_get_by_id_camera_response:
            response = parse_and_flatten_messages(messages_get_by_id_camera_response)
            logging.info(f"Received data camera: {response}")
            return response
        except Exception as e:
            logging.error(f"Error in get_by_id_camera: {e}")
            return None
