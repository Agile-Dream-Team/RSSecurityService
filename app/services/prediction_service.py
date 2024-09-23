import json
import logging
from typing import Any

from RSKafkaWrapper.client import KafkaClient
from app.shared import messages_prediction_response, messages_consumed_prediction_event, lock_prediction_response
from app.api.utils import parse_and_flatten_messages


class PredictionService:

    def __init__(self, client: KafkaClient):
        self.client = client


    def get_prediction(self, camera_id: int):
        try:
            with lock_prediction_response:
                messages_prediction_response.clear()
            messages_consumed_prediction_event.clear()  # Clear the event before waiting
            to_send = {
                "id": camera_id
            }
            self.client.send_message("prediction_request", to_send)
            logging.info("Waiting for message consumption event to be set.")
            messages_consumed_prediction_event.wait(timeout=10)
            logging.info("Event set, proceeding to parse messages.")

            logging.info(f"Messages before parsing: {messages_prediction_response}")

            with lock_prediction_response:
                response = parse_and_flatten_messages(messages_prediction_response)
            logging.info(f"Received data prediction: {response}")
            return response
        except Exception as e:
            logging.error(f"Error in prediction: {e}")
            return None

