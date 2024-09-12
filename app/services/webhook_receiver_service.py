import json
import logging
from typing import List, Dict, Any

from app.dto.webhook_in_dto import SaveDTO
from app.services.kafka_producer_service import KafkaProducerService
from kafka_rs.client import KafkaClient
from app.shared import messages_save_response, messages_get_all_response, messages_consumed_event
from app.api.v1.utils import parse_and_flatten_messages


class WebhookReceiverService:

    def __init__(self, client: KafkaClient):
        self.client = client
        self.kafka_producer_service = KafkaProducerService(client)

    def receive_webhook(self, webhook_data: SaveDTO):
        messages_save_response.clear()
        messages_consumed_event.clear()  # Clear the event before waiting
        self.kafka_producer_service.process_webhook_to_kafka(webhook_data)
        messages_consumed_event.wait()
        response = parse_and_flatten_messages(messages_save_response)
        logging.info(f"Received data SAVE: {response}")
        return response

    def get_all(self) -> list[Any]:
        messages_get_all_response.clear()
        messages_consumed_event.clear()  # Clear the event before waiting
        self.kafka_producer_service.get_all()
        messages_consumed_event.wait()
        response = parse_and_flatten_messages(messages_get_all_response)
        logging.info(f"Received data GET ALL: {response}")
        return response
