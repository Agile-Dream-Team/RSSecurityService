import json
import logging
from typing import Any

from RSKafkaWrapper.client import KafkaClient
from app.shared import (
    messages_camera_response,
    messages_get_all_camera_response,
    messages_consumed_camera_event)
from app.api.utils import parse_and_flatten_messages
from app.mapper.camera_mapper import CameraMapper


class CameraService:

    def __init__(self, client: KafkaClient):
        self.client = client

    def save_camera(self, camera_dto):
        try:
            messages_camera_response.clear()
            messages_consumed_camera_event.clear()  # Clear the event before waiting

            camera_mapper = CameraMapper(
                image_b64=camera_dto.image_b64,
                sensor_data_id=camera_dto.sensor_data_id
            )
            self.client.send_message("camera", camera_mapper.model_dump_json())
            logging.info("Waiting for message consumption event to be set.")
            messages_consumed_camera_event.wait(timeout=10)
            logging.info("Event set, proceeding to parse messages.")
            response = parse_and_flatten_messages(messages_camera_response)
            logging.info(f"Received data camera: {response}")
            return response

        except Exception as e:
            logging.error(f"An error occurred while saving camera: {e}")
            raise

    def get_all_camera(self) -> list[Any]:
        try:
            messages_get_all_camera_response.clear()
            messages_consumed_camera_event.clear()  # Clear the event before waiting
            to_send = {
                "event": "get_all"
            }
            self.client.send_message("get_all_camera", str(to_send))
            logging.debug("Waiting for message consumption event to be set.")
            messages_consumed_camera_event.wait(timeout=10)
            logging.debug("Event set, proceeding to parse messages.")
            response = parse_and_flatten_messages(messages_get_all_camera_response)
            logging.info(f"Received data camera: {response}")
            return response

        except Exception as e:
            logging.error(f"An error occurred while fetching all camera: {e}")
            raise

    def get_by_id_camera(self, record_id: int):
        pass
