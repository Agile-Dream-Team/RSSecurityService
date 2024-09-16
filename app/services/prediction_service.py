import json
import logging
from typing import Any

from kafka_rs.client import KafkaClient
from app.shared import messages_prediction_response, messages_consumed_prediction_event
from app.api.utils import parse_and_flatten_messages


class PredictionService:

    def __init__(self, client: KafkaClient):
        self.client = client

    def get_prediction(self, camera_id) -> list[Any]:
        try:
            messages_prediction_response.clear()
            messages_consumed_prediction_event.clear()  # Clear the event before waiting
            to_send = {
                "camera_id": f'{camera_id}'
            }
            self.client.send_message("prediction_request", str(to_send))

            messages_consumed_prediction_event.wait()
            response = parse_and_flatten_messages(messages_prediction_response)
            logging.info(f"Received data prediction_request: {response}")
            return response

        except Exception as e:
            logging.error(f"An error occurred while fetching prediction_request: {e}")
            raise

